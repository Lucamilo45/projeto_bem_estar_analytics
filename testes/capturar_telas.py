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

import functools
import http.server
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
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


def servir_anuncios(pasta: str) -> str:
    """Faz o papel do Google Sheets: serve um CSV de anúncios fictícios e uma
    imagem numa porta local. Retorna o endereço do CSV."""
    shutil.copy(os.path.join(PASTA_PROJETO, "assets", "banner_home.webp"), os.path.join(pasta, "foto.webp"))
    servidor = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0),
        functools.partial(http.server.SimpleHTTPRequestHandler, directory=pasta),
    )
    servidor.RequestHandlerClass.log_message = lambda *args: None
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{servidor.server_address[1]}"
    linhas = [
        "ativo,espaco,titulo,descricao,imagem_url,link,data_inicio,data_fim",
        f"sim,esporte,Corrida de Rua Ficticia,Inscrições abertas para a corrida do bairro.,{base}/foto.webp,https://example.com/1,,",
        f"sim,esporte,Loja Esportiva Ficticia,Tênis e roupas para caminhada.,{base}/foto.webp,https://example.com/2,,",
        f"sim,esporte,Anúncio com imagem quebrada,O endereço da imagem não existe.,{base}/nao_existe.jpg,https://example.com/3,,",
        "sim,esporte,Anúncio sem imagem,Este anúncio não tem imagem.,,https://example.com/4,,",
        f"sim,parceiro,Faculdade Parceira Ficticia,Texto do anúncio do parceiro.,{base}/foto.webp,https://example.com/5,,",
    ]
    with open(os.path.join(pasta, "anuncios.csv"), "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas) + "\n")
    return f"{base}/anuncios.csv"


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
        '[data-testid="stApp"][data-test-script-state="notRunning"]', timeout=120000
    )
    pagina.wait_for_selector('[data-testid="stMainBlockContainer"] > div', timeout=120000)
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
               INSTAGRAM_NUTRI_DEMO="nutri.demo", DADOS_CSV=os.path.join(pasta, "dados_sono.csv"),
               ANUNCIOS_CSV_URL=servir_anuncios(pasta))
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

                # Cards clicáveis: clicar no ÍCONE do card (fora do botão) deve abrir as dicas.
                for chave, titulo in (("alimentacao", "Alimentação"), ("exercicios", "Caminhadas e exercícios")):
                    card = pagina.locator(f".st-key-cardtema_{chave}")
                    card.scroll_into_view_if_needed()
                    # Clique de mouse na posição do ícone (a camada do botão fica por cima
                    # dele de propósito, por isso não dá para "clicar no ícone" diretamente).
                    caixa = card.locator(".bolha-icone").bounding_box()
                    pagina.mouse.click(caixa["x"] + caixa["width"] / 2, caixa["y"] + caixa["height"] / 2)
                    esperar_tela(pagina)
                    abriu = pagina.locator(".hero-tema h1").first.inner_text().strip()
                    print(f"  clique no ícone do card '{titulo}' abriu: {abriu!r}")
                    fotografar(pagina, f"{tamanho}_1b_dicas_{chave}")
                    clicar(pagina, "⬅️ Voltar ao início")
                cursor = pagina.locator(".st-key-cardtema_sono").evaluate("e => getComputedStyle(e).cursor")
                print(f"  cursor sobre o card: {cursor}")
                pagina.locator(".st-key-cardtema_sono").scroll_into_view_if_needed()
                time.sleep(0.5)
                fotografar(pagina, f"{tamanho}_1a_cards")

                # Espaços de publicidade
                esporte = pagina.locator(".espaco-esporte")
                esporte.scroll_into_view_if_needed()
                time.sleep(1.5)
                imagens = pagina.locator(".anuncio").evaluate_all(
                    "els => els.map(e => e.querySelector('.anuncio-imagem') ? 'com imagem' : 'sem imagem')")
                print(f"  publicidade: {pagina.locator('.etiqueta-publicidade').count()} etiquetas | "
                      f"{pagina.locator('.espaco-esporte .anuncio').count()} anúncios de esporte | "
                      f"{pagina.locator('.espaco-parceiro .anuncio').count()} parceiro | imagens: {imagens}")
                fotografar(pagina, f"{tamanho}_1c_publicidade")

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
                contatos = pagina.locator(".botao-nutri")
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
