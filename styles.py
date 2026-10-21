"""
Identidade visual do app: fontes, cores de cada página e componentes
reutilizáveis (cards, cartões de recomendação, barra de progresso).

Todo o CSS fica aqui para que app.py cuide só do conteúdo das telas.
Cada página tem a sua paleta (PALETAS) e chama aplicar_tema(pagina)
logo no início. Os gráficos do Plotly usam a paleta da mesma página
através de cores_graficos(pagina) e estilizar_grafico(fig, pagina).

Contraste: todas as combinações de texto/fundo e texto branco sobre a
cor principal foram conferidas com contraste mínimo de 4.5 (WCAG AA).
"""

from html import escape
from urllib.parse import quote

import streamlit as st

# ============================================================
# PALETAS POR PÁGINA
# ============================================================
PALETAS = {
    # Início: coral, amarelo e turquesa (energia, boas-vindas).
    # Botões com texto grande e negrito: coral e turquesa têm contraste
    # acima de 3 com o branco (mínimo WCAG para texto grande).
    "inicio": {
        "principal": "#EF4F4F",
        "principal_hover": "#D93C3C",
        "secundario": "#0D9488",
        "secundario_hover": "#0F766E",
        "apoio": "#E11D48",
        "degrade": "linear-gradient(135deg, #FF6B6B 0%, #FF9F43 100%)",
        "fundo": "#FFF7F2",
        # Fundo da página: degradê suave + "bolhas" decorativas arredondadas.
        "fundo_decorado": (
            "radial-gradient(circle at 8% 12%, rgba(255,107,107,0.22) 0 120px, transparent 121px),"
            "radial-gradient(circle at 92% 8%, rgba(45,212,191,0.22) 0 150px, transparent 151px),"
            "radial-gradient(circle at 85% 88%, rgba(250,204,21,0.25) 0 110px, transparent 111px),"
            "radial-gradient(circle at 4% 80%, rgba(45,212,191,0.16) 0 80px, transparent 81px),"
            "radial-gradient(circle at 50% 100%, rgba(255,159,67,0.14) 0 140px, transparent 141px),"
            "linear-gradient(135deg, #FFE4E1 0%, #FFF7D6 50%, #D9F7F2 100%)"
        ),
        "superficie": "#FFFFFF",
        "texto": "#3B1D14",
        "texto_suave": "#7C4A3A",
        "borda": "#FED7C3",
        "graficos": ["#FF6B6B", "#FF9F43", "#FDBA74", "#E11D48", "#C2410C"],
    },
    # Questionário: roxo e lilás (calma, foco)
    "questionario": {
        "principal": "#7C3AED",
        "principal_hover": "#6D28D9",
        "apoio": "#C4B5FD",
        "degrade": "linear-gradient(135deg, #7C3AED 0%, #C084FC 100%)",
        "fundo": "#FAF7FF",
        "superficie": "#FFFFFF",
        "texto": "#2E1065",
        "texto_suave": "#5B4B8A",
        "borda": "#E4D9FF",
        "graficos": ["#7C3AED", "#C084FC", "#A78BFA", "#C026D3", "#6D28D9"],
    },
    # Dashboard: azul-turquesa e verde-água (clareza, dados)
    "dashboard": {
        "principal": "#0F766E",
        "principal_hover": "#115E59",
        "apoio": "#2DD4BF",
        "degrade": "linear-gradient(135deg, #14B8A6 0%, #5EEAD4 100%)",
        "fundo": "#F2FBFA",
        "superficie": "#FFFFFF",
        "texto": "#0B3B3A",
        "texto_suave": "#3D6B68",
        "borda": "#C7EDE8",
        "graficos": ["#0D9488", "#06B6D4", "#10B981", "#3B82F6", "#5EEAD4"],
        # Uma cor por card de indicador (todas com texto branco legível)
        "cards": ["#0F766E", "#0E7490", "#047857", "#1D4ED8"],
    },
    # Resultado / dicas da IA: amarelo e rosa (alegria, conquista)
    "resultado": {
        "principal": "#BE185D",
        "principal_hover": "#9D174D",
        "apoio": "#FACC15",
        "degrade": "linear-gradient(135deg, #FEF08A 0%, #FBCFE8 100%)",
        "fundo": "#FFFBEB",
        "superficie": "#FFFFFF",
        "texto": "#4A1030",
        "texto_suave": "#7A3A58",
        "borda": "#FBD5E5",
        "graficos": ["#EC4899", "#FACC15", "#FB923C", "#BE185D", "#F9A8D4"],
        "cards": ["#BE185D", "#A21CAF", "#C2410C", "#9D174D"],
    },
}

