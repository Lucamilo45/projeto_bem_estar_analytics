"""
Tira fotos (capturas de tela) das telas Início, Questionário, Resultado e
Dashboard num navegador de verdade (Microsoft Edge), no tamanho de
computador e de celular, usando dados FICTÍCIOS.

Sobe um servidor de teste separado na porta 8599, com um CSV temporário
(o dados_sono.csv real não é tocado) e uma senha sorteada na hora.

Como rodar (na pasta do projeto):
    venv\\Scripts\\pip install -r requirements-dev.txt
    venv\\Scripts\\python testes\\capturar_telas.py
As fotos ficam na pasta testes/capturas/ (ignorada pelo git).
"""

import os
import secrets
import subprocess
import sys
import tempfile
import time
import urllib.request
from urllib.parse import unquote

from playwright.sync_api import sync_playwright

PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_FOTOS = os.path.join(PASTA_PROJETO, "testes", "capturas")
PORTA = 8599
URL = f"http://localhost:{PORTA}"
SENHA = secrets.token_urlsafe(12)


def criar_dados_ficticios(caminho: str) -> None:
    """Grava 10 respostas fictícias da nutricionista 'demo' no CSV temporário."""
    os.environ["DADOS_CSV"] = caminho
    sys.path.insert(0, PASTA_PROJETO)
    import database

    database.CSV_PATH = caminho
    for i in range(10):
        database.salvar_dados({
            "nome": f"Paciente Ficticio {i}", "email": f"p{i}@exemplo.com", "idade": 25 + i,
            "sexo": "Outro", "profissao": "teste", "hora_dormir": "23:00:00",
            "hora_acordar": "07:00:00", "horas_sono": 5 + i % 4, "qualidade_sono":
            ["Ruim", "Regular", "Boa", "Excelente"][i % 4], "interrupcoes_noturnas": i % 3,
            "cronotipo_pontos": i % 9, "cronotipo": ["Matutino", "Intermediário", "Vespertino"][i % 3],
            "porcoes_frutas": i % 6, "litros_agua": 1.0 + (i % 4) * 0.5, "xicaras_cafe": i % 5,
            "freq_processados": i % 10, "energia": 3 + i % 7, "humor": 4 + i % 6,
            "produtividade": 5, "dias_exercicio": i % 7, "minutos_exercicio": 30,
            "nivel_estresse": 9 - i % 8, "nutricionista_id": "demo",
        })


def esperar_servidor() -> None:
    for _ in range(60):
        try:
            if urllib.request.urlopen(f"{URL}/_stcore/health").read() == b"ok":
                return
        except OSError:
            pass
        time.sleep(1)
    raise RuntimeError("O servidor de teste não respondeu.")


def esperar_tela(pagina) -> None:
    """Espera o Streamlit terminar de desenhar a tela."""
    # O Streamlit marca a página com data-test-script-state="notRunning"
    # quando termina de rodar o app.
    time.sleep(0.5)
    pagina.wait_for_selector(
        '[data-testid="stApp"][data-test-script-state="notRunning"]', timeout=60000
    )
    pagina.wait_for_selector('[data-testid="stMainBlockContainer"] > div', timeout=60000)
    time.sleep(1.5)


def clicar(pagina, texto: str) -> None:
    pagina.get_by_role("button", name=texto).first.click()
    esperar_tela(pagina)


def fotografar(pagina, nome: str) -> None:
    pagina.screenshot(path=os.path.join(PASTA_FOTOS, f"{nome}.png"), full_page=True)
    print(f"  📸 {nome}.png")


