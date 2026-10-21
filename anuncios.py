"""
Espaços de publicidade ("Esporte" e "Parceiro").

Os anúncios vêm de uma planilha do Google Sheets publicada como CSV. O
endereço fica na variável ANUNCIOS_CSV_URL (Secrets do Streamlit Cloud ou
.env). Colunas da planilha (veja anuncios_modelo.csv):

    ativo       sim / não
    espaco      esporte / parceiro
    titulo      título do anúncio
    descricao   texto curto
    imagem_url  endereço direto de uma imagem (opcional)
    link        para onde o anúncio leva
    data_inicio primeiro dia em que aparece (opcional, AAAA-MM-DD ou DD/MM/AAAA)
    data_fim    último dia em que aparece (opcional)

A planilha é lida no máximo a cada 10 minutos (cache). Se ela falhar ou
estiver em formato errado, os espaços simplesmente não aparecem e o
motivo fica registrado no log; o app continua funcionando.
"""

import io
import logging
import os
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

COLUNAS = ["ativo", "espaco", "titulo", "descricao", "imagem_url", "link", "data_inicio", "data_fim"]
ESPACOS = ("esporte", "parceiro")
TEMPO_CACHE_SEGUNDOS = 10 * 60
TIMEOUT_SEGUNDOS = 8

# Horário de Brasília (o Brasil não tem mais horário de verão). O servidor
# do Streamlit Cloud usa UTC, e sem isso um anúncio "virava o dia" às 21h.
FUSO_BRASILIA = timezone(timedelta(hours=-3))


def _sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def _link_seguro(url: str) -> str:
    """Aceita só endereços http(s); qualquer outra coisa (ex: "javascript:") vira vazio."""
    url = (url or "").strip()
    return url if url.lower().startswith(("https://", "http://")) else ""


def _data(valor: str) -> date | None:
    """Lê datas como 2026-10-31 ou 31/10/2026. Vazio ou inválido = sem limite."""
    valor = (valor or "").strip()
    if not valor:
        return None
    formatos = ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%Y/%m/%d")
    for formato in formatos:
        try:
            return datetime.strptime(valor, formato).date()
        except ValueError:
            continue
    logger.warning("Anúncios: data inválida %r (use AAAA-MM-DD ou DD/MM/AAAA); ignorada.", valor)
    return None


def hoje() -> date:
    return datetime.now(FUSO_BRASILIA).date()


def filtrar_anuncios(df: pd.DataFrame, dia: date) -> dict[str, list[dict]]:
    """Separa os anúncios válidos por espaço: só ativos, dentro do período,
    com título e link seguro."""
    resultado = {espaco: [] for espaco in ESPACOS}
    for linha in df.to_dict("records"):
        ativo = _sem_acento(str(linha.get("ativo", ""))).strip().lower()
        espaco = _sem_acento(str(linha.get("espaco", ""))).strip().lower()
        titulo = str(linha.get("titulo", "")).strip()
        link = _link_seguro(str(linha.get("link", "")))
        if ativo not in ("sim", "s", "x", "1", "true", "yes") or espaco not in ESPACOS:
            continue
        if not titulo or not link:
            logger.warning("Anúncios: linha %r ignorada (sem título ou com link inválido).", titulo)
            continue
        inicio, fim = _data(str(linha.get("data_inicio", ""))), _data(str(linha.get("data_fim", "")))
        if (inicio and dia < inicio) or (fim and dia > fim):
            continue
        resultado[espaco].append({
            "titulo": titulo,
            "descricao": str(linha.get("descricao", "")).strip(),
            "imagem_url": _link_seguro(str(linha.get("imagem_url", ""))),
            "link": link,
        })
    return resultado


@st.cache_data(ttl=TEMPO_CACHE_SEGUNDOS, show_spinner=False)
def _baixar_planilha(url: str) -> pd.DataFrame | None:
    """Baixa e lê o CSV publicado. Retorna None se algo der errado."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SEGUNDOS) as resposta:
            conteudo = resposta.read()
        df = pd.read_csv(io.BytesIO(conteudo), dtype=str, keep_default_na=False)
    except Exception as erro:  # rede, endereço errado, arquivo que não é CSV...
        logger.warning("Anúncios: não foi possível ler a planilha (%s: %s).", type(erro).__name__, erro)
        return None

    df.columns = [_sem_acento(str(c)).strip().lower() for c in df.columns]
    faltando = [c for c in COLUNAS if c not in df.columns]
    if faltando:
        logger.warning("Anúncios: faltam colunas na planilha: %s.", ", ".join(faltando))
        return None
    return df


def carregar_anuncios() -> dict[str, list[dict]]:
    """Anúncios que devem aparecer hoje, por espaço. Vazio se não houver
    planilha configurada ou se ela falhar."""
    url = os.environ.get("ANUNCIOS_CSV_URL", "").strip()
    if not url:
        return {espaco: [] for espaco in ESPACOS}
    df = _baixar_planilha(url)
    if df is None:
        return {espaco: [] for espaco in ESPACOS}
    return filtrar_anuncios(df, hoje())
