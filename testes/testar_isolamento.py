"""
Teste de isolamento entre nutricionistas.

Cria dados FICTÍCIOS num arquivo temporário (o dados_sono.csv real não é
tocado) para duas nutricionistas, "ana" e "bia", e confere que cada uma
só enxerga os próprios pacientes — tanto nas funções de dados quanto
nas telas do app.

Como rodar (na pasta do projeto):
    venv\\Scripts\\python testes\\testar_isolamento.py
"""

import os
import secrets
import sys
import tempfile

PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PASTA_PROJETO)
os.chdir(PASTA_PROJETO)

import pandas as pd  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

import auth  # noqa: E402
import database  # noqa: E402

# Senhas sorteadas a cada execução: só existem durante o teste.
SENHAS = {"ana": secrets.token_urlsafe(12), "bia": secrets.token_urlsafe(12)}
for codigo, senha in SENHAS.items():
    os.environ[f"SENHA_NUTRI_{codigo.upper()}"] = senha

PACIENTES = {
    "ana": ["Paciente Ana Um", "Paciente Ana Dois", "Paciente Ana Tres"],
    "bia": ["Paciente Bia Um", "Paciente Bia Dois"],
    "": ["Paciente Sem Nutri"],
}

resultados = []


def confere(descricao: str, ok: bool) -> None:
    resultados.append(ok)
    print(f"  {'✅ PASSOU' if ok else '❌ FALHOU'}  {descricao}")


def resposta_ficticia(nome: str, nutri: str, i: int) -> dict:
    return {
        "nome": nome, "email": f"{nome.lower().replace(' ', '.')}@exemplo.com",
        "idade": 30 + i, "sexo": "Outro", "profissao": "teste",
        "hora_dormir": "23:00:00", "hora_acordar": "07:00:00", "horas_sono": 6 + i,
        "qualidade_sono": "Boa", "interrupcoes_noturnas": 1, "cronotipo_pontos": 4,
        "cronotipo": "Intermediário", "porcoes_frutas": 3, "litros_agua": 2.0,
        "xicaras_cafe": 1, "freq_processados": 5, "energia": 5 + i, "humor": 6,
        "produtividade": 6, "dias_exercicio": 2, "minutos_exercicio": 30,
        "nivel_estresse": 5, database.COLUNA_NUTRICIONISTA: nutri,
    }


def textos_da_tela(at: AppTest) -> str:
    """Junta todo texto visível da tela (markdown, títulos, avisos, tabelas)."""
    partes = [str(m.value) for m in at.markdown]
    partes += [str(e.value) for e in list(at.info) + list(at.error) + list(at.caption)]
    partes += [d.value.to_csv() for d in at.dataframe]
    return "\n".join(partes)


def nomes_na_tela(at: AppTest) -> set[str]:
    texto = textos_da_tela(at)
    return {n for lista in PACIENTES.values() for n in lista if n in texto}


def entrar(codigo: str, senha: str) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=60)
    at.session_state.step = "dashboard"
    at.run()
    at.text_input(key="login_codigo").input(codigo)
    at.text_input(key="login_senha").input(senha)
    next(b for b in at.button if b.label == "Entrar").click()
    at.run()
    return at


with tempfile.TemporaryDirectory() as pasta:
    database.CSV_PATH = os.path.join(pasta, "dados_sono.csv")

    print("\n1) Arquivo no formato antigo (sem a coluna nutricionista_id)")
    antiga = resposta_ficticia("Paciente Antigo", "", 0)
    antiga.pop(database.COLUNA_NUTRICIONISTA)
    antiga["data_envio"] = "2026-01-01 10:00:00.000000"
    pd.DataFrame([antiga]).to_csv(database.CSV_PATH, index=False)
    PACIENTES[""].append("Paciente Antigo")
    database.carregar_dados.clear()

    for nutri, nomes in PACIENTES.items():
        for i, nome in enumerate(nomes):
            if nome != "Paciente Antigo":
                database.salvar_dados(resposta_ficticia(nome, nutri, i))

    copias = [f for f in os.listdir(pasta) if "_backup_" in f]
    confere("cópia de segurança criada antes de mudar o formato do arquivo", len(copias) == 1)
    todos = database.carregar_dados()
    confere("resposta antiga preservada (nenhum dado apagado)", "Paciente Antigo" in set(todos["nome"]))
    confere(f"total de respostas no arquivo = 7 (encontrado: {len(todos)})", len(todos) == 7)

    print("\n2) Funções de dados")
    for nutri in ("ana", "bia"):
        nomes = set(database.carregar_dados_da_nutricionista(nutri)["nome"])
        confere(f"'{nutri}' vê só os próprios pacientes: {sorted(nomes)}", nomes == set(PACIENTES[nutri]))
    for codigo in ("", "nan", "carla"):
        confere(f"código {codigo!r} não vê dados de ninguém",
                database.carregar_dados_da_nutricionista(codigo).empty)
    email_bia = resposta_ficticia("Paciente Bia Um", "bia", 0)["email"]
    confere("e-mail de paciente da bia não é 'reconhecido' no link da ana",
            not database.email_ja_respondeu(email_bia, "ana"))

    print("\n3) Login")
    confere("senha certa da ana entra", auth.verificar_login("ana", SENHAS["ana"]))
    confere("senha da bia NÃO entra como ana", not auth.verificar_login("ana", SENHAS["bia"]))
    confere("senha vazia NÃO entra", not auth.verificar_login("ana", ""))
    confere("nutricionista sem senha configurada NÃO entra", not auth.verificar_login("carla", "x"))

    print("\n4) Telas do app")
    at = AppTest.from_file("app.py", default_timeout=60)
    at.session_state.step = "dashboard"
    at.run()
    confere("dashboard sem login mostra só o formulário (nenhum paciente)",
            not at.exception and not nomes_na_tela(at) and len(at.dataframe) == 0)

    at = entrar("ana", SENHAS["bia"])
    confere("login com senha errada mostra erro e nenhum paciente",
            len(at.error) == 1 and not nomes_na_tela(at))

    for nutri in ("ana", "bia"):
        at = entrar(nutri, SENHAS[nutri])
        vistos = nomes_na_tela(at)
        confere(f"tela da '{nutri}' sem erros", not at.exception)
        confere(f"tela da '{nutri}' mostra: {sorted(vistos)}", vistos == set(PACIENTES[nutri]))

    for link, esperado in (("ana", "ana"), ("carla", ""), ("../x", "")):
        at = AppTest.from_file("app.py", default_timeout=60)
        at.query_params["nutri"] = link
        at.run()
        confere(f"link ?nutri={link} liga as respostas a {esperado or 'ninguém'!r}",
                at.session_state.nutricionista_id == esperado)

print(f"\nResultado: {sum(resultados)} de {len(resultados)} verificações passaram.")
sys.exit(0 if all(resultados) else 1)
