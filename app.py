# app.py
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import sqlite3
from database import BancoDadosHeuristica
from reports import GeradorRelatorios
from models import CURSOS

st.set_page_config(
    page_title="Heurística IFSP",
    page_icon="📐",
    layout="wide"
)

def gerar_grafo_teoremas(db):
    """Constrói um grafo visual de teoremas e tags usando NetworkX + Matplotlib."""
    with sqlite3.connect(db.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.id, t.codigo, t.nome, GROUP_CONCAT(tg.nome) as tags
            FROM teoremas t
            LEFT JOIN teorema_tags tt ON t.id = tt.teorema_id
            LEFT JOIN tags tg ON tt.tag_id = tg.id
            GROUP BY t.id
        """)
        teoremas = cursor.fetchall()

    G = nx.Graph()
    for t in teoremas:
        if not t['tags']:
            continue
        G.add_node(t['codigo'], tipo='teorema', label=t['codigo'])
        tags = t['tags'].split(',')
        for tag in tags:
            tag = tag.strip()
            G.add_node(tag, tipo='tag', label=tag)
            G.add_edge(t['codigo'], tag)

    # Configurar layout e cores
    pos = nx.spring_layout(G, k=0.5, seed=42)
    plt.figure(figsize=(12, 8))

    # Desenhar nós de teorema (azul)
    teorema_nodes = [n for n, attr in G.nodes(data=True) if attr.get('tipo') == 'teorema']
    nx.draw_networkx_nodes(G, pos, nodelist=teorema_nodes, node_color='#1f77b4', node_size=300, alpha=0.9)

    # Desenhar nós de tag (laranja)
    tag_nodes = [n for n, attr in G.nodes(data=True) if attr.get('tipo') == 'tag']
    nx.draw_networkx_nodes(G, pos, nodelist=tag_nodes, node_color='#ff7f0e', node_size=100, alpha=0.8)

    # Desenhar arestas
    nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.5)

    # Rótulos (apenas para teoremas, para não poluir)
    labels = {n: n for n in teorema_nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color='black')

    plt.title("Mapa de Conexões: Teoremas e Tags", fontsize=16)
    plt.axis('off')

    return plt.gcf()

def get_db():
    return BancoDadosHeuristica()

db = get_db()

# Sidebar - Filtros
st.sidebar.title("🔍 Filtros")

texto_busca = st.sidebar.text_input("🔎 Buscar por nome ou código", placeholder="Ex: Green, EC-02")

curso_sel = st.sidebar.selectbox("📚 Curso", ["Todos"] + CURSOS)

# Carregar listas de tags e estratégias do banco (com cache)
@st.cache_data
def carregar_opcoes():
    tags = db.obter_todas_tags()
    estrategias = db.obter_todas_estrategias()
    return tags, estrategias

tags_disponiveis, estrategias_disponiveis = carregar_opcoes()

tags_sel = st.sidebar.multiselect("🏷️ Tags (interseção)", tags_disponiveis)
estrategias_sel = st.sidebar.multiselect("🧠 Estratégias (qualquer uma)", estrategias_disponiveis)

if st.sidebar.button("Filtrar", use_container_width=True):
    with st.spinner("Carregando..."):
        resultados = db.buscar_por_filtros(
            curso=None if curso_sel == "Todos" else curso_sel,
            tags=tags_sel if tags_sel else None,
            estrategias=estrategias_sel if estrategias_sel else None,
            texto=texto_busca if texto_busca else None
        )
    st.session_state['resultados'] = resultados
    st.session_state['filtro_aplicado'] = True
else:
    if 'resultados' not in st.session_state:
        st.session_state['resultados'] = db.listar_todos()
        st.session_state['filtro_aplicado'] = False

if st.sidebar.button("🔄 Limpar Filtros", use_container_width=True):
    st.session_state['resultados'] = db.listar_todos()
    st.session_state['filtro_aplicado'] = False
    st.rerun()

# Área principal
st.title("📚 Sistema de Estudos em Heurística Matemática")
st.markdown("### Instituto Federal de São Paulo")

if 'teorema_sel_id' not in st.session_state:
    st.session_state['teorema_sel_id'] = None

if st.session_state['teorema_sel_id'] is None:
    teoremas = st.session_state['resultados']

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Teoremas", len(teoremas))
    with col2:
        st.metric("Cursos", len(CURSOS))
    with col3:
        if tags_sel:
            st.metric("Com tags selecionadas", len(teoremas))
        else:
            st.metric("Disponíveis", len(teoremas))

    if not teoremas:
        st.warning("Nenhum teorema encontrado com os filtros atuais.")
    else:
        cols = st.columns(3)
        for i, t in enumerate(teoremas):
            with cols[i % 3]:
                with st.container(border=True):
                    st.subheader(t['codigo'])
                    st.markdown(f"**{t['nome']}**")
                    st.caption(f"📌 {t['curso']}")
                    if st.button("📖 Ver detalhes", key=f"btn_{t['id']}", use_container_width=True):
                        st.session_state['teorema_sel_id'] = t['id']
                        st.rerun()

    st.divider()
    st.subheader("🌐 Mapa de Conexões entre Teoremas e Tags")
    with st.spinner("Gerando grafo..."):
        try:
            fig = gerar_grafo_teoremas(db)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Não foi possível gerar o grafo: {e}")

else:
    teorema = db.buscar_por_id(st.session_state['teorema_sel_id'])
    if not teorema:
        st.error("Teorema não encontrado.")
        st.session_state['teorema_sel_id'] = None
        st.rerun()

    if st.button("← Voltar para lista", use_container_width=False):
        st.session_state['teorema_sel_id'] = None
        st.rerun()

    st.header(f"{teorema['codigo']}: {teorema['nome']}")
    st.markdown(f"**Curso:** {teorema['curso']}")

    disciplinas = teorema['disciplinas'].split(',') if teorema['disciplinas'] else []
    tags = teorema['tags'].split(',') if teorema['tags'] else []
    col1, col2 = st.columns(2)
    with col1:
        if disciplinas:
            st.markdown("**Disciplinas:** " + ", ".join(disciplinas))
    with col2:
        if tags:
            st.markdown("**Tags:** " + ", ".join(tags))

    st.divider()

    tabs = st.tabs([
        "📐 Formulação", "📚 Contexto", "🧠 Estratégia", "🏗️ Aplicação",
        "📌 Pré-requisitos", "🔧 Técnicas", "💡 Intuição", "🔄 Analogias",
        "🧐 Curiosidades", "📝 Exercícios & Leituras"
    ])

    with tabs[0]:
        st.markdown(teorema['formulacao'])
    with tabs[1]:
        st.markdown(teorema['contexto_historico'] or "*Não informado*")
    with tabs[2]:
        st.markdown(f"**Estratégia Principal:** {teorema['estrategia_principal']}")
        st.markdown(f"**Padrão de Raciocínio:** {teorema['padrao_raciocinio']}")
    with tabs[3]:
        st.markdown(teorema['aplicacao_curso'] or "*Não informado*")
    with tabs[4]:
        st.markdown(teorema['pre_requisitos'] or "*Não especificado*")
    with tabs[5]:
        st.markdown(teorema['tecnicas_resolucao'] or "*Não especificado*")
    with tabs[6]:
        st.markdown(teorema['intuicao'] or "*Não fornecida*")
    with tabs[7]:
        st.markdown(teorema['analogias'] or "*Nenhuma analogia registrada*")
    with tabs[8]:
        st.markdown(teorema['curiosidades'] or "*Nenhuma curiosidade*")
    with tabs[9]:
        col_ex, col_leit = st.columns(2)
        with col_ex:
            st.subheader("✍️ Exercícios")
            exercicios = db.get_exercicios(teorema['id'])
            if exercicios:
                for ex in exercicios:
                    with st.expander(f"[{ex['nivel'].upper()}] {ex['enunciado'][:50]}..."):
                        st.write(ex['enunciado'])
            else:
                st.info("Nenhum exercício cadastrado.")
        with col_leit:
            st.subheader("📖 Leituras Complementares")
            leituras = db.get_leituras(teorema['id'])
            if leituras:
                for ref in leituras:
                    st.markdown(f"- {ref['referencia']}")
            else:
                st.info("Nenhuma leitura cadastrada.")

    st.divider()
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("📄 Gerar Relatório Completo (Markdown)", use_container_width=True):
            gerador = GeradorRelatorios(db)
            relatorio = gerador.gerar_relatorio_completo(teorema['codigo'])
            st.session_state['relatorio_gerado'] = relatorio
            st.success("Relatório gerado com sucesso!")
    with col2:
        if 'relatorio_gerado' in st.session_state:
            st.download_button(
                label="⬇️ Baixar Relatório",
                data=st.session_state['relatorio_gerado'],
                file_name=f"relatorio_{teorema['codigo']}.md",
                mime="text/markdown",
                use_container_width=True
            )
    if 'relatorio_gerado' in st.session_state:
        with st.expander("📋 Visualizar Relatório (Markdown)"):
            st.markdown(st.session_state['relatorio_gerado'])
