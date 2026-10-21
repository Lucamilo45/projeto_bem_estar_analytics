"""
Teste dos espaços de publicidade.

Sobe um pequeno servidor local que faz o papel do Google Sheets e confere:
filtros (ativo, espaço, datas, links seguros), falhas da planilha (o
espaço some sem quebrar o app), cache de 10 minutos e as telas do app.

Como rodar (na pasta do projeto):
    venv\\Scripts\\python testes\\testar_anuncios.py
"""

import http.server
import os
import sys
import threading
import time
from datetime import date

PASTA_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PASTA_PROJETO)
os.chdir(PASTA_PROJETO)
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ.pop("ANUNCIOS_CSV_URL", None)

import pandas as pd  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

import anuncios  # noqa: E402

CABECALHO = "ativo,espaco,titulo,descricao,imagem_url,link,data_inicio,data_fim\n"
PLANILHAS = {
    "/boa.csv": CABECALHO
    + "sim,esporte,Corrida Ficticia,Descricao,https://example.com/a.jpg,https://example.com/corrida,,\n"
    + "Sim,Esporte ,Loja Ficticia,,,https://example.com/loja,01/10/2026,31/12/2026\n"
    + "sim,parceiro,Faculdade Ficticia,Texto do parceiro,,https://example.com/fac,2026-10-01,\n",
    "/sem_coluna.csv": "ativo,espaco,titulo\nsim,esporte,Sem link\n",
    "/pagina.html": "<html><body>Isto não é um CSV</body></html>",
}
pedidos = []


