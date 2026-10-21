"""
Link de convite de cada nutricionista: endereço com ?nutri=codigo,
mensagem para compartilhar no WhatsApp e QR Code para imprimir.

Quem abre o app pelo link de uma nutricionista tem as respostas salvas
com o código dela (coluna nutricionista_id) e só aparece no painel dela.
"""

import io
import os
from pathlib import Path
from urllib.parse import quote, urlsplit

import qrcode
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


def endereco_do_app() -> str:
    """Endereço base do app, sem caminho nem parâmetros.

    Usa a variável APP_URL se existir (útil se o app tiver domínio próprio);
    senão, descobre pelo endereço que o navegador está usando agora.
    """
    url = os.environ.get("APP_URL") or st.context.url or ""
    partes = urlsplit(url)
    if not partes.scheme or not partes.netloc:
        return ""
    return f"{partes.scheme}://{partes.netloc}"


def link_da_nutricionista(codigo: str) -> str:
    return f"{endereco_do_app()}/?nutri={codigo}"


def link_compartilhar_whatsapp(nome: str, link: str) -> str:
    """Abre o WhatsApp com uma mensagem pronta (a nutricionista escolhe o contato)."""
    mensagem = (
        f"Olá! Sou {nome}, sua nutricionista. Responda este questionário rápido "
        f"sobre sono, alimentação e bem-estar (leva uns 3 minutos): {link}"
    )
    return f"https://wa.me/?text={quote(mensagem)}"


def link_whatsapp_paciente(numero: str, nome: str) -> str:
    """Conversa no WhatsApp da nutricionista, com uma mensagem pronta do paciente."""
    mensagem = (
        f"Olá, {nome}! Vim pelo app de Bem-Estar e respondi o questionário. "
        "Gostaria de conversar sobre uma orientação nutricional."
    )
    return f"https://wa.me/{numero}?text={quote(mensagem)}"


def link_instagram(usuario: str) -> str:
    return f"https://www.instagram.com/{usuario}/"


# Fonte do cartão do QR Code. A fonte padrão do Pillow não tem acentos
# ("Questionário" sairia "Question?rio"), por isso o projeto inclui a
# Poppins (licença SIL Open Font License, em assets/fontes/OFL.txt).
FONTE_CARTAO = Path(__file__).resolve().parent / "assets" / "fontes" / "Poppins-SemiBold.ttf"


def _fonte(tamanho: int):
    try:
        return ImageFont.truetype(str(FONTE_CARTAO), tamanho)
    except OSError:  # arquivo da fonte ausente: usa a padrão (sem acentos)
        return ImageFont.load_default(size=tamanho)


@st.cache_data
def qr_code_png(link: str, nome: str) -> bytes:
    """Gera um cartão em PNG com o QR Code do link e o nome da nutricionista,
    pronto para baixar e imprimir."""
    qr = qrcode.QRCode(box_size=12, border=3, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(link)
    qr.make(fit=True)
    imagem_qr = qr.make_image(fill_color="#0B3B3A", back_color="white").convert("RGB")

    # Cartão um pouco mais largo que o QR Code, com o QR centralizado.
    lado_qr = imagem_qr.width
    largura = max(lado_qr + 120, 600)
    margem = 30
    cartao = Image.new("RGB", (largura, lado_qr + 150), "white")
    cartao.paste(imagem_qr, ((largura - lado_qr) // 2, 0))
    desenho = ImageDraw.Draw(cartao)
    for texto, tamanho, y in (
        ("Questionário de bem-estar", 34, lado_qr + 6),
        (f"Nutricionista: {nome}", 28, lado_qr + 56),
        ("Aponte a câmera do celular para responder", 22, lado_qr + 104),
    ):
        # Diminui a letra até o texto caber (nomes longos não saem do cartão).
        fonte = _fonte(tamanho)
        while tamanho > 12 and desenho.textlength(texto, font=fonte) > largura - 2 * margem:
            tamanho -= 1
            fonte = _fonte(tamanho)
        x = (largura - desenho.textlength(texto, font=fonte)) / 2
        desenho.text((x, y), texto, fill="#0B3B3A", font=fonte)

    saida = io.BytesIO()
    cartao.save(saida, format="PNG")
    return saida.getvalue()
