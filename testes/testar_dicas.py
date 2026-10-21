"""
Teste das páginas de dicas abertas pelos cards da página inicial.

Confere que cada card abre a página do seu tema, que todas as páginas
abrem sem erros, que o conteúdo não fala em calorias ou quantidades e
que sempre aparece o aviso de que não substitui a nutricionista.

Como rodar (na pasta do projeto):
    venv\\Scripts\\python testes\\testar_dicas.py
"""

import os
import re
import sys

PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PASTA_PROJETO)
os.chdir(PASTA_PROJETO)
os.environ["ANTHROPIC_API_KEY"] = ""

from streamlit.testing.v1 import AppTest  # noqa: E402

import conteudo_dicas  # noqa: E402

resultados = []


def confere(descricao: str, ok: bool) -> None:
    resultados.append(ok)
    print(f"  {'✅ PASSOU' if ok else '❌ FALHOU'}  {descricao}")


def texto_da_tela(at: AppTest) -> str:
    return "\n".join(str(m.value) for m in at.markdown)


print("\n1) Conteúdo")
todo_texto = " ".join(
    [t["titulo"] + " " + t["introducao"] + " " + t["resumo"] for t in conteudo_dicas.TEMAS.values()]
    + [item for t in conteudo_dicas.TEMAS.values() for _, _, itens in t["secoes"] for item in itens]
).lower()
proibidas = re.findall(r"\bkcal\b|calori\w*|\bgramas?\b|\bml\b|\blitros?\b|\d", todo_texto)
confere(f"sem calorias nem quantidades (encontrado: {sorted(set(proibidas)) or 'nada'})", not proibidas)
confere("4 temas: sono, energia, alimentação e exercícios",
        list(conteudo_dicas.TEMAS) == ["sono", "energia", "alimentacao", "exercicios"])
confere("alimentação fala de períodos do dia, hidratação e lanches",
        all(s in todo_texto for s in ("manhã", "almoço", "noite", "hidratação", "lanches")))
confere("exercícios fala de benefícios, como começar, horários e cuidados",
        all(s in todo_texto for s in ("benefícios", "como começar", "horários", "cuidados")))

print("\n2) Cards da página inicial")
at = AppTest.from_file("app.py", default_timeout=60).run()
botoes = {b.key: b for b in at.button if (b.key or "").startswith("btn_tema_")}
confere(f"4 cards clicáveis na página inicial (encontrados: {len(botoes)})", len(botoes) == 4)

for chave, tema in conteudo_dicas.TEMAS.items():
    at = AppTest.from_file("app.py", default_timeout=60).run()
    at.button(key=f"btn_tema_{chave}").click().run()
    texto = texto_da_tela(at)
    confere(f"card '{tema['titulo']}' abre a página do tema",
            at.session_state.step == "dicas" and at.session_state.tema == chave and not at.exception)
    confere(f"  página mostra todas as seções ({len(tema['secoes'])})",
            all(titulo in texto for _, titulo, _ in tema["secoes"]))
    confere("  página mostra o aviso de que não substitui a nutricionista", conteudo_dicas.AVISO in texto)
    outros = [b for b in at.button if (b.key or "").startswith("ver_")]
    confere("  'Veja também' leva aos outros 3 temas", len(outros) == 3)

print("\n3) Navegação entre temas e volta")
at = AppTest.from_file("app.py", default_timeout=60)
at.session_state.step = "dicas"
at.session_state.tema = "sono"
at.run()
at.button(key="ver_alimentacao").click().run()
confere("de Sono para Alimentação pelo 'Veja também'", at.session_state.tema == "alimentacao")
next(b for b in at.button if "Voltar ao início" in b.label).click().run()
confere("'Voltar ao início' volta para a página inicial", at.session_state.step == "home")

print(f"\nResultado: {sum(resultados)} de {len(resultados)} verificações passaram.")
sys.exit(0 if all(resultados) else 1)
