# 📚 Heurística IFSP

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Sistema de estudos em heurística matemática para os cursos do IFSP**, inspirado no método de George Polya. Explore 50 teoremas fundamentais, com formulações, contexto histórico, estratégias de resolução, exercícios e leituras complementares.

![Tela principal]

![Detalhes do teorema](docs/screenshot_details.png)

## ✨ Funcionalidades

- 🔍 **Busca inteligente**: filtre por curso, tags, estratégias ou texto livre.
- 📋 **Visualização rica**: cards interativos e abas organizadas por categoria.
- 📄 **Relatórios em Markdown**: gere material de estudo personalizado com um clique.
- 🧠 **Método Polya**: cada teorema inclui análise estratégica (entender, planejar, executar, revisar).
- 📊 **Métricas em tempo real**: acompanhe quantos teoremas atendem aos filtros.
- 🖥️ **Interface web amigável** (Streamlit) + **CLI** para uso em terminal.

## 🚀 Instalação e Uso

### Pré-requisitos
- Python 3.8 ou superior
- Git (opcional)

### Passos

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/heuristica-ifsp.git
   cd heuristica-ifsp

2. Crie um ambiente virtual (recomendado):
   python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3. Instale as dependências:

pip install -r requirements.txt

4. Execute a interface web:

streamlit run app.py
Acesse http://localhost:8501 no seu navegador.

5. (Alternativa) Use a interface de linha de comando:

python cli.py

📁 Estrutura do Projeto
Arquivo	Descrição
app.py	Interface web com Streamlit.
cli.py	Interface de linha de comando.
database.py	Gerenciamento do banco SQLite e carga inicial dos dados.
models.py	Definição do schema e constantes.
reports.py	Gerador de relatórios a partir de template Markdown.
teoremas.json	Base de dados com os 50 teoremas.
templates/	Pasta com o template do relatório (relatorio.md).
requirements.txt	Dependências Python.

📈 Próximos Passos (Roadmap)
Enriquecimento do conteúdo: pré-requisitos, técnicas de resolução, intuição e curiosidades.

Busca com Full-Text Search (FTS5) para maior desempenho.

Exportação para PDF.

Módulo administrativo para adicionar/editar teoremas via interface.

Deploy online (Streamlit Cloud) para acesso público.

🤝 Contribuindo
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.
Para adicionar novos teoremas, basta editar o arquivo teoremas.json seguindo a estrutura existente.

📄 Licença
Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

👨‍🏫 Contato
Desenvolvido por Pedro Machado – aluno de graduação do curso Bacharelado em Engenharia Civil do IFSP - Campus Votuporanga.
Dúvidas ou sugestões? 
Entre em contato: m.valgas@aluno.ifsp.edu.br 
