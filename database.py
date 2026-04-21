# database.py (versão final thread-safe)
import sqlite3
import json
from pathlib import Path
from models import CREATE_SCHEMA

class BancoDadosHeuristica:
    def __init__(self, db_path="heuristica_ifsp.db"):
        self.db_path = db_path
        self.criar_schema()
        self.carregar_dados_iniciais()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def criar_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(CREATE_SCHEMA)

    def carregar_dados_iniciais(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
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

            conn.commit()

            # Inserir Teoremas e relacionamentos
            for codigo, info in teoremas_data.items():
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

            conn.commit()
            print(f"✅ {len(teoremas_data)} teoremas carregados com sucesso!")

    def buscar_teorema_por_codigo(self, codigo):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
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
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
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
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
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

            # Se houver tags, fazemos uma subconsulta para interseção
            if tags:
                tag_placeholders = ','.join(['?'] * len(tags))
                subquery = f"""
                    SELECT tt.teorema_id
                    FROM teorema_tags tt
                    JOIN tags tg ON tt.tag_id = tg.id
                    WHERE tg.nome IN ({tag_placeholders})
                    GROUP BY tt.teorema_id
                    HAVING COUNT(DISTINCT tg.nome) = ?
                """
                # Adiciona os parâmetros das tags e o número de tags
                params_tags = list(tags) + [len(tags)]
                # Modifica a query principal para filtrar pelos IDs retornados
                query = f"""
                    SELECT t.* FROM teoremas t
                    WHERE t.id IN ({subquery})
                """
                # Se já tínhamos outros filtros, adicionamos aqui
                if curso:
                    query += " AND t.curso = ?"
                    params_tags.append(params.pop(0))  # remove curso dos params originais
                if texto:
                    query += " AND (t.nome LIKE ? OR t.codigo LIKE ? OR t.formulacao LIKE ?)"
                    params_tags.extend(params[:3])
                    params = params[3:]
                if estrategias:
                    or_clauses = []
                    for _ in estrategias:
                        or_clauses.append("t.estrategia_principal LIKE ?")
                    query += " AND (" + " OR ".join(or_clauses) + ")"
                    params_tags.extend(params)
                params = params_tags

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def listar_todos(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, codigo, nome, curso FROM teoremas ORDER BY curso, codigo")
            return [dict(row) for row in cursor.fetchall()]

    def obter_todas_tags(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT nome FROM tags ORDER BY nome")
            return [row[0] for row in cursor.fetchall()]

    def obter_todas_estrategias(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT estrategia_principal FROM teoremas WHERE estrategia_principal IS NOT NULL ORDER BY estrategia_principal")
            return [row[0] for row in cursor.fetchall()]

    def fechar(self):
        pass
