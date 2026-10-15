"""
Teste do fluxo completo: um paciente entra pelo link de uma nutricionista,
responde o questionário inteiro, clica em "Finalizar" e a nutricionista
abre o dashboard com os gráficos.

Usa dados FICTÍCIOS num arquivo temporário (o dados_sono.csv real não é
tocado) e desliga a IA para não gastar créditos.

Como rodar (na pasta do projeto):
    venv\\Scripts\\python testes\\testar_fluxo_completo.py
"""

import os
import secrets
import sys
import tempfile

PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PASTA_PROJETO)
os.chdir(PASTA_PROJETO)

os.environ["ANTHROPIC_API_KEY"] = ""  # sem IA: usa a dica fixa
SENHA = secrets.token_urlsafe(12)  # sorteada, só existe durante o teste
os.environ["SENHA_NUTRI_DEMO"] = SENHA

from streamlit.testing.v1 import AppTest  # noqa: E402

import database  # noqa: E402

resultados = []


def confere(descricao: str, ok: bool) -> None:
    resultados.append(ok)
    print(f"  {'✅ PASSOU' if ok else '❌ FALHOU'}  {descricao}")


ESTADO = ("step", "user_data", "nutricionista_id")


def abrir_tela(estado: dict) -> AppTest:
    """Abre o app do zero com o estado (tela atual e respostas) da etapa anterior.

    Abrir cada tela do zero evita uma limitação do AppTest: quando o app troca
    de tela com st.rerun(), ele mantém campos da tela anterior e falha ao lê-los.
    No navegador isso não acontece.
    """
    at = AppTest.from_file("app.py", default_timeout=60)
    for chave, valor in estado.items():
        at.session_state[chave] = valor
    at.run()
    return at


def clicar(at: AppTest, texto: str) -> dict:
    """Clica no botão e devolve o estado resultante (próxima tela + respostas)."""
    next(b for b in at.button if texto in b.label).click()
    at.run()
    return {chave: at.session_state[chave] for chave in ESTADO}


def responder_questionario(i: int) -> AppTest:
    # Entrada pelo link da nutricionista
    at = AppTest.from_file("app.py", default_timeout=60)
    at.query_params["nutri"] = "demo"
    at.run()
    estado = clicar(at, "Começar o questionário")

    at = abrir_tela(estado)                      # consentimento
    at.checkbox[0].check().run()
    estado = clicar(at, "Concordo e quero continuar")

    at = abrir_tela(estado)                      # perfil
    at.text_input[0].input(f"Paciente Ficticio {i}")
    at.text_input[1].input(f"paciente{i}@exemplo.com")
    estado = clicar(at, "Próximo")

    at = abrir_tela(estado)                      # sono
    at.slider[0].set_value(5 + i % 4)            # horas de sono
    estado = clicar(at, "Próximo")

    at = abrir_tela(estado)                      # cronotipo
    estado = clicar(at, "Próximo")

    at = abrir_tela(estado)                      # alimentação
    at.slider[0].set_value(i % 6)                # porções de frutas
    estado = clicar(at, "Próximo")

    at = abrir_tela(estado)                      # bem-estar
    at.slider[0].set_value(3 + i % 6)            # energia
    estado = clicar(at, "Próximo")

    at = abrir_tela(estado)                      # atividade
    at.slider[0].set_value(i % 7)                # dias de exercício
    at.slider[2].set_value(9 - i % 8)            # estresse
    clicar(at, "Finalizar")
    return at


with tempfile.TemporaryDirectory() as pasta:
    database.CSV_PATH = os.path.join(pasta, "dados_sono.csv")
    database.carregar_dados.clear()

    print("\n1) Paciente responde o questionário e clica em Finalizar")
    for i in range(10):
        at = responder_questionario(i)
        if i == 0:
            confere("Finalizar sem erros", not at.exception)
            confere("abre a tela de resultado", at.session_state.step == "resumo")

    df = database.carregar_dados()
    confere(f"10 respostas salvas (encontradas: {len(df)})", len(df) == 10)
    confere("todas ligadas à nutricionista 'demo'",
            set(df[database.COLUNA_NUTRICIONISTA]) == {"demo"})

    print("\n2) Nutricionista abre o dashboard")
    at = AppTest.from_file("app.py", default_timeout=60)
    at.run()
    clicar(at, "Ver Dashboard")
    at.text_input(key="login_codigo").input("demo")
    at.text_input(key="login_senha").input(SENHA)
    clicar(at, "Entrar")
    graficos = at.get("plotly_chart")
    confere("dashboard sem erros", not at.exception)
    confere(f"5 gráficos na tela (encontrados: {len(graficos)})", len(graficos) == 5)
    confere("tabela com as 10 respostas", len(at.dataframe) == 1 and len(at.dataframe[0].value) == 10)

print(f"\nResultado: {sum(resultados)} de {len(resultados)} verificações passaram.")
sys.exit(0 if all(resultados) else 1)