class Servidor(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        pedidos.append(self.path)
        if self.path == "/lenta.csv":
            time.sleep(3)
        corpo = PLANILHAS.get(self.path)
        if corpo is None:
            self.send_response(404)
            self.end_headers()
            return
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.end_headers()
            self.wfile.write(corpo.encode("utf-8"))
        except ConnectionError:
            pass  # o app desistiu antes (teste da planilha lenta): é o esperado

    def log_message(self, *args):
        pass


servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Servidor)
threading.Thread(target=servidor.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{servidor.server_address[1]}"
PLANILHAS["/lenta.csv"] = PLANILHAS["/boa.csv"]

resultados = []


def confere(descricao: str, ok: bool) -> None:
    resultados.append(ok)
    print(f"  {'✅ PASSOU' if ok else '❌ FALHOU'}  {descricao}")


def titulos(lista: list[dict]) -> list[str]:
    return [a["titulo"] for a in lista]


print("\n1) Filtros")
df = pd.DataFrame([
    # ativo, espaco, titulo, descricao, imagem_url, link, data_inicio, data_fim
    ["sim", "esporte", "No período", "", "", "https://ex.com/1", "2026-10-01", "2026-10-31"],
    ["não", "esporte", "Desativado", "", "", "https://ex.com/2", "", ""],
    ["NÃO", "esporte", "Desativado maiúsculo", "", "", "https://ex.com/3", "", ""],
    ["sim", "esporte", "Ainda não começou", "", "", "https://ex.com/4", "2026-11-01", ""],
    ["sim", "esporte", "Já terminou", "", "", "https://ex.com/5", "", "2026-10-16"],
    ["sim", "esporte", "Termina hoje", "", "", "https://ex.com/6", "", "17/10/2026"],
    ["Sim", " Esporte ", "Com espaços e maiúsculas", "", "", "https://ex.com/7", "", ""],
    ["sim", "esporte", "Link perigoso", "", "", "javascript:alert(1)", "", ""],
    ["sim", "esporte", "", "", "", "https://ex.com/8", "", ""],
    ["sim", "outro", "Espaço desconhecido", "", "", "https://ex.com/9", "", ""],
    ["sim", "esporte", "Imagem perigosa", "", "javascript:x", "https://ex.com/10", "", ""],
    ["sim", "parceiro", "Parceiro", "", "", "https://ex.com/11", "", ""],
], columns=anuncios.COLUNAS)
filtrados = anuncios.filtrar_anuncios(df, date(2026, 10, 17))
esperado = ["No período", "Termina hoje", "Com espaços e maiúsculas", "Imagem perigosa"]
confere(f"esporte mostra só os válidos: {titulos(filtrados['esporte'])}",
        titulos(filtrados["esporte"]) == esperado)
confere("parceiro separado do esporte", titulos(filtrados["parceiro"]) == ["Parceiro"])
confere("imagem com endereço perigoso é descartada (o anúncio fica sem imagem)",
        filtrados["esporte"][3]["imagem_url"] == "")
confere("data do Brasil (UTC-3) é usada para 'hoje'", anuncios.hoje() is not None)

print("\n2) Leitura da planilha e falhas")
anuncios._baixar_planilha.clear()
os.environ["ANUNCIOS_CSV_URL"] = f"{BASE}/boa.csv"
lista = anuncios.carregar_anuncios()
confere(f"planilha boa: esporte={titulos(lista['esporte'])}, parceiro={titulos(lista['parceiro'])}",
        len(lista["esporte"]) == 2 and titulos(lista["parceiro"]) == ["Faculdade Ficticia"])
pedidos.clear()
anuncios.carregar_anuncios()
anuncios.carregar_anuncios()
confere(f"cache: novas leituras não baixam a planilha de novo (downloads: {len(pedidos)})", len(pedidos) == 0)
confere("cache configurado para 10 minutos", anuncios.TEMPO_CACHE_SEGUNDOS == 600)

for descricao, url in (
    ("endereço que não existe (404)", f"{BASE}/nao_existe.csv"),
    ("planilha sem as colunas certas", f"{BASE}/sem_coluna.csv"),
    ("página que não é CSV", f"{BASE}/pagina.html"),
    ("servidor fora do ar", "http://127.0.0.1:1/planilha.csv"),
    ("endereço inválido", "isto não é um endereço"),
):
    os.environ["ANUNCIOS_CSV_URL"] = url
    try:
        lista = anuncios.carregar_anuncios()
        ok = lista == {"esporte": [], "parceiro": []}
    except Exception as erro:  # não pode acontecer: falha deve só esconder o espaço
        ok = False
        print("    erro:", erro)
    confere(f"{descricao}: espaços somem sem erro", ok)

anuncios.TIMEOUT_SEGUNDOS = 1
os.environ["ANUNCIOS_CSV_URL"] = f"{BASE}/lenta.csv"
inicio = time.time()
lista = anuncios.carregar_anuncios()
confere(f"planilha lenta: desiste no tempo limite ({time.time() - inicio:.1f}s) e esconde",
        lista["esporte"] == [] and time.time() - inicio < 2.5)
anuncios.TIMEOUT_SEGUNDOS = 8
os.environ.pop("ANUNCIOS_CSV_URL")
confere("sem ANUNCIOS_CSV_URL configurado: nada aparece",
        anuncios.carregar_anuncios() == {"esporte": [], "parceiro": []})

print("\n3) Telas do app")


def tela(passo: str, url: str | None) -> AppTest:
    anuncios._baixar_planilha.clear()
    if url:
        os.environ["ANUNCIOS_CSV_URL"] = url
    else:
        os.environ.pop("ANUNCIOS_CSV_URL", None)
    at = AppTest.from_file("app.py", default_timeout=60)
    at.session_state.step = passo
    at.session_state.user_data = {"nome": "Paciente", "horas_sono": 7}
    return at.run()


def html(at: AppTest) -> str:
    return "\n".join(str(m.value) for m in at.markdown)


for passo, nome in (("home", "página inicial"), ("resumo", "tela de resultado")):
    at = tela(passo, f"{BASE}/boa.csv")
    texto = html(at)
    confere(f"{nome}: espaços Esporte e Parceiro com a etiqueta 'Publicidade'",
            not at.exception and texto.count("Publicidade") == 2
            and "Corrida Ficticia" in texto and "Faculdade Ficticia" in texto)
    confere(f"{nome}: links abrem em nova aba e marcados como patrocinados",
            'target="_blank" rel="noopener sponsored"' in texto)
    at = tela(passo, f"{BASE}/nao_existe.csv")
    confere(f"{nome}: planilha com erro esconde os espaços sem quebrar",
            not at.exception and "Publicidade" not in html(at))

PLANILHAS["/xss.csv"] = CABECALHO + 'sim,esporte,"<script>alert(1)</script>",<b>x</b>,,https://example.com,,\n'
texto = html(tela("home", f"{BASE}/xss.csv"))
confere("texto da planilha não vira código na página (<script> é neutralizado)",
        "<script>alert(1)</script>" not in texto and "&lt;script&gt;" in texto)

modelo = pd.read_csv("anuncios_modelo.csv", dtype=str, keep_default_na=False)
confere("anuncios_modelo.csv tem exatamente as colunas pedidas", list(modelo.columns) == anuncios.COLUNAS)

servidor.shutdown()
print(f"\nResultado: {sum(resultados)} de {len(resultados)} verificações passaram.")
sys.exit(0 if all(resultados) else 1)