os.makedirs(PASTA_FOTOS, exist_ok=True)
with tempfile.TemporaryDirectory() as pasta:
    criar_dados_ficticios(os.path.join(pasta, "dados_sono.csv"))
    env = dict(os.environ, SENHA_NUTRI_DEMO=SENHA, ANTHROPIC_API_KEY="",
               NOME_NUTRI_DEMO="Nutricionista Demo", WHATSAPP_NUTRI_DEMO="5511900000000",
               INSTAGRAM_NUTRI_DEMO="nutri.demo", DADOS_CSV=os.path.join(pasta, "dados_sono.csv"))
    env.pop("APP_URL", None)  # o link deve usar o endereço real do app
    servidor = subprocess.Popen(
        [os.path.join(PASTA_PROJETO, "venv", "Scripts", "streamlit.exe"), "run", "app.py",
         "--server.port", str(PORTA), "--server.headless", "true"],
        cwd=PASTA_PROJETO, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    try:
        esperar_servidor()
        with sync_playwright() as p:
            navegador = p.chromium.launch(channel="msedge")
            for tamanho, largura, altura in (("computador", 1366, 900), ("celular", 390, 844)):
                print(f"\n{tamanho}:")
                contexto = navegador.new_context(
                    viewport={"width": largura, "height": altura}, accept_downloads=True,
                    permissions=["clipboard-read", "clipboard-write"],
                )
                pagina = contexto.new_page()

                pagina.goto(f"{URL}/?nutri=demo")
                esperar_tela(pagina)
                fotografar(pagina, f"{tamanho}_1_inicio")
                # A ilustração precisa carregar e ocupar toda a largura da coluna.
                info = pagina.locator(".home-ilustracao").evaluate(
                    """i => ({carregou: i.complete && i.naturalWidth > 0,
                              largura: Math.round(i.getBoundingClientRect().width),
                              coluna: Math.round(i.closest('[data-testid="stColumn"]')
                                                  .getBoundingClientRect().width)})"""
                )
                print(f"  ilustração carregou: {info['carregou']} | largura "
                      f"{info['largura']}px de {info['coluna']}px da coluna")

                clicar(pagina, "🚀 Começar o questionário")
                pagina.get_by_text("Li e concordo").click()
                esperar_tela(pagina)
                clicar(pagina, "✅ Concordo e quero continuar")
                pagina.get_by_role("textbox", name="Nome", exact=True).fill("Paciente Foto")
                pagina.get_by_role("textbox", name="E-mail", exact=True).fill("foto@exemplo.com")
                pagina.get_by_role("textbox", name="E-mail", exact=True).press("Enter")
                esperar_tela(pagina)
                clicar(pagina, "Próximo ➡️")
                fotografar(pagina, f"{tamanho}_2_questionario")
                for _ in range(4):
                    clicar(pagina, "Próximo ➡️")
                clicar(pagina, "🎉 Finalizar")
                fotografar(pagina, f"{tamanho}_3_resultado")
                contatos = pagina.locator(".botao-contato")
                print("  contatos para o paciente:",
                      [contatos.nth(i).get_attribute("href").split("?")[0] for i in range(contatos.count())])
                contatos.first.scroll_into_view_if_needed()
                time.sleep(1)
                fotografar(pagina, f"{tamanho}_3b_contatos")

                clicar(pagina, "🏠 Voltar ao início")
                clicar(pagina, "📊 Ver Dashboard")
                pagina.get_by_role("textbox", name="Seu código de nutricionista").fill("demo")
                pagina.get_by_role("textbox", name="Senha", exact=True).fill(SENHA)
                clicar(pagina, "Entrar")
                pagina.wait_for_selector(".js-plotly-plot", timeout=30000)
                time.sleep(2)
                graficos = pagina.locator(".js-plotly-plot").count()
                print(f"  gráficos desenhados na tela: {graficos}")
                fotografar(pagina, f"{tamanho}_4_dashboard")
                # Link de convite: copiar, compartilhar e QR Code
                link_mostrado = pagina.locator('[data-testid="stCode"]').first.inner_text().strip()
                print("  link de convite mostrado:", link_mostrado)
                quadro = pagina.frame_locator('iframe[title="st.iframe"], iframe').first
                quadro.get_by_text("Copiar link").click()
                time.sleep(1)
                copiado = pagina.evaluate("navigator.clipboard.readText()")
                print("  'Copiar link' copiou o link certo:", copiado == link_mostrado,
                      "| botão mostra:", quadro.locator("#copiar").inner_text().strip())
                compartilhar = pagina.get_by_role("link", name="📲 Compartilhar no WhatsApp")
                print("  'Compartilhar no WhatsApp' contém o link:",
                      link_mostrado in unquote(compartilhar.get_attribute("href")))
                with pagina.expect_download() as baixado:
                    pagina.locator(".botao-qr").click()
                arquivo = baixado.value
                destino = os.path.join(PASTA_FOTOS, f"{tamanho}_qrcode_{arquivo.suggested_filename}")
                arquivo.save_as(destino)
                print(f"  QR Code baixado: {arquivo.suggested_filename} ({os.path.getsize(destino)} bytes)")
                pagina.locator(".qr-convite").scroll_into_view_if_needed()
                time.sleep(1)
                fotografar(pagina, f"{tamanho}_4b_convite")
                # O Streamlit rola por dentro da página: rola até os gráficos.
                pagina.locator(".js-plotly-plot").first.scroll_into_view_if_needed()
                time.sleep(1)
                fotografar(pagina, f"{tamanho}_5_graficos")
                contexto.close()
            navegador.close()
    finally:
        servidor.terminate()
        erros = servidor.communicate(timeout=30)[1].decode("utf-8", "replace")
        linhas_erro = [l for l in erros.splitlines() if "Error" in l or "Traceback" in l]
        print("\nErros no servidor:", linhas_erro or "nenhum")
