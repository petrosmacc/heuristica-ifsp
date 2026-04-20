# models.py
"""Modelos de dados e schema do banco."""

CREATE_SCHEMA = """
-- Tabela principal de teoremas
CREATE TABLE IF NOT EXISTS teoremas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    curso TEXT NOT NULL,
    formulacao TEXT NOT NULL,
    contexto_historico TEXT,
    estrategia_principal TEXT,
    padrao_raciocinio TEXT,
    aplicacao_curso TEXT,
    pre_requisitos TEXT,
    tecnicas_resolucao TEXT,
    intuicao TEXT,
    analogias TEXT,
    curiosidades TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de disciplinas associadas
CREATE TABLE IF NOT EXISTS disciplinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    curso TEXT NOT NULL
);

-- Tabela de tags (aplicações, técnicas, conceitos)
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    categoria TEXT NOT NULL
);

-- Relacionamento teorema-disciplina
CREATE TABLE IF NOT EXISTS teorema_disciplinas (
    teorema_id INTEGER NOT NULL,
    disciplina_id INTEGER NOT NULL,
    PRIMARY KEY (teorema_id, disciplina_id),
    FOREIGN KEY (teorema_id) REFERENCES teoremas(id) ON DELETE CASCADE,
    FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE
);

-- Relacionamento teorema-tags
CREATE TABLE IF NOT EXISTS teorema_tags (
    teorema_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (teorema_id, tag_id),
    FOREIGN KEY (teorema_id) REFERENCES teoremas(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Tabela de exercícios
CREATE TABLE IF NOT EXISTS exercicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teorema_id INTEGER NOT NULL,
    nivel TEXT NOT NULL,
    enunciado TEXT NOT NULL,
    solucao TEXT,
    FOREIGN KEY (teorema_id) REFERENCES teoremas(id) ON DELETE CASCADE
);

-- Tabela de leituras complementares
CREATE TABLE IF NOT EXISTS leituras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teorema_id INTEGER NOT NULL,
    referencia TEXT NOT NULL,
    tipo TEXT,
    FOREIGN KEY (teorema_id) REFERENCES teoremas(id) ON DELETE CASCADE
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_teoremas_curso ON teoremas(curso);
CREATE INDEX IF NOT EXISTS idx_teoremas_estrategia ON teoremas(estrategia_principal);
CREATE INDEX IF NOT EXISTS idx_tags_categoria ON tags(categoria);
"""

CURSOS = [
    "Engenharia Civil",
    "Engenharia Elétrica",
    "Licenciatura em Física",
    "Sistemas de Informação"
]
