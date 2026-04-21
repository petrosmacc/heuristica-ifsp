# database.py (versão corrigida para threading)
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
        pass  # não precisa fechar nada, cada operação já fecha sua conexão

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

            # ... (restante da lógica de inserção, mesma de antes, mas usando a conexão `conn`)
            # Certifique-se de usar `conn` em vez de `self.conn`
            # Exemplo: cursor.execute(...); conn.commit()
            # ...
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
            # ... (query montada dinamicamente, mesma lógica anterior)
            # Certifique-se de usar a conexão local `conn`
            # ...
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
        pass  # não há mais conexão persistente
