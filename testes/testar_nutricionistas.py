"""
Teste do cadastro das nutricionistas: contatos próprios de cada uma,
link de convite (?nutri=codigo), compartilhamento no WhatsApp e QR Code.

Usa nutricionistas e dados FICTÍCIOS (o dados_sono.csv real não é tocado)
e senhas sorteadas na hora.

Como rodar (na pasta do projeto):
    venv\\Scripts\\python testes\\testar_nutricionistas.py
"""

import base64
import os
import re
import secrets
import sys
import tempfile
from urllib.parse import unquote

PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PASTA_PROJETO)
os.chdir(PASTA_PROJETO)

os.environ["ANTHROPIC_API_KEY"] = ""  # sem IA: usa a dica fixa
os.environ["APP_URL"] = "https://exemplo.streamlit.app"
CADASTRO = {
    "ANA": {"SENHA": secrets.token_urlsafe(12), "NOME": "Ana Souza",
            "WHATSAPP": "+55 (11) 98888-7777", "INSTAGRAM": "@ana.nutri"},
    "BIA": {"SENHA": secrets.token_urlsafe(12), "NOME": "Bia Lima",
            "WHATSAPP": "5521977776666", "INSTAGRAM": "bia_nutri"},
    # Só senha, sem contatos: não deve mostrar botões de contato.
    "CAIO": {"SENHA": secrets.token_urlsafe(12)},
}
for codigo, campos in CADASTRO.items():
    for campo, valor in campos.items():
        os.environ[f"{campo}_NUTRI_{codigo}"] = valor
os.environ["WHATSAPP_NUTRI_ERRADO"] = "123"  # sem senha: não existe

from streamlit.testing.v1 import AppTest  # noqa: E402

import auth  # noqa: E402
import convite  # noqa: E402
import database  # noqa: E402

resultados = []


def confere(descricao: str, ok: bool) -> None:
    resultados.append(ok)
    print(f"  {'✅ PASSOU' if ok else '❌ FALHOU'}  {descricao}")


def html_da_tela(at: AppTest) -> str:
    return "\n".join(str(m.value) for m in at.markdown) + "\n".join(
        str(c.value) for c in list(at.caption) + list(at.code)
    )


def tela_resultado(nutri: str) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=60)
    at.session_state.step = "resumo"
    at.session_state.nutricionista_id = nutri
    at.session_state.user_data = {"nome": "Paciente Teste", "horas_sono": 7, "energia": 6}
    return at.run()


def painel(codigo: str) -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=60)
    at.session_state.step = "dashboard"
    at.session_state.nutri_logada = codigo
    return at.run()


print("\n1) Cadastro")
ana = auth.perfil("ana")
confere(f"nome da ana: {ana['nome']!r}", ana["nome"] == "Ana Souza")
confere(f"WhatsApp com só números: {ana['whatsapp']!r}", ana["whatsapp"] == "5511988887777")
confere(f"Instagram sem @: {ana['instagram']!r}", ana["instagram"] == "ana.nutri")
caio = auth.perfil("caio")
confere(f"sem NOME cadastrado usa o código: {caio['nome']!r}", caio["nome"] == "Caio")
confere("sem senha a nutricionista não existe", auth.perfil("errado") is None)
os.environ["INSTAGRAM_NUTRI_CAIO"] = "nome com espaço"
os.environ["WHATSAPP_NUTRI_CAIO"] = "1234"
confere("Instagram e WhatsApp inválidos ficam vazios (sem botão errado)",
        auth.perfil("caio")["instagram"] == "" and auth.perfil("caio")["whatsapp"] == "")
del os.environ["INSTAGRAM_NUTRI_CAIO"], os.environ["WHATSAPP_NUTRI_CAIO"]