# Cards coloridos da página inicial: (fundo claro, cor do texto/destaque).
# Texto escuro sobre fundo claro, todos com contraste acima de 5.8.
CORES_CARDS_INICIO = {
    "rosa": ("#FCE7F3", "#9D174D"),
    "amarelo": ("#FEF9C3", "#854D0E"),
    "verde_agua": ("#CCFBF1", "#115E59"),
    "roxo": ("#EDE9FE", "#5B21B6"),
}

# Cores da barra de progresso do questionário: uma por etapa, do roxo ao magenta.
CORES_ETAPAS = ["#6D28D9", "#7C3AED", "#8B5CF6", "#A855F7", "#C026D3", "#DB2777"]

_FONTES = (
    "https://fonts.googleapis.com/css2?"
    "family=Poppins:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap"
)


# ============================================================
# TEMA DA PÁGINA
# ============================================================
def aplicar_tema(pagina: str) -> None:
    """Aplica fontes, cores e estilo dos componentes para a página informada
    ("inicio", "questionario", "dashboard" ou "resultado")."""
    p = PALETAS[pagina]
    fundo_pagina = p.get("fundo_decorado", p["fundo"])

    # Páginas com cor "secundario" (Início) têm os botões secundários
    # também preenchidos, com texto branco.
    css_secundario = ""
    if "secundario" in p:
        css_secundario = f"""
        /* Texto de 1.2rem em negrito conta como "texto grande" (WCAG),
           o que garante leitura confortável nos botões coloridos. */
        div[data-testid="stButton"] button {{ min-height: 3.6rem; }}
        div[data-testid="stButton"] button p {{ font-size: 1.2rem !important; }}
        div[data-testid="stButton"] button:not([kind="primary"]) {{
            background: {p["secundario"]} !important;
            color: #FFFFFF !important;
            border: 0 !important;
            box-shadow: 0 8px 20px color-mix(in srgb, {p["secundario"]} 30%, transparent) !important;
        }}
        div[data-testid="stButton"] button:not([kind="primary"]):hover {{
            background: {p["secundario_hover"]} !important;
            color: #FFFFFF !important;
            box-shadow: var(--sombra-forte) !important;
        }}
        """

    st.markdown(
        f"""
        <style>
        @import url('{_FONTES}');

        :root {{
            --principal: {p["principal"]};
            --principal-hover: {p["principal_hover"]};
            --apoio: {p["apoio"]};
            --degrade: {p["degrade"]};
            --fundo: {p["fundo"]};
            --superficie: {p["superficie"]};
            --texto: {p["texto"]};
            --texto-suave: {p["texto_suave"]};
            --borda: {p["borda"]};
            --raio: 20px;
            --sombra: 0 4px 14px rgba(30, 20, 60, 0.06), 0 12px 32px rgba(30, 20, 60, 0.06);
            --sombra-forte: 0 10px 28px rgba(30, 20, 60, 0.14);
            --fonte-titulo: 'Poppins', sans-serif;
            --fonte-texto: 'Inter', sans-serif;
        }}

        /* ===== BASE ===== */
        html, body, .stApp, [class*="css"] {{ font-family: var(--fonte-texto); }}
        .stApp {{ background: {fundo_pagina} !important; background-attachment: fixed !important; }}
        section[data-testid="stMain"] {{ background: transparent !important; }}
        /* Barra do topo semitransparente: mostra o fundo colorido, mas o
           texto que rola por baixo dela não se mistura com os botões */
        header[data-testid="stHeader"] {{
            background: rgba(255, 255, 255, 0.55) !important;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }}
        /* Espaço no topo para o conteúdo não ficar atrás da barra do Streamlit */
        .block-container {{ padding-top: 4.5rem; max-width: 1150px; }}

        /* Esconde o ícone de link (corrente) que o Streamlit põe ao lado dos títulos */
        [data-testid="stHeaderActionElements"],
        h1 a[href^="#"], h2 a[href^="#"], h3 a[href^="#"] {{ display: none !important; }}

        /* ===== TÍTULOS ===== */
        h1, h2, h3 {{
            font-family: var(--fonte-titulo) !important;
            color: var(--texto) !important;
            letter-spacing: -0.01em;
        }}
        h1 {{ font-size: clamp(1.8rem, 4vw, 2.6rem) !important; font-weight: 800 !important; }}
        h2 {{ font-size: clamp(1.4rem, 3vw, 1.9rem) !important; font-weight: 700 !important; }}
        h3 {{ font-size: clamp(1.15rem, 2.4vw, 1.4rem) !important; font-weight: 700 !important; }}

        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li,
        div[data-testid="stCaptionContainer"],
        label, .stRadio label, .stSlider label {{
            color: var(--texto) !important;
            line-height: 1.65;
        }}
        div[data-testid="stCaptionContainer"] {{ color: var(--texto-suave) !important; }}

        /* ===== CAMPOS ===== */
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] > div > div {{
            border-radius: 14px !important;
            border: 1.5px solid var(--borda) !important;
            background: var(--superficie) !important;
            color: var(--texto) !important;
        }}
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stNumberInput"] input:focus {{
            border-color: var(--principal) !important;
            box-shadow: 0 0 0 3px color-mix(in srgb, var(--principal) 20%, transparent) !important;
        }}
        div[data-testid="stSlider"] div[role="slider"] {{ background: var(--principal) !important; }}

        /* ===== BOTÕES ===== */
        div[data-testid="stButton"] button,
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stDownloadButton"] button {{
            border-radius: 14px !important;
            font-family: var(--fonte-texto) !important;
            font-weight: 700 !important;
            min-height: 3rem;
            padding: 0.55rem 1.3rem !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease !important;
        }}
        div[data-testid="stButton"] button[kind="primary"],
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stDownloadButton"] button {{
            background: var(--principal) !important;
            border: 0 !important;
            color: #FFFFFF !important;
            box-shadow: 0 8px 20px color-mix(in srgb, var(--principal) 30%, transparent) !important;
        }}
        div[data-testid="stButton"] button[kind="primary"]:hover,
        div[data-testid="stFormSubmitButton"] button:hover,
        div[data-testid="stDownloadButton"] button:hover {{
            background: var(--principal-hover) !important;
            transform: translateY(-2px);
            box-shadow: var(--sombra-forte) !important;
        }}
        div[data-testid="stButton"] button:not([kind="primary"]) {{
            background: var(--superficie) !important;
            color: var(--principal) !important;
            border: 2px solid var(--borda) !important;
        }}
        div[data-testid="stButton"] button:not([kind="primary"]):hover {{
            border-color: var(--principal) !important;
            transform: translateY(-2px);
        }}
        div[data-testid="stButton"] button p,
        div[data-testid="stFormSubmitButton"] button p,
        div[data-testid="stDownloadButton"] button p {{
            color: inherit !important;
            font-weight: 700 !important;
        }}

        /* ===== ALERTAS E CAIXAS ===== */
        div[data-testid="stAlert"] {{ border-radius: 16px !important; }}
        div[data-testid="stExpander"] details {{
            border-radius: var(--raio) !important;
            border: 1.5px solid var(--borda) !important;
            background: var(--superficie);
        }}
        div[data-testid="stForm"] {{
            border-radius: var(--raio) !important;
            border: 1.5px solid var(--borda) !important;
            background: var(--superficie);
            box-shadow: var(--sombra);
            padding: 1.4rem;
        }}
        hr {{ border-color: var(--borda) !important; margin: 1.8rem 0 !important; }}

        /* ===== COMPONENTES PRÓPRIOS ===== */
        .hero {{
            background: var(--degrade);
            border-radius: var(--raio);
            padding: clamp(1.8rem, 5vw, 3.2rem);
            box-shadow: var(--sombra-forte);
            margin-bottom: 1.6rem;
        }}
        .hero .hero-icone {{ font-size: clamp(2.6rem, 7vw, 3.6rem); line-height: 1; }}
        .hero h1 {{ color: #FFFFFF !important; margin: 0.6rem 0 0.4rem; }}
        .hero p {{
            color: #FFFFFF !important;
            font-size: clamp(1rem, 2.2vw, 1.15rem);
            font-weight: 500;
            max-width: 40rem;
            margin: 0;
        }}
        .hero.hero-claro h1, .hero.hero-claro p {{ color: var(--texto) !important; }}

        .grade-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 1rem;
            margin: 0.6rem 0 1.4rem;
        }}
        .card {{
            background: var(--superficie);
            border: 1.5px solid var(--borda);
            border-radius: var(--raio);
            padding: 1.2rem 1.3rem;
            box-shadow: var(--sombra);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .card:hover {{ transform: translateY(-3px); box-shadow: var(--sombra-forte); }}
        .card .card-icone {{ font-size: 2.2rem; line-height: 1; margin-bottom: 0.5rem; }}
        .card strong {{
            display: block;
            font-family: var(--fonte-titulo);
            font-size: 1.05rem;
            color: var(--texto);
            margin-bottom: 0.25rem;
        }}
        .card span {{ color: var(--texto-suave); font-size: 0.95rem; line-height: 1.5; }}

        .card-indicador {{ border: 0; color: #FFFFFF; }}
        .card-indicador .card-rotulo {{
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #FFFFFF;
            opacity: 0.95;
        }}
        .card-indicador .card-valor {{
            font-family: var(--fonte-titulo);
            font-size: clamp(1.7rem, 4vw, 2.2rem);
            font-weight: 800;
            color: #FFFFFF;
            line-height: 1.2;
            margin-top: 0.2rem;
        }}
        .card-indicador .card-detalhe {{ color: #FFFFFF; font-size: 0.86rem; opacity: 0.95; }}

        .cartao-recomendacao {{
            background: var(--degrade);
            border-radius: var(--raio);
            padding: 1.3rem 1.5rem;
            box-shadow: var(--sombra);
            display: flex;
            gap: 1rem;
            align-items: flex-start;
            margin-bottom: 0.9rem;
        }}
        .cartao-recomendacao .card-icone {{ font-size: 2.4rem; line-height: 1; }}
        .cartao-recomendacao strong {{
            display: block;
            font-family: var(--fonte-titulo);
            font-size: 1.1rem;
            color: var(--texto);
            margin-bottom: 0.3rem;
        }}
        .cartao-recomendacao p {{ color: var(--texto) !important; margin: 0; line-height: 1.6; }}

        .progresso-etapas {{ display: flex; gap: 0.4rem; margin: 0.4rem 0 0.6rem; }}
        .progresso-etapas .segmento {{ flex: 1; height: 10px; border-radius: 999px; background: #E9E3F7; }}
        .progresso-rotulos {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 0.4rem;
            text-align: center;
            font-size: 0.82rem;
            color: var(--texto-suave);
        }}
        .progresso-rotulos .atual {{ font-weight: 700; color: var(--texto); }}

        /* ===== PÁGINA INICIAL ===== */
        .home-selo {{
            display: inline-block;
            background: #FFFFFF;
            color: var(--principal-hover);
            font-weight: 700;
            font-size: 0.9rem;
            padding: 0.35rem 0.9rem;
            border-radius: 999px;
            box-shadow: var(--sombra);
            margin-bottom: 0.9rem;
        }}
        .home-titulo {{
            font-family: var(--fonte-titulo) !important;
            font-weight: 800 !important;
            font-size: clamp(2rem, 4.2vw, 3.1rem) !important;
            line-height: 1.12 !important;
            color: var(--texto) !important;
            margin: 0 0 0.8rem !important;
            padding: 0 !important;
        }}
        .home-titulo .destaque {{
            background: linear-gradient(90deg, #EF4F4F, #F59E0B 55%, #0D9488);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }}
        .home-subtitulo {{
            font-size: clamp(1.02rem, 1.8vw, 1.18rem);
            color: var(--texto-suave);
            line-height: 1.65;
            margin-bottom: 1.4rem;
        }}
        .home-ilustracao {{
            display: block;
            width: 100%;
            height: auto;
            box-sizing: border-box;
            border-radius: 28px;
            box-shadow: 0 18px 40px rgba(239, 79, 79, 0.18), 0 6px 16px rgba(13, 148, 136, 0.12);
            border: 6px solid #FFFFFF;
        }}

        .home-selo-convite {{ margin-right: 0.5rem; color: #0B7A61; }}

        /* ===== CARDS CLICÁVEIS (página inicial) =====
           Cada card é um st.container(key="cardtema_...") com um botão dentro.
           O ::after do botão se estica sobre o card inteiro: clicar em
           qualquer parte do card equivale a clicar no botão. */
        [class*="st-key-cardtema_"] {{
            position: relative;
            border-radius: var(--raio);
            padding: 1.4rem 1.3rem 1.2rem;
            box-shadow: var(--sombra);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            cursor: pointer;
            margin-top: 1.4rem;
        }}
        [class*="st-key-cardtema_"]:hover {{ transform: translateY(-4px); box-shadow: var(--sombra-forte); }}
        [class*="st-key-cardtema_"] [data-testid="stElementContainer"],
        [class*="st-key-cardtema_"] [data-testid="stButton"],
        [class*="st-key-cardtema_"] [data-testid="stButton"] button {{ position: static !important; }}
        [class*="st-key-cardtema_"] [data-testid="stButton"] button,
        [class*="st-key-cardtema_"] [data-testid="stButton"] button:hover {{
            transform: none !important;  /* sem isso a área clicável "pula" no hover */
            min-height: 2.8rem !important;
        }}
        [class*="st-key-cardtema_"] [data-testid="stButton"] button p {{ font-size: 1rem !important; }}
        [class*="st-key-cardtema_"] [data-testid="stButton"] button::after {{
            content: "";
            position: absolute;
            inset: 0;
            border-radius: var(--raio);
        }}
        /* Mesma altura em todos os cards, para os botões ficarem alinhados */
        .card-clicavel-conteudo {{ min-height: 15rem; }}
        .card-clicavel-conteudo .bolha-icone {{
            width: 64px; height: 64px;
            border-radius: 50%;
            background: #FFFFFF;
            display: flex; align-items: center; justify-content: center;
            font-size: 2.2rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 6px 14px rgba(0, 0, 0, 0.06);
        }}
        .card-clicavel-conteudo strong {{
            display: block;
            font-family: var(--fonte-titulo);
            font-size: 1.12rem;
            margin-bottom: 0.3rem;
        }}
        .card-clicavel-conteudo span {{ font-size: 0.96rem; line-height: 1.5; }}

        /* ===== CARTÃO "SUA NUTRICIONISTA" (para o paciente) ===== */
        .nutri-cta {{
            background: #FFFFFF;
            border: 1.5px solid #E2E8F0;
            border-radius: var(--raio);
            box-shadow: var(--sombra);
            padding: 1.4rem 1.5rem 1.5rem;
            margin: 1.2rem 0 1.6rem;
        }}
        .nutri-cta-topo {{ display: flex; align-items: center; gap: 1rem; margin-bottom: 0.9rem; }}
        .nutri-avatar {{
            width: 64px; height: 64px; flex-shrink: 0;
            border-radius: 50%;
            background: linear-gradient(135deg, #0B7A61, #833AB4);
            color: #FFFFFF;
            font-family: var(--fonte-titulo);
            font-weight: 800;
            font-size: 1.45rem;
            display: flex; align-items: center; justify-content: center;
        }}
        .nutri-cta-topo small {{
            display: block;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #475569;
        }}
        .nutri-cta-topo strong {{ font-family: var(--fonte-titulo); font-size: 1.35rem; color: #1F2937; }}
        .nutri-cta p {{ color: #334155 !important; margin: 0 0 1rem; }}
        .botoes-nutri {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 0.9rem;
        }}
        .botao-nutri {{
            display: flex; align-items: center; justify-content: center; gap: 0.6rem;
            min-height: 64px;
            padding: 0.9rem 1.2rem;
            border-radius: 18px;
            font-size: 1.15rem;
            font-weight: 800;
            color: #FFFFFF !important;
            text-decoration: none !important;
            box-shadow: var(--sombra);
            transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
        }}
        .botao-nutri:hover {{ transform: translateY(-3px); box-shadow: var(--sombra-forte); }}
        .botao-nutri .icone {{ font-size: 1.5rem; line-height: 1; }}
        .botao-nutri-whatsapp {{ background: #0B7A61; }}
        .botao-nutri-whatsapp:hover {{ background: #075E54; }}
        .botao-nutri-instagram {{ background: linear-gradient(45deg, #C13584, #833AB4); }}
        .botao-nutri-instagram:hover {{ background: linear-gradient(45deg, #A62C70, #6E2F99); }}

        /* ===== ESPAÇOS DE PUBLICIDADE ===== */
        .espaco-anuncio {{ margin: 2.2rem 0 1rem; }}
        .espaco-cabecalho {{ display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.7rem; flex-wrap: wrap; }}
        .espaco-cabecalho h3 {{ margin: 0 !important; font-size: 1.25rem !important; }}
        .etiqueta-publicidade {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            background: #E2E8F0;
            color: #334155;
            border-radius: 999px;
            padding: 0.2rem 0.65rem;
        }}
        .dica-carrossel {{ font-size: 0.85rem; color: var(--texto-suave); margin-left: auto; }}
        .carrossel {{
            display: flex;
            gap: 1rem;
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            padding: 0.2rem 0.2rem 0.8rem;
        }}
        .anuncio {{
            flex: 0 0 calc((100% - 2rem) / 3);
            min-width: 240px;
            scroll-snap-align: start;
            display: flex;
            flex-direction: column;
            background: #FFFFFF;
            border: 1.5px solid #E2E8F0;
            border-radius: var(--raio);
            overflow: hidden;
            box-shadow: var(--sombra);
            text-decoration: none !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .anuncio:hover {{ transform: translateY(-3px); box-shadow: var(--sombra-forte); }}
        .anuncio-imagem {{
            width: 100%;
            aspect-ratio: 16 / 9;
            background-color: #F1F5F9;
            background-size: cover;
            background-position: center;
        }}
        .anuncio .corpo {{ padding: 1rem 1.1rem 1.1rem; display: flex; flex-direction: column; gap: 0.35rem; flex: 1; }}
        .anuncio strong {{ font-family: var(--fonte-titulo); font-size: 1.05rem; color: #1F2937; }}
        .anuncio span {{ color: #475569; font-size: 0.93rem; line-height: 1.5; }}
        .anuncio .chamada {{ margin-top: auto; padding-top: 0.4rem; font-weight: 700; color: #0F766E; }}
        .anuncio-parceiro {{ flex-direction: row; }}
        .anuncio-parceiro .anuncio-imagem {{ width: 42%; flex-shrink: 0; aspect-ratio: auto; min-height: 200px; }}
        .anuncio-parceiro .corpo {{ padding: 1.4rem 1.6rem; justify-content: center; }}
        .anuncio-parceiro strong {{ font-size: 1.3rem; }}

        /* ===== PÁGINAS DE DICAS ===== */
        .hero-tema {{
            border-radius: var(--raio);
            padding: clamp(1.5rem, 4vw, 2.6rem);
            box-shadow: var(--sombra-forte);
            margin-bottom: 1.4rem;
        }}
        .hero-tema .hero-icone {{ font-size: clamp(2.6rem, 7vw, 3.6rem); line-height: 1; }}
        .hero-tema h1 {{ margin: 0.5rem 0 0.4rem; color: inherit !important; }}
        .hero-tema p {{ margin: 0; font-size: clamp(1rem, 2.2vw, 1.15rem); max-width: 46rem; color: inherit !important; }}
        .grade-dicas {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin-bottom: 1.4rem;
        }}
        .secao-dicas {{
            background: #FFFFFF;
            border-radius: var(--raio);
            border-left: 8px solid;
            padding: 1.2rem 1.4rem;
            box-shadow: var(--sombra);
        }}
        .secao-dicas h3 {{ margin: 0 0 0.6rem !important; font-size: 1.2rem !important; color: inherit !important; }}
        .secao-dicas ul {{ margin: 0; padding-left: 1.2rem; }}
        .secao-dicas li {{ color: #2B2B2B; line-height: 1.6; margin-bottom: 0.35rem; }}
        .aviso-dicas {{
            background: #FFFFFF;
            border: 2px dashed;
            border-radius: var(--raio);
            padding: 1rem 1.3rem;
            margin-bottom: 1.4rem;
            font-weight: 600;
        }}

        /* ===== CONTATO E CONVITE DA NUTRICIONISTA ===== */
        .botao-contato {{
            display: block;
            text-align: center;
            padding: 0.8rem 1rem;
            border-radius: 14px;
            text-decoration: none !important;
            font-weight: 700;
            font-size: 1rem;
            color: #FFFFFF !important;
            box-shadow: var(--sombra);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .botao-contato:hover {{ transform: translateY(-2px); box-shadow: var(--sombra-forte); }}
        .botao-qr {{ background: #0E7490; margin-top: 0.8rem; }}
        .qr-convite {{
            display: block;
            width: 100%;
            max-width: 260px;
            margin: 0 auto;
            border-radius: var(--raio);
            border: 1.5px solid var(--borda);
            box-shadow: var(--sombra);
        }}
        div[data-testid="stLinkButton"] a {{
            background: #0B7A61 !important;
            color: #FFFFFF !important;
            border: 0 !important;
            border-radius: 14px !important;
            min-height: 3rem;
            font-weight: 700 !important;
        }}
        div[data-testid="stLinkButton"] a p {{ color: #FFFFFF !important; font-weight: 700 !important; }}
        div[data-testid="stLinkButton"] a:hover {{ background: #075E54 !important; }}

        {css_secundario}

        /* ===== CELULAR ===== */
        @media (max-width: 640px) {{
            .block-container {{ padding: 4rem 1rem 2rem; }}
            .progresso-rotulos {{ display: none; }}
            .cartao-recomendacao {{ flex-direction: column; gap: 0.5rem; }}
            .home-ilustracao {{ border-radius: 20px; border-width: 4px; }}
            .card-clicavel-conteudo {{ min-height: 0; }}
            .anuncio {{ flex-basis: 85%; }}
            .anuncio-parceiro {{ flex-direction: column; }}
            .anuncio-parceiro .anuncio-imagem {{ width: 100%; aspect-ratio: 16 / 9; min-height: 0; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# COMPONENTES
# ============================================================
def hero(icone: str, titulo: str, subtitulo: str, claro: bool = False) -> None:
    """Faixa de destaque no topo da página, com o degradê da página.
    Use claro=True quando o degradê for claro (texto escuro em vez de branco)."""
    classe = "hero hero-claro" if claro else "hero"
    st.markdown(
        f'<div class="{classe}"><div class="hero-icone">{icone}</div>'
        f"<h1>{escape(titulo)}</h1><p>{escape(subtitulo)}</p></div>",
        unsafe_allow_html=True,
    )


def card_clicavel(chave: str, cor: str, icone: str, titulo: str, texto: str) -> bool:
    """Card colorido da página inicial que funciona como botão.
    Retorna True quando a pessoa clica em qualquer parte do card."""
    fundo, tinta = CORES_CARDS_INICIO[cor]
    with st.container(key=f"cardtema_{chave}"):
        st.markdown(
            f"""
            <style>
            .st-key-cardtema_{chave} {{ background: {fundo}; }}
            .st-key-cardtema_{chave} div[data-testid="stButton"] button:not([kind="primary"]) {{
                background: {tinta} !important;
                color: #FFFFFF !important;
            }}
            </style>
            <div class="card-clicavel-conteudo" style="color:{tinta};">
                <div class="bolha-icone">{icone}</div>
                <strong style="color:{tinta};">{escape(titulo)}</strong>
                <span style="color:{tinta};">{escape(texto)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return st.button("Ver dicas →", key=f"btn_tema_{chave}", width="stretch")


def cartao_nutricionista(nome: str, link_whatsapp: str, link_instagram: str) -> None:
    """Cartão "Sua nutricionista" com botões grandes de WhatsApp e Instagram.
    Botões sem link (contato não cadastrado) não aparecem."""
    iniciais = "".join(parte[0] for parte in nome.split()[:2]).upper() or "N"
    botoes = ""
    if link_whatsapp:
        botoes += (
            f'<a class="botao-nutri botao-nutri-whatsapp" href="{escape(link_whatsapp, quote=True)}" '
            'target="_blank" rel="noopener"><span class="icone">💬</span>Falar no WhatsApp</a>'
        )
    if link_instagram:
        botoes += (
            f'<a class="botao-nutri botao-nutri-instagram" href="{escape(link_instagram, quote=True)}" '
            'target="_blank" rel="noopener"><span class="icone">📸</span>Seguir no Instagram</a>'
        )
    st.markdown(
        f'<div class="nutri-cta"><div class="nutri-cta-topo">'
        f'<div class="nutri-avatar" aria-hidden="true">{escape(iniciais)}</div>'
        f"<div><small>Sua nutricionista</small><strong>{escape(nome)}</strong></div></div>"
        "<p>Quer uma orientação alimentar feita para você? Converse com sua nutricionista "
        "e acompanhe as dicas no Instagram.</p>"
        f'<div class="botoes-nutri">{botoes}</div></div>',
        unsafe_allow_html=True,
    )


# Caracteres que podem ficar como estão num endereço dentro de url('...').
_URL_SEGURA = ":/?#[]@!$&*+,;=%-._~"


def _anuncio_html(anuncio: dict, classe: str) -> str:
    # A imagem vira fundo de um quadro (e não uma tag <img>): se o endereço
    # estiver errado, aparece só o fundo claro, sem o ícone de imagem quebrada.
    # quote() codifica aspas, parênteses e espaços, que quebrariam o url(...).
    imagem = (
        '<div class="anuncio-imagem" aria-hidden="true" '
        f"style=\"background-image:url('{quote(anuncio['imagem_url'], safe=_URL_SEGURA)}');\"></div>"
        if anuncio["imagem_url"] else ""
    )
    descricao = f'<span>{escape(anuncio["descricao"])}</span>' if anuncio["descricao"] else ""
    return (
        f'<a class="{classe}" href="{escape(anuncio["link"], quote=True)}" target="_blank" '
        f'rel="noopener sponsored">{imagem}<div class="corpo">'
        f'<strong>{escape(anuncio["titulo"])}</strong>{descricao}'
        f'<div class="chamada">Saiba mais →</div></div></a>'
    )


def espaco_anuncios(espaco: str, anuncios: list[dict]) -> None:
    """Espaço de publicidade com a etiqueta "Publicidade". Não mostra nada se
    não houver anúncios. "esporte" vira um carrossel de cards; "parceiro"
    mostra um banner horizontal (o primeiro anúncio ativo)."""
    if not anuncios:
        return
    if espaco == "esporte":
        titulo = "🏃 Esporte"
        dica = '<span class="dica-carrossel">arraste para ver mais →</span>' if len(anuncios) > 3 else ""
        conteudo = '<div class="carrossel">' + "".join(_anuncio_html(a, "anuncio") for a in anuncios) + "</div>"
    else:
        titulo = "🎓 Parceiro"
        dica = ""
        conteudo = _anuncio_html(anuncios[0], "anuncio anuncio-parceiro")
    st.markdown(
        f'<div class="espaco-anuncio espaco-{espaco}"><div class="espaco-cabecalho">'
        f'<h3>{titulo}</h3><span class="etiqueta-publicidade">Publicidade</span>{dica}</div>'
        f"{conteudo}</div>",
        unsafe_allow_html=True,
    )


def pagina_dicas(tema: dict, aviso: str) -> None:
    """Monta a página de dicas de um tema, com as cores do tema."""
    fundo, tinta = CORES_CARDS_INICIO[tema["cor"]]
    secoes = "".join(
        f'<div class="secao-dicas" style="border-left-color:{tinta}; color:{tinta};">'
        f"<h3>{icone} {escape(titulo)}</h3><ul>"
        + "".join(f"<li>{escape(item)}</li>" for item in itens)
        + "</ul></div>"
        for icone, titulo, itens in tema["secoes"]
    )
    st.markdown(
        f'<div class="hero-tema" style="background:{fundo}; color:{tinta};">'
        f'<div class="hero-icone">{tema["icone"]}</div>'
        f'<h1>{escape(tema["titulo"])}</h1><p>{escape(tema["introducao"])}</p></div>'
        f'<div class="grade-dicas">{secoes}</div>'
        f'<div class="aviso-dicas" style="border-color:{tinta}; color:{tinta};">'
        f"🩺 {escape(aviso)}</div>",
        unsafe_allow_html=True,
    )


def cards_indicadores(itens: list[tuple[str, str, str, str]], pagina: str) -> None:
    """Grade de cards coloridos com (ícone, rótulo, valor, detalhe).
    Cada card recebe uma cor diferente da paleta da página."""
    p = PALETAS[pagina]
    cores = p.get("cards", [p["principal"]])
    html = "".join(
        f'<div class="card card-indicador" style="background:{cores[i % len(cores)]};">'
        f'<div class="card-icone">{icone}</div>'
        f'<div class="card-rotulo">{escape(rotulo)}</div>'
        f'<div class="card-valor">{escape(valor)}</div>'
        f'<div class="card-detalhe">{escape(detalhe)}</div></div>'
        for i, (icone, rotulo, valor, detalhe) in enumerate(itens)
    )
    st.markdown(f'<div class="grade-cards">{html}</div>', unsafe_allow_html=True)


def cartao_recomendacao(icone: str, titulo: str, texto: str) -> None:
    """Cartão com o degradê da página, para dicas e recomendações.
    O texto é escapado: pode vir da IA ou de dados digitados pela pessoa."""
    st.markdown(
        f'<div class="cartao-recomendacao"><div class="card-icone">{icone}</div>'
        f"<div><strong>{escape(titulo)}</strong><p>{escape(texto)}</p></div></div>",
        unsafe_allow_html=True,
    )


def progresso_etapas(etapas: list[str], indice_atual: int) -> None:
    """Barra de progresso do questionário: cada etapa concluída ou atual
    fica com a sua cor; as próximas ficam cinza-lilás."""
    segmentos = "".join(
        f'<div class="segmento" style="background:{CORES_ETAPAS[i % len(CORES_ETAPAS)]};"></div>'
        if i <= indice_atual else '<div class="segmento"></div>'
        for i in range(len(etapas))
    )
    rotulos = "".join(
        f'<div class="{"atual" if i == indice_atual else ""}">'
        f'{"✅ " if i < indice_atual else ""}{escape(nome)}</div>'
        for i, nome in enumerate(etapas)
    )
    st.markdown(
        f'<div class="progresso-etapas">{segmentos}</div>'
        f'<div class="progresso-rotulos">{rotulos}</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# GRÁFICOS (PLOTLY)
# ============================================================
def cores_graficos(pagina: str) -> list[str]:
    """Sequência de cores dos gráficos da página."""
    return PALETAS[pagina]["graficos"]


def estilizar_grafico(fig, pagina: str):
    """Aplica fontes, cores e fundo transparente da página a um gráfico Plotly."""
    p = PALETAS[pagina]
    fig.update_layout(
        colorway=p["graficos"],
        font=dict(family="Inter, sans-serif", color=p["texto"], size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
    )
    fig.update_xaxes(gridcolor=p["borda"], zeroline=False)
    fig.update_yaxes(gridcolor=p["borda"], zeroline=False)
    return fig
