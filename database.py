# database.py
import sqlite3
import json
from pathlib import Path
from models import CREATE_SCHEMA

class BancoDadosHeuristica:
    def __init__(self, db_path="heuristica_ifsp.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        self.criar_schema()
        self.migrate_schema()   # Adiciona novas colunas se necessário
        self.carregar_dados_iniciais()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fechar()

    def criar_schema(self):
        cursor = self.conn.cursor()
        cursor.executescript(CREATE_SCHEMA)
        self.conn.commit()

    def migrate_schema(self):
        """Adiciona colunas novas que possam ter sido introduzidas em versões posteriores."""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(teoremas)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]
        novas_colunas = {
            'pre_requisitos': 'TEXT',
            'tecnicas_resolucao': 'TEXT',
            'intuicao': 'TEXT',
            'analogias': 'TEXT',
            'curiosidades': 'TEXT'
        }
        for col, tipo in novas_colunas.items():
            if col not in colunas_existentes:
                cursor.execute(f"ALTER TABLE teoremas ADD COLUMN {col} {tipo}")
        self.conn.commit()

    def carregar_dados_iniciais(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM teoremas")
        if cursor.fetchone()[0] > 0:
            print("ℹ️ Banco de dados já populado.")
            return

        print("🔄 Carregando teoremas do arquivo JSON...")
        json_path = Path(__file__).parent / "teoremas.json"
        if not json_path.exists():
            print("❌ Arquivo teoremas.json não encontrado.")
            return

        with open(json_path, "r", encoding="utf-8") as f:
            teoremas_data = json.load(f)

        all_disciplinas = set()
        all_tags = set()

        for codigo, info in teoremas_data.items():
            for disc in info['disciplinas']:
                all_disciplinas.add((disc, info['curso']))
            for cat, tags_list in info['tags'].items():
                for tag in tags_list:
                    all_tags.add((tag, cat))

        # Inserir Disciplinas
        for nome, curso in all_disciplinas:
            cursor.execute(
                "INSERT OR IGNORE INTO disciplinas (nome, curso) VALUES (?, ?)",
                (nome, curso)
            )

        # Inserir Tags
        for nome, cat in all_tags:
            cursor.execute(
                "INSERT OR IGNORE INTO tags (nome, categoria) VALUES (?, ?)",
                (nome, cat)
            )

        self.conn.commit()

        # Inserir Teoremas e relacionamentos
        for codigo, info in teoremas_data.items():
            # Extrair campos opcionais com get
            pre_req = info.get('pre_requisitos')
            if isinstance(pre_req, list):
                pre_req = ', '.join(pre_req)
            tecnicas = info.get('tecnicas_resolucao')
            if isinstance(tecnicas, list):
                tecnicas = ', '.join(tecnicas)

            cursor.execute("""
                INSERT INTO teoremas (
                    codigo, nome, curso, formulacao, contexto_historico,
                    estrategia_principal, padrao_raciocinio, aplicacao_curso,
                    pre_requisitos, tecnicas_resolucao, intuicao, analogias, curiosidades
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                codigo,
                info['nome'],
                info['curso'],
                info['formulação'],
                info['contexto_historico'],
                info['estrategia_principal'],
                info['padrao_raciocinio'],
                info['aplicacao_curso'],
                pre_req,
                tecnicas,
                info.get('intuicao'),
                info.get('analogias'),
                info.get('curiosidades')
            ))
            teorema_id = cursor.lastrowid

            # Disciplinas
            for disc in info['disciplinas']:
                cursor.execute("SELECT id FROM disciplinas WHERE nome = ?", (disc,))
                disc_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT OR IGNORE INTO teorema_disciplinas (teorema_id, disciplina_id) VALUES (?, ?)",
                    (teorema_id, disc_id)
                )

            # Tags
            for cat, tags_list in info['tags'].items():
                for tag in tags_list:
                    cursor.execute("SELECT id FROM tags WHERE nome = ?", (tag,))
                    tag_id = cursor.fetchone()[0]
                    cursor.execute(
                        "INSERT OR IGNORE INTO teorema_tags (teorema_id, tag_id) VALUES (?, ?)",
                        (teorema_id, tag_id)
                    )

            # Exercícios
            for ex in info.get('exercicios', []):
                cursor.execute(
                    "INSERT INTO exercicios (teorema_id, nivel, enunciado) VALUES (?, ?, ?)",
                    (teorema_id, ex['nivel'], ex['enunciado'])
                )

            # Leituras
            for ref in info.get('leituras', []):
                cursor.execute(
                    "INSERT INTO leituras (teorema_id, referencia) VALUES (?, ?)",
                    (teorema_id, ref)
                )

        self.conn.commit()
        print(f"✅ {len(teoremas_data)} teoremas carregados com sucesso!")

    def buscar_teorema_por_codigo(self, codigo):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.*,
                   GROUP_CONCAT(DISTINCT d.nome) as disciplinas,
                   GROUP_CONCAT(DISTINCT tg.nome) as tags
            FROM teoremas t
            LEFT JOIN teorema_disciplinas td ON t.id = td.teorema_id
            LEFT JOIN disciplinas d ON td.disciplina_id = d.id
            LEFT JOIN teorema_tags tt ON t.id = tt.teorema_id
            LEFT JOIN tags tg ON tt.tag_id = tg.id
            WHERE t.codigo = ?
            GROUP BY t.id
        """, (codigo,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def buscar_por_id(self, teorema_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.*,
                   GROUP_CONCAT(DISTINCT d.nome) as disciplinas,
                   GROUP_CONCAT(DISTINCT tg.nome) as tags
            FROM teoremas t
            LEFT JOIN teorema_disciplinas td ON t.id = td.teorema_id
            LEFT JOIN disciplinas d ON td.disciplina_id = d.id
            LEFT JOIN teorema_tags tt ON t.id = tt.teorema_id
            LEFT JOIN tags tg ON tt.tag_id = tg.id
            WHERE t.id = ?
            GROUP BY t.id
        """, (teorema_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def buscar_por_filtros(self, curso=None, tags=None, estrategias=None, texto=None):
        """
        Filtros:
        - curso: string exata
        - tags: lista de nomes de tags (interseção)
        - estrategias: lista de substrings para estrategia_principal (OR)
        - texto: busca em nome, codigo, formulacao
        """
        query = """
            SELECT DISTINCT t.* FROM teoremas t
            LEFT JOIN teorema_tags tt ON t.id = tt.teorema_id
            LEFT JOIN tags tg ON tt.tag_id = tg.id
            WHERE 1=1
        """
        params = []

        if curso:
            query += " AND t.curso = ?"
            params.append(curso)

        if tags:
            # Para múltiplas tags, exigimos que o teorema tenha TODAS as tags (interseção)
            # Usaremos HAVING COUNT(DISTINCT tg.nome) = ?
            # Isso requer GROUP BY e HAVING, então vamos construir uma subconsulta
            tag_placeholders = ','.join(['?'] * len(tags))
            query = f"""
                SELECT DISTINCT t.* FROM teoremas t
                WHERE t.id IN (
                    SELECT tt.teorema_id
                    FROM teorema_tags tt
                    JOIN tags tg ON tt.tag_id = tg.id
                    WHERE tg.nome IN ({tag_placeholders})
                    GROUP BY tt.teorema_id
                    HAVING COUNT(DISTINCT tg.nome) = ?
                )
            """
            params.extend(tags)
            params.append(len(tags))
            # Aplicar outros filtros depois (curso, texto, etc.)
            # Vamos reconstruir a query principal com os filtros adicionais
            base_query = query
            query = f"""
                SELECT t.* FROM teoremas t
                WHERE t.id IN ({base_query})
            """
            # Agora adicionar curso e texto
            if curso:
                query += " AND t.curso = ?"
                params.append(curso)
            if texto:
                query += " AND (t.nome LIKE ? OR t.codigo LIKE ? OR t.formulacao LIKE ?)"
                like = f"%{texto}%"
                params.extend([like, like, like])
            if estrategias:
                or_clauses = []
                for _ in estrategias:
                    or_clauses.append("t.estrategia_principal LIKE ?")
                query += " AND (" + " OR ".join(or_clauses) + ")"
                for est in estrategias:
                    params.append(f"%{est}%")
        else:
            # Sem tags, podemos usar a construção simples
            if curso:
                query += " AND t.curso = ?"
                params.append(curso)
            if texto:
                query += " AND (t.nome LIKE ? OR t.codigo LIKE ? OR t.formulacao LIKE ?)"
                like = f"%{texto}%"
                params.extend([like, like, like])
            if estrategias:
                or_clauses = []
                for _ in estrategias:
                    or_clauses.append("t.estrategia_principal LIKE ?")
                query += " AND (" + " OR ".join(or_clauses) + ")"
                for est in estrategias:
                    params.append(f"%{est}%")

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def listar_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, codigo, nome, curso FROM teoremas ORDER BY curso, codigo")
        return [dict(row) for row in cursor.fetchall()]

    def obter_todas_tags(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT nome FROM tags ORDER BY nome")
        return [row['nome'] for row in cursor.fetchall()]

    def obter_todas_estrategias(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT estrategia_principal FROM teoremas WHERE estrategia_principal IS NOT NULL ORDER BY estrategia_principal")
        return [row['estrategia_principal'] for row in cursor.fetchall()]

    def fechar(self):
        self.conn.close()