with tempfile.TemporaryDirectory() as pasta:
    database.CSV_PATH = os.path.join(pasta, "dados_sono.csv")
    database.carregar_dados.clear()

    print("\n2) Contatos mostrados aos pacientes")
    texto = html_da_tela(tela_resultado("ana"))
    confere("paciente da ana vê o WhatsApp da ana", "wa.me/5511988887777" in texto)
    confere("paciente da ana vê o Instagram da ana", "instagram.com/ana.nutri" in texto)
    confere("paciente da ana NÃO vê contatos da bia",
            "5521977776666" not in texto and "bia_nutri" not in texto)
    texto = html_da_tela(tela_resultado("bia"))
    confere("paciente da bia vê só os contatos da bia",
            "wa.me/5521977776666" in texto and "5511988887777" not in texto)
    texto = html_da_tela(tela_resultado(""))
    confere("paciente sem link não vê nenhum contato (nem de exemplo)",
            "wa.me" not in texto and "instagram.com" not in texto and "5511999999999" not in texto)
    texto = html_da_tela(tela_resultado("caio"))
    confere("nutricionista sem contatos cadastrados: sem botões", "wa.me" not in texto)

    texto = html_da_tela(tela_resultado("ana"))
    confere("botões grandes 'Falar no WhatsApp' e 'Seguir no Instagram'",
            "Falar no WhatsApp" in texto and "Seguir no Instagram" in texto and "botao-nutri" in texto)
    whatsapp = re.search(r'href="(https://wa\.me/[^"]+)"', texto).group(1)
    confere("mensagem pronta do WhatsApp cita o nome da nutricionista",
            "Olá, Ana Souza! Vim pelo app de Bem-Estar" in unquote(whatsapp))
    confere("Instagram leva ao perfil certo", 'href="https://www.instagram.com/ana.nutri/"' in texto)
    confere("cartão mostra o nome e as iniciais", "Ana Souza" in texto and ">AS<" in texto)

    os.environ["WHATSAPP_NUTRI_CAIO"] = "5531955554444"
    texto = html_da_tela(tela_resultado("caio"))
    confere("só WhatsApp cadastrado: aparece só o botão do WhatsApp",
            "Falar no WhatsApp" in texto and "Seguir no Instagram" not in texto)
    del os.environ["WHATSAPP_NUTRI_CAIO"]

    for nutri, deve_aparecer in (("ana", True), ("", False)):
        at = AppTest.from_file("app.py", default_timeout=60)
        at.session_state.step = "dicas"
        at.session_state.tema = "alimentacao"
        at.session_state.nutricionista_id = nutri
        texto = html_da_tela(at.run())
        confere(f"página de dicas {'com' if nutri else 'sem'} link de nutricionista: "
                f"cartão {'aparece' if deve_aparecer else 'não aparece'}",
                not at.exception and ("Falar no WhatsApp" in texto) == deve_aparecer)

    at = AppTest.from_file("app.py", default_timeout=60)
    at.query_params["nutri"] = "ana"
    at.run()
    confere("início pelo link da ana mostra 'Convite de Ana Souza'", "Convite de Ana Souza" in html_da_tela(at))

    print("\n3) Link de convite no painel")
    for codigo, nome in (("ana", "Ana Souza"), ("bia", "Bia Lima")):
        at = painel(codigo)
        esperado = f"https://exemplo.streamlit.app/?nutri={codigo}"
        confere(f"painel da {codigo} sem erros", not at.exception)
        confere(f"link da {codigo}: {esperado}", any(c.value == esperado for c in at.code))
        compartilhar = [b for b in at.get("link_button") if "WhatsApp" in b.proto.label]
        confere(f"botão 'Compartilhar no WhatsApp' leva o link da {codigo}",
                len(compartilhar) == 1 and esperado in unquote(compartilhar[0].proto.url))
        texto = html_da_tela(at)
        qr = re.search(r'class="qr-convite" src="data:image/png;base64,([^"]+)"', texto)
        confere(f"QR Code da {codigo} aparece e é do link dela",
                bool(qr) and base64.b64decode(qr.group(1)) == convite.qr_code_png(esperado, nome))
        confere(f"botão de baixar o QR Code da {codigo}", f'download="convite-{codigo}.png"' in texto)
        outro = "bia" if codigo == "ana" else "ana"
        confere(f"painel da {codigo} não mostra o link da {outro}", f"?nutri={outro}" not in texto)
    confere("botão 'Copiar link' presente", len(painel("ana").get("iframe")) >= 1)

print(f"\nResultado: {sum(resultados)} de {len(resultados)} verificações passaram.")
sys.exit(0 if all(resultados) else 1)
