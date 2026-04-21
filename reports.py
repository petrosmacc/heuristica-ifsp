# reports.py
from pathlib import Path
from datetime import datetime

TEMPLATE_PADRAO = """# RELATÓRIO DE ESTUDO - HEURÍSTICA MATEMÁTICA
## INSTITUTO FEDERAL SP

**Data:** {{ data }}

---

### 📋 IDENTIFICAÇÃO

- **Código:** {{ codigo }}
- **Teorema:** {{ nome }}
- **Curso:** {{ curso }}
- **Disciplinas:** {{ disciplinas }}

---

### 📐 1. FORMULAÇÃO FORMAL

{{ formulacao }}

---

### 📚 2. CONTEXTO HISTÓRICO

{{ contexto_historico }}

---

### 🧠 3. ANÁLISE ESTRATÉGICA (POLYA)

- **Estratégia Principal:** {{ estrategia_principal }}
- **Padrão de Raciocínio:** {{ padrao_raciocinio }}
- **Tags:** {{ tags }}

**Fase 1 - Entender:** O que é dado e o que é procurado?  
**Fase 2 - Planejar:** Como aplicar '{{ estrategia_principal }}'?  
**Fase 3 - Executar:** Passos lógicos da demonstração/aplicação.  
**Fase 4 - Revisar:** Verificação de consistência e generalização.

---

### 🏗️ 4. APLICAÇÃO NO CURSO ({{ curso }})

{{ aplicacao_curso }}

---

### 📌 5. PRÉ-REQUISITOS

{{ pre_requisitos }}

---

### 🔧 6. TÉCNICAS DE RESOLUÇÃO

{{ tecnicas_resolucao }}

---

### 💡 7. INTUIÇÃO

{{ intuicao }}

---

### 🔄 8. ANALOGIAS

{{ analogias }}

---

### 🧐 9. CURIOSIDADES

{{ curiosidades }}

---

### ✍️ 10. EXERCÍCIOS PROPOSTOS

{{ exercicios }}

---

### 📖 11. LEITURAS COMPLEMENTARES

{{ leituras }}

---
*Relatório gerado automaticamente pelo Sistema Heurística IFSP*
"""

class GeradorRelatorios:
    def __init__(self, db, template_path=None):
        self.db = db
        if template_path is None:
            template_path = Path(__file__).parent / "templates" / "relatorio.md"
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                self.template = f.read()
        except FileNotFoundError:
            print("⚠️ Template não encontrado, usando template padrão embutido.")
            self.template = TEMPLATE_PADRAO

    def gerar_relatorio_completo(self, codigo):
        teorema = self.db.buscar_teorema_por_codigo(codigo)
        if not teorema:
            return f"❌ Teorema {codigo} não encontrado."

        exercicios = self.db.get_exercicios(teorema['id'])
        leituras = self.db.get_leituras(teorema['id'])

        tags_list = teorema['tags'].split(',') if teorema['tags'] else []
        disc_list = teorema['disciplinas'].split(',') if teorema['disciplinas'] else []

        placeholders = {
            'codigo': teorema['codigo'],
            'nome': teorema['nome'],
            'curso': teorema['curso'],
            'formulacao': teorema['formulacao'],
            'contexto_historico': teorema['contexto_historico'] or '',
            'estrategia_principal': teorema['estrategia_principal'] or '',
            'padrao_raciocinio': teorema['padrao_raciocinio'] or '',
            'aplicacao_curso': teorema['aplicacao_curso'] or '',
            'pre_requisitos': teorema['pre_requisitos'] or '*Não especificado*',
            'tecnicas_resolucao': teorema['tecnicas_resolucao'] or '*Não especificado*',
            'intuicao': teorema['intuicao'] or '*Não fornecida*',
            'analogias': teorema['analogias'] or '*Nenhuma analogia registrada*',
            'curiosidades': teorema['curiosidades'] or '*Nenhuma curiosidade*',
            'disciplinas': ' | '.join(disc_list),
            'tags': ' | '.join(tags_list),
            'data': datetime.now().strftime('%d/%m/%Y %H:%M')
        }

        relatorio = self.template
        for key, value in placeholders.items():
            relatorio = relatorio.replace(f'{{{{ {key} }}}}', str(value))

        # Exercícios
        ex_md = ""
        for ex in exercicios:
            ex_md += f"• [{ex['nivel'].upper()}] {ex['enunciado']}\n"
        relatorio = relatorio.replace('{{ exercicios }}', ex_md if ex_md else '*Nenhum exercício cadastrado*')

        # Leituras
        leituras_md = ""
        for ref in leituras:
            leituras_md += f"• {ref['referencia']}\n"
        relatorio = relatorio.replace('{{ leituras }}', leituras_md if leituras_md else '*Nenhuma leitura cadastrada*')

        return relatorio
