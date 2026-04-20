#!/usr/bin/env python3
# cli.py
"""Interface de linha de comando para o sistema Heurística IFSP."""

from database import BancoDadosHeuristica
from reports import GeradorRelatorios

def main():
    print("\n" + "="*80)
    print("  SISTEMA DE ESTUDOS EM HEURÍSTICA MATEMÁTICA - IFSP v2.0")
    print("="*80 + "\n")

    with BancoDadosHeuristica() as db:
        gerador = GeradorRelatorios(db)

        while True:
            print("\nMENU PRINCIPAL:")
            print("1. Listar todos os teoremas")
            print("2. Buscar por Curso")
            print("3. Buscar por Tag")
            print("4. Buscar por Estratégia")
            print("5. Gerar Relatório Completo")
            print("6. Sair")

            opcao = input("\nEscolha uma opção: ").strip()

            if opcao == "1":
                teoremas = db.listar_todos()
                print("\n" + "-"*60)
                for t in teoremas:
                    print(f"{t['codigo']:6} | {t['curso']:20} | {t['nome']}")
                print("-"*60)

            elif opcao == "2":
                from models import CURSOS
                print("\nCursos disponíveis:")
                for i, c in enumerate(CURSOS, 1):
                    print(f"{i}. {c}")
                try:
                    idx = int(input("Escolha o número do curso: ")) - 1
                    if 0 <= idx < len(CURSOS):
                        curso_sel = CURSOS[idx]
                        resultados = db.buscar_por_filtros(curso=curso_sel)
                        print(f"\n🔍 {len(resultados)} teoremas em {curso_sel}:")
                        for r in resultados:
                            print(f"  {r['codigo']}: {r['nome']}")
                except ValueError:
                    print("❌ Entrada inválida.")

            elif opcao == "3":
                termo = input("Digite a tag: ").strip()
                resultados = db.buscar_por_filtros(tag=termo)
                if resultados:
                    print(f"\n🔍 {len(resultados)} teoremas com tag '{termo}':")
                    for r in resultados:
                        print(f"  {r['codigo']}: {r['nome']} ({r['curso']})")
                else:
                    print("❌ Nenhum teorema encontrado.")

            elif opcao == "4":
                termo = input("Digite a estratégia: ").strip()
                resultados = db.buscar_por_filtros(estrategia=termo)
                if resultados:
                    print(f"\n🔍 {len(resultados)} teoremas com estratégia '{termo}':")
                    for r in resultados:
                        print(f"  {r['codigo']}: {r['nome']}")
                else:
                    print("❌ Nenhum teorema encontrado.")

            elif opcao == "5":
                codigo = input("Código do teorema (ex: EC-04): ").strip().upper()
                relatorio = gerador.gerar_relatorio_completo(codigo)
                print("\n" + relatorio)
                salvar = input("\nSalvar em arquivo? (s/n): ").strip().lower()
                if salvar == 's':
                    nome_arq = f"relatorio_{codigo.lower()}.md"
                    with open(nome_arq, "w", encoding="utf-8") as f:
                        f.write(relatorio)
                    print(f"✅ Relatório salvo em '{nome_arq}'")

            elif opcao == "6":
                print("\n👋 Encerrando. Bons estudos!")
                break
            else:
                print("❌ Opção inválida.")

            input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
