import base64
import os

import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

import ai_advisor
import analysis
import database
from database import carregar_dados, salvar_dados

load_dotenv()  # lê o arquivo .env, se existir, para carregar ANTHROPIC_API_KEY

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Análise de Sono, Cronotipo e Qualidade de Vida",
    page_icon="🌙",
    layout="wide",
)

BANNER_PATH = "assets/banner_home.png"

# ============================================================
# TIPOGRAFIA — toque "tech" em títulos e métricas, mantendo o
# corpo de texto em fonte legível. Aplicado uma vez, no topo.
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

    /* ===== VARIÁVEIS ===== */
    :root {
        --font-display: 'JetBrains Mono', monospace;
        --font-body:    'Inter', sans-serif;
        --accent:       #4f7f69;
        --accent-strong:#2d6a4f;
        --surface:      #ffffff;
        --bg:           #f8fafc;
        --border:       #e2e8f0;
        --text-main:    #1a1a2e;
        --text-soft:    #64748b;
        --shadow-soft:  0 1px 4px rgba(23,32,51,0.07), 0 4px 16px rgba(23,32,51,0.05);
    }

    /* ===== BASE ===== */
    html, body, [class*="css"] { font-family: var(--font-body); }
    .stApp, section[data-testid="stMain"] { background: var(--bg) !important; }

    /* ===== TÍTULOS ===== */
    h1 {
        font-family: var(--font-display) !important;
        font-size: clamp(1.6rem, 3.5vw, 2.4rem) !important;
        font-weight: 700 !important;
        color: var(--text-main) !important;
        letter-spacing: -0.03em;
    }
    h2 {
        font-family: var(--font-display) !important;
        font-size: clamp(1.2rem, 2.2vw, 1.65rem) !important;
        font-weight: 700 !important;
        color: var(--text-main) !important;
        letter-spacing: -0.02em;
    }
    h3 {
        font-family: var(--font-display) !important;
        font-size: clamp(1.08rem, 1.7vw, 1.35rem) !important;
        font-weight: 650 !important;
        color: var(--text-main) !important;
    }
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stCaptionContainer"] {
        color: var(--text-soft) !important;
        line-height: 1.65;
    }

    /* ===== CARDS DE MÉTRICAS ===== */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.92);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem 1.15rem;
        box-shadow: var(--shadow-soft);
        transition: box-shadow 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        box-shadow: 0 6px 20px rgba(23,32,51,0.12);
    }
    div[data-testid="stMetricValue"] {
        font-family: var(--font-display) !important;
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: var(--text-main) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-family: var(--font-body) !important;
        text-transform: uppercase;
        font-size: 0.72rem !important;
        letter-spacing: 0.08em;
        color: var(--text-soft) !important;
        font-weight: 700 !important;
    }

    /* ===== CAMPOS ===== */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stSelectbox"] > div > div {
        border-radius: 8px !important;
        border: 1px solid var(--border) !important;
        background: var(--surface) !important;
        font-family: var(--font-body) !important;
        color: var(--text-main) !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(79,127,105,0.16) !important;
    }

    /* ===== BOTÕES ===== */
    div[data-testid="stButton"] button {
        border-radius: 8px !important;
        font-family: var(--font-body) !important;
        font-weight: 700 !important;
        letter-spacing: 0;
        min-height: 2.8rem;
        transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease !important;
    }
    div[data-testid="stButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 24px rgba(23,32,51,0.12) !important;
        border-color: var(--accent) !important;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-strong), var(--accent)) !important;
        border-color: var(--accent-strong) !important;
    }

    /* ===== BARRA DE PROGRESSO ===== */
    div[data-testid="stProgressBar"] > div {
        border-radius: 999px !important;
        height: 7px !important;
        background: #e4eaf1 !important;
    }
    div[data-testid="stProgressBar"] > div > div {
        background: linear-gradient(90deg, var(--accent-strong), #8cb7a2) !important;
        border-radius: 999px !important;
    }

    /* ===== ALERTAS ===== */
    div[data-testid="stAlert"] {
        border-radius: 10px !important;
        border-left-width: 4px !important;
        font-family: var(--font-body) !important;
    }

    /* ===== DIVISOR ===== */
    hr {
        border-color: var(--border) !important;
        margin: 1.6rem 0 !important;
    }

    /* ===== BANNER HERO ===== */
    .hero-banner {
        border-radius: 12px !important;
        box-shadow: var(--shadow-soft);
    }
    .hero-banner-content h1 {
        font-family: var(--font-display) !important;
        font-size: clamp(2rem, 4vw, 3.2rem) !important;
        font-weight: 700 !important;
        color: var(--text-main) !important;
        letter-spacing: 0;
    }
    .hero-banner-content p {
        font-family: var(--font-body) !important;
        color: #344054 !important;
        font-size: 1.08rem !important;
        line-height: 1.65;
        max-width: 42rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)



def render_hero_banner(titulo: str, subtitulo: str) -> bool:
    """Mostra título e subtítulo sobrepostos à imagem de banner.

    Retorna True se a imagem foi encontrada e o banner foi renderizado,
    False caso contrário (nesse caso o chamador deve usar st.title normal).
    """
    if not os.path.exists(BANNER_PATH):
        return False

    with open(BANNER_PATH, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .hero-banner {{
            position: relative;
            background-image: url("data:image/png;base64,{img_b64}");
            background-size: cover;
            background-position: center;
            border-radius: 16px;
            padding: 56px 40px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .hero-banner::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(
                90deg,
                rgba(255,255,255,0.92) 0%,
                rgba(255,255,255,0.75) 35%,
                rgba(255,255,255,0.15) 70%,
                rgba(255,255,255,0) 100%
            );
            border-radius: 16px;
        }}
        .hero-banner-content {{
            position: relative;
            z-index: 2;
            max-width: 600px;
        }}
        .hero-banner-content h1 {{
            color: #2E2E2E;
            font-size: 2.1rem;
            margin: 0 0 12px 0;
        }}
        .hero-banner-content p {{
            color: #3a3a3a;
            font-size: 1.05rem;
            margin: 0;
        }}
        </style>
        <div class="hero-banner">
            <div class="hero-banner-content">
                <h1>{titulo}</h1>
                <p>{subtitulo}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return True

# Ordem das etapas do questionário, com nome legível e ícone para o mapa de progresso.
ETAPAS_QUESTIONARIO = [
    ("perfil", "👤 Perfil"),
    ("sono", "😴 Sono"),
    ("cronotipo", "🌅 Cronotipo"),
    ("alimentacao", "🍎 Alimentação"),
    ("bemestar", "✨ Bem-estar"),
    ("atividade", "🏃 Atividade"),
]
_CHAVES_ETAPAS = [chave for chave, _ in ETAPAS_QUESTIONARIO]

# ============================================================
# ESTADO INICIAL
# ============================================================
if "step" not in st.session_state:
    st.session_state.step = "home"
if "user_data" not in st.session_state:
    st.session_state.user_data = {}


def ir_para(etapa: str) -> None:
    st.session_state.step = etapa
    st.rerun()


def barra_progresso() -> None:
    """Mostra um mapa visual das etapas do questionário, destacando onde a
    pessoa está, o que já foi concluído e o que ainda falta."""
    if st.session_state.step not in _CHAVES_ETAPAS:
        return

    idx_atual = _CHAVES_ETAPAS.index(st.session_state.step)

    cols = st.columns(len(ETAPAS_QUESTIONARIO))
    for i, (_, label) in enumerate(ETAPAS_QUESTIONARIO):
        with cols[i]:
            if i < idx_atual:
                st.markdown(
                    f"<div style='text-align:center; color:#7A9E7E; font-size:0.85rem;'>"
                    f"✅<br>{label}</div>",
                    unsafe_allow_html=True,
                )
            elif i == idx_atual:
                st.markdown(
                    f"<div style='text-align:center; font-weight:700; color:#2E2E2E; font-size:0.85rem;'>"
                    f"🔵<br>{label}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='text-align:center; opacity:0.4; font-size:0.85rem;'>"
                    f"⚪<br>{label}</div>",
                    unsafe_allow_html=True,
                )

    st.progress((idx_atual + 1) / len(ETAPAS_QUESTIONARIO))
    st.caption(f"Etapa {idx_atual + 1} de {len(ETAPAS_QUESTIONARIO)} · faltam {len(ETAPAS_QUESTIONARIO) - idx_atual - 1}")


# ============================================================
# ETAPA: HOME
# ============================================================
def render_home():
    st.markdown(
        """
        <style>
        .home-actions {
            display: grid;
            grid-template-columns: minmax(260px, 0.9fr) minmax(280px, 1.7fr);
            gap: 1rem;
            margin: 1.75rem 0 1.25rem;
            align-items: stretch;
        }
        div[data-testid="stButton"] button {
            min-height: 3.35rem;
            border-radius: 12px !important;
            font-size: 1rem !important;
            font-weight: 800 !important;
            letter-spacing: 0;
        }
        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(135deg, #2f684f 0%, #4f9a73 54%, #f2a84a 100%) !important;
            color: #ffffff !important;
            border: 0 !important;
            box-shadow: 0 16px 32px rgba(47,104,79,0.28) !important;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover {
            filter: saturate(1.08) brightness(1.03);
            transform: translateY(-2px);
            box-shadow: 0 20px 38px rgba(47,104,79,0.34) !important;
        }
        div[data-testid="stButton"] button:not([kind="primary"]) {
            background: #ffffff !important;
            color: #25364d !important;
            border: 1px solid #cfd8e5 !important;
            box-shadow: 0 10px 24px rgba(23,32,51,0.07) !important;
        }
        div[data-testid="stButton"] button:not([kind="primary"]):hover {
            border-color: #4f7f69 !important;
            color: #2f684f !important;
            background: #f8fbf9 !important;
            transform: translateY(-2px);
        }
        .home-highlights {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin-top: 1.25rem;
        }
        .home-highlight {
            background: rgba(255,255,255,0.86);
            border: 1px solid #dce3ec;
            border-radius: 14px;
            padding: 1rem 1.05rem;
            box-shadow: 0 12px 26px rgba(23,32,51,0.07);
        }
        .home-highlight strong {
            display: block;
            color: #172033;
            font-size: 0.98rem;
            margin-bottom: 0.25rem;
        }
        .home-highlight span {
            color: #5f6b7a;
            font-size: 0.9rem;
            line-height: 1.45;
        }
        .hero-banner-content h1 {
            font-weight: 750 !important;
            letter-spacing: 0 !important;
            color: #15162b !important;
            text-shadow: 0 2px 14px rgba(255,255,255,0.78);
        }
        .hero-banner-content p {
            color: #3f536f !important;
            font-weight: 500;
            line-height: 1.65;
        }
        @media (max-width: 760px) {
            .home-actions, .home-highlights { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    tem_banner = render_hero_banner(
        "🌙 Análise de Sono, Cronotipo e Qualidade de Vida",
        "Responda algumas perguntas rápidas sobre seu sono, alimentação e bem-estar "
        "e descubra como seus hábitos impactam sua energia no dia a dia.",
    )
    if not tem_banner:
        st.title("🌙 Análise de Sono, Cronotipo e Qualidade de Vida")
        st.write(
            "Responda algumas perguntas rápidas sobre seu sono, alimentação e bem-estar "
            "e descubra como seus hábitos impactam sua energia no dia a dia."
        )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🚀 Começar Questionário", type="primary", use_container_width=True):
            ir_para("consentimento")
    with col2:
        if st.button("📊 Ver Dashboard dos Dados", use_container_width=True):
            ir_para("dashboard")

    st.markdown(
        """
        <div class="home-highlights">
            <div class="home-highlight">
                <strong>🌙 Sono e rotina</strong>
                <span>Mapeie horários, qualidade do sono e interrupções noturnas.</span>
            </div>
            <div class="home-highlight">
                <strong>⚡ Energia diária</strong>
                <span>Veja como alimentação, água e atividade física se conectam ao bem-estar.</span>
            </div>
            <div class="home-highlight">
                <strong>📈 Evolução visual</strong>
                <span>Acompanhe respostas coletadas em gráficos e indicadores simples.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ETAPA 1: PERFIL
# ============================================================
def _validar_email(email: str) -> bool:
    """Validação simples de formato de e-mail (não verifica existência real)."""
    email = email.strip()
    if not email or "@" not in email:
        return False
    usuario, _, dominio = email.partition("@")
    return bool(usuario) and "." in dominio and not dominio.startswith(".")


def render_perfil():
    barra_progresso()
    st.subheader("👤 Etapa 1: Dados Pessoais")

    nome = st.text_input("Nome", value=st.session_state.user_data.get("nome", ""))
    email = st.text_input(
        "E-mail",
        value=st.session_state.user_data.get("email", ""),
        help="Usamos seu e-mail apenas para reconhecer suas respostas anteriores "
             "e acompanhar sua evolução ao longo do tempo.",
    )
    idade = st.number_input("Idade", 18, 100, value=st.session_state.user_data.get("idade", 30))
    sexo = st.selectbox("Sexo", ["Feminino", "Masculino", "Outro", "Prefiro não dizer"])
    profissao = st.text_input("Profissão", value=st.session_state.user_data.get("profissao", ""))

    # Aviso de boas-vindas de volta, sem bloquear o preenchimento.
    email_valido = _validar_email(email)
    if email_valido and database.email_ja_respondeu(email):
        st.info("👋 Bem-vindo(a) de volta! Encontramos respostas suas anteriores.")

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Voltar"):
        ir_para("home")
    if col2.button("Próximo ➡️", type="primary"):
        if not nome.strip():
            st.warning("Por favor, preencha seu nome antes de continuar.")
        elif not email_valido:
            st.warning("Por favor, preencha um e-mail válido antes de continuar.")
        else:
            st.session_state.user_data.update({
                "nome": nome, "email": email.strip().lower(), "idade": idade,
                "sexo": sexo, "profissao": profissao,
            })
            ir_para("sono")


# ============================================================
# ETAPA 2: HÁBITOS DE SONO
# ============================================================
def render_sono():
    barra_progresso()
    st.subheader("😴 Etapa 2: Hábitos de Sono")

    col1, col2 = st.columns(2)
    with col1:
        hora_dormir = st.time_input("Horário que costuma dormir")
        hora_acordar = st.time_input("Horário que costuma acordar")
    with col2:
        horas_sono = st.slider("Horas de sono por noite", 0, 12, 7)
        qualidade = st.select_slider("Qualidade do sono", ["Ruim", "Regular", "Boa", "Excelente"])

    interrupcoes = st.slider("Quantas vezes você acorda durante a noite?", 0, 10, 0)

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Voltar"):
        ir_para("perfil")
    if col2.button("Próximo ➡️", type="primary"):
        st.session_state.user_data.update({
            "hora_dormir": str(hora_dormir),
            "hora_acordar": str(hora_acordar),
            "horas_sono": horas_sono,
            "qualidade_sono": qualidade,
            "interrupcoes_noturnas": interrupcoes,
        })
        ir_para("cronotipo")


# ============================================================
# ETAPA 3: CRONOTIPO
# ============================================================
def calcular_cronotipo(pontos: int) -> str:
    if pontos <= 3:
        return "Matutino"
    elif pontos <= 6:
        return "Intermediário"
    else:
        return "Vespertino"


def render_cronotipo():
    barra_progresso()
    st.subheader("🌅 Etapa 3: Cronotipo")
    st.caption("Essas perguntas ajudam a identificar se você é mais produtivo de manhã, à tarde ou à noite.")

    p1 = st.radio(
        "Se você pudesse escolher livremente, a que horas prefere acordar?",
        ["Antes das 6h", "Entre 6h e 8h", "Entre 8h e 10h", "Depois das 10h"],
    )
    p2 = st.radio(
        "Em que período você se sente mais alerta e produtivo?",
        ["Manhã (até 12h)", "Início da tarde (12h-17h)", "Fim da tarde/noite (17h-22h)", "Madrugada (depois das 22h)"],
    )
    p3 = st.radio(
        "Se tivesse uma prova difícil, em que horário preferiria fazê-la?",
        ["Logo de manhã", "Meio da manhã", "Tarde", "Noite"],
    )

    # Cada resposta vale 0-3 pontos (quanto mais tarde, mais pontos = mais vespertino)
    listas = [
        ["Antes das 6h", "Entre 6h e 8h", "Entre 8h e 10h", "Depois das 10h"],
        ["Manhã (até 12h)", "Início da tarde (12h-17h)", "Fim da tarde/noite (17h-22h)", "Madrugada (depois das 22h)"],
        ["Logo de manhã", "Meio da manhã", "Tarde", "Noite"],
    ]
    opcoes = [p1, p2, p3]
    pontos = sum(listas[i].index(opcoes[i]) for i in range(3))

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Voltar"):
        ir_para("sono")
    if col2.button("Próximo ➡️", type="primary"):
        cronotipo = calcular_cronotipo(pontos)
        st.session_state.user_data.update({
            "cronotipo_pontos": pontos,
            "cronotipo": cronotipo,
        })
        ir_para("alimentacao")


# ============================================================
# ETAPA 4: ALIMENTAÇÃO
# ============================================================
def render_alimentacao():
    barra_progresso()
    st.subheader("🍎 Etapa 4: Alimentação")

    col1, col2 = st.columns(2)
    with col1:
        frutas = st.slider("Porções de frutas/verduras por dia", 0, 10, 3)
        agua = st.slider("Litros de água por dia", 0.0, 5.0, 2.0, step=0.5)
    with col2:
        cafe = st.slider("Xícaras de café/cafeína por dia", 0, 10, 1)
        processados = st.slider("Frequência de alimentos processados (0=nunca, 10=sempre)", 0, 10, 5)

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Voltar"):
        ir_para("cronotipo")
    if col2.button("Próximo ➡️", type="primary"):
        st.session_state.user_data.update({
            "porcoes_frutas": frutas,
            "litros_agua": agua,
            "xicaras_cafe": cafe,
            "freq_processados": processados,
        })
        ir_para("bemestar")


# ============================================================
# ETAPA 5: BEM-ESTAR
# ============================================================
def render_bemestar():
    barra_progresso()
    st.subheader("✨ Etapa 5: Bem-estar")

    energia = st.slider("Nível de energia durante o dia (0-10)", 0, 10, 5)
    humor = st.slider("Como você avalia seu humor geral (0-10)", 0, 10, 5)
    produtividade = st.slider("Nível de produtividade (0-10)", 0, 10, 5)

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Voltar"):
        ir_para("alimentacao")
    if col2.button("Próximo ➡️", type="primary"):
        st.session_state.user_data.update({
            "energia": energia,
            "humor": humor,
            "produtividade": produtividade,
        })
        ir_para("atividade")


# ============================================================
# ETAPA 6: ATIVIDADE FÍSICA
# ============================================================
def render_atividade():
    barra_progresso()
    st.subheader("🏃 Etapa 6: Atividade Física e Estresse")

    exercicio = st.slider("Dias de exercício físico por semana", 0, 7, 2)
    minutos = st.slider("Minutos de exercício por sessão", 0, 180, 30, step=5)
    estresse = st.slider("Nível de estresse percebido (0=nenhum, 10=extremo)", 0, 10, 5)

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Voltar"):
        ir_para("bemestar")
    if col2.button("🎉 Finalizar", type="primary"):
        st.session_state.user_data.update({
            "dias_exercicio": exercicio,
            "minutos_exercicio": minutos,
            "nivel_estresse": estresse,
        })
        salvar_dados(st.session_state.user_data.copy())
        ir_para("resumo")


# ============================================================
# ETAPA: RESUMO / RELATÓRIO PERSONALIZADO
# ============================================================
# ============================================================
# CONTATO DA NUTRICIONISTA PARCEIRA
# ============================================================
# TODO: trocar pelos dados reais quando a parceria for confirmada.
# Número do WhatsApp no formato internacional, só números (ex: 5511999999999).
NUTRICIONISTA_WHATSAPP_NUMERO = "5511999999999"
NUTRICIONISTA_WHATSAPP_MENSAGEM = "Olá! Vi sua recomendação no app de Bem-Estar e gostaria de uma orientação nutricional."
NUTRICIONISTA_INSTAGRAM_USUARIO = "sua_nutricionista"  # sem o @


def render_contato_nutricionista() -> None:
    """Mostra botões de contato com a nutricionista parceira (WhatsApp e Instagram),
    com as cores características de cada rede social."""
    import urllib.parse

    mensagem_codificada = urllib.parse.quote(NUTRICIONISTA_WHATSAPP_MENSAGEM)
    link_whatsapp = f"https://wa.me/{NUTRICIONISTA_WHATSAPP_NUMERO}?text={mensagem_codificada}"
    link_instagram = f"https://instagram.com/{NUTRICIONISTA_INSTAGRAM_USUARIO}"

    st.markdown(
        """
        <style>
        .botao-contato {
            display: block;
            text-align: center;
            padding: 0.6rem 1rem;
            border-radius: 8px;
            text-decoration: none !important;
            font-weight: 600;
            font-size: 0.95rem;
            font-family: 'Inter', sans-serif;
            transition: opacity 0.15s ease;
        }
        .botao-contato:hover { opacity: 0.88; }
        .botao-whatsapp { background-color: #25D366; color: white !important; }
        .botao-instagram {
            background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Quer uma orientação alimentar personalizada de verdade? Fale com nossa nutricionista parceira:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f'<a href="{link_whatsapp}" target="_blank" class="botao-contato botao-whatsapp">'
            f'💬 WhatsApp da Nutricionista</a>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<a href="{link_instagram}" target="_blank" class="botao-contato botao-instagram">'
            f'📸 Instagram da Nutricionista</a>',
            unsafe_allow_html=True,
        )


def gerar_dicas(dados: dict) -> list:
    dicas = []
    if dados.get("horas_sono", 7) < 6:
        dicas.append("😴 Você está dormindo pouco. Tente aumentar gradualmente para 7-8h por noite.")
    if dados.get("porcoes_frutas", 0) < 3:
        dicas.append("🍎 Considere aumentar o consumo de frutas e verduras para mais energia.")
    if dados.get("litros_agua", 0) < 1.5:
        dicas.append("💧 Sua hidratação está abaixo do recomendado. Tente beber mais água ao longo do dia.")
    if dados.get("dias_exercicio", 0) < 3:
        dicas.append("🏃 Poucos dias de exercício na semana. Mesmo caminhadas curtas já fazem diferença.")
    if dados.get("nivel_estresse", 0) >= 7:
        dicas.append("🧘 Seu nível de estresse está alto. Técnicas de respiração ou meditação podem ajudar.")
    if dados.get("xicaras_cafe", 0) >= 5:
        dicas.append("☕ Consumo elevado de cafeína pode estar afetando a qualidade do seu sono.")
    if not dicas:
        dicas.append("🌟 Seus hábitos estão equilibrados! Continue assim.")
    return dicas


def render_resumo():
    st.balloons()
    dados = st.session_state.user_data
    st.title("🎉 Seu Relatório Personalizado")
    st.write(f"Obrigado, **{dados.get('nome', '')}**! Aqui está o seu resumo:")

    indice = analysis.calcular_indice_bem_estar(dados)
    classificacao = analysis.classificar_indice_bem_estar(indice)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Horas de sono", f"{dados.get('horas_sono', '-')}h")
    col2.metric("Cronotipo", dados.get("cronotipo", "-"))
    col3.metric("Nível de energia", f"{dados.get('energia', '-')}/10")
    col4.metric(
        "Índice de Bem-Estar",
        f"{indice}/100",
        help="Combina sono, água, exercício, frutas, estresse, energia e humor. "
             "É um índice próprio deste projeto, não uma medida clínica validada.",
    )
    st.caption(f"Classificação: **{classificacao}**")

    st.subheader("💡 Dicas personalizadas")
    for dica in gerar_dicas(dados):
        st.info(dica)

    st.subheader("🍽️ Dica de Alimentação")
    if ai_advisor.ia_disponivel():
        with st.spinner("Gerando uma dica personalizada..."):
            periodo = ai_advisor.periodo_do_dia_atual()
            dica_ia = ai_advisor.gerar_dica_alimentacao_ia(
                cronotipo=dados.get("cronotipo", "Intermediário"),
                nivel_estresse=dados.get("nivel_estresse", 5),
                periodo=periodo,
                porcoes_frutas=dados.get("porcoes_frutas"),
            )
        if dica_ia:
            st.success(dica_ia)
        else:
            st.info(
                "🍎 Prefira refeições leves e bem distribuídas ao longo do dia, "
                "priorizando frutas, verduras e bastante água. "
                "Para orientação alimentar específica, consulte um nutricionista."
            )
    else:
        st.info(
            "🍎 Prefira refeições leves e bem distribuídas ao longo do dia, "
            "priorizando frutas, verduras e bastante água. "
            "Para orientação alimentar específica, consulte um nutricionista."
        )

    render_contato_nutricionista()

    col1, col2 = st.columns(2)
    if col1.button("📊 Ver Dashboard Geral"):
        ir_para("dashboard")
    if col2.button("🏠 Voltar ao início"):
        st.session_state.user_data = {}
        ir_para("home")


# ============================================================
# DASHBOARD
# ============================================================
def render_dashboard():
    st.title("📊 Dashboard - Visão Geral dos Dados Coletados")

    if st.button("⬅️ Voltar ao início"):
        ir_para("home")

    df = carregar_dados()

    if df.empty:
        st.warning("Ainda não há dados coletados. Responda o questionário primeiro!")
        return

    # Avisa se alguma linha tem dado numérico inválido (virou NaN na validação)
    linhas_com_problema = df[df.isna().any(axis=1)]
    if not linhas_com_problema.empty:
        st.info(
            f"⚠️ {len(linhas_com_problema)} resposta(s) têm algum valor inválido e "
            "podem não aparecer em todos os gráficos."
        )

    # ------------------------------------------------------------
    # Cartões de indicadores
    # ------------------------------------------------------------
    resumo = analysis.gerar_resumo_estatistico(df) if analysis.amostra_suficiente(df) else []
    significativos = [r for r in resumo if r["significativo"]]

    indices_bem_estar = df.apply(lambda linha: analysis.calcular_indice_bem_estar(linha.to_dict()), axis=1)
    indice_medio = round(indices_bem_estar.mean(), 1) if len(indices_bem_estar) > 0 else None

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de participantes", len(df))
    col2.metric("Análises realizadas", len(resumo))
    col3.metric("Resultados significativos", len(significativos))
    if indice_medio is not None:
        col4.metric(
            "Índice de Bem-Estar médio",
            f"{indice_medio}/100",
            help="Combina sono, água, exercício, frutas, estresse, energia e humor. "
                 "É um índice próprio deste projeto, não uma medida clínica validada.",
        )

    st.divider()

    # ------------------------------------------------------------
    # Insights descritivos (seguros mesmo com poucos dados)
    # ------------------------------------------------------------
    st.subheader("💡 Insights")
    insights = analysis.gerar_insights_descritivos(df)
    if insights:
        for insight in insights:
            st.write(insight)
    else:
        st.caption("Ainda não há dados suficientes para gerar insights.")

    st.divider()

    # ------------------------------------------------------------
    # Análise estatística (regressões, com aviso de amostra mínima)
    # ------------------------------------------------------------
    st.subheader("📈 Análise Estatística")

    if not analysis.amostra_suficiente(df):
        st.warning(
            f"São necessárias pelo menos {analysis.AMOSTRA_MINIMA} respostas para gerar "
            f"análises estatísticas confiáveis (atualmente há {len(df)}). "
            "Com poucos dados, qualquer relação encontrada seria pouco confiável "
            "— continue coletando respostas para liberar essa seção."
        )
    elif not resumo:
        st.info("Não há pares de variáveis suficientes para análise no momento.")
    else:
        if significativos:
            st.write(f"**{len(significativos)} relação(ões) com evidência estatística (p < 0.05):**")
            for r in significativos:
                st.success(f"**{r['forca']}** · {analysis.interpretar_resultado(r)}")
        else:
            st.write(
                "Nenhuma das relações testadas mostrou evidência estatística "
                "significativa até agora (todas com p ≥ 0.05). Isso é esperado com "
                "amostras pequenas — não significa que as relações não existam."
            )

        with st.expander("Ver todos os resultados testados, incluindo os não significativos"):
            for r in resumo:
                selo = "✅ significativo" if r["significativo"] else "⏳ ainda não confirmado"
                st.write(f"**{r['rotulo']}** — correlação {r['forca'].lower()} ({selo})")
                st.caption(analysis.interpretar_resultado(r))

    st.divider()

    # ------------------------------------------------------------
    # Gráficos
    # ------------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribuição de Cronotipos")
        if "cronotipo" in df.columns:
            fig = px.pie(df, names="cronotipo", hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Horas de Sono vs Energia")
        if "horas_sono" in df.columns and "energia" in df.columns:
            fig = px.scatter(df, x="horas_sono", y="energia", color="cronotipo",
                              trendline="ols",
                              color_discrete_sequence=px.colors.qualitative.Pastel,
                              labels={"horas_sono": "Horas de sono", "energia": "Energia (0-10)"})
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Porções de Frutas vs Energia")
        if "porcoes_frutas" in df.columns and "energia" in df.columns:
            fig = px.scatter(df, x="porcoes_frutas", y="energia",
                              trendline="ols",
                              color_discrete_sequence=["#9b8cf2"],
                              labels={"porcoes_frutas": "Porções de frutas/dia", "energia": "Energia (0-10)"})
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Dias de Exercício vs Estresse")
        if "dias_exercicio" in df.columns and "nivel_estresse" in df.columns:
            fig = px.scatter(df, x="dias_exercicio", y="nivel_estresse",
                              trendline="ols",
                              color_discrete_sequence=["#f4a261"],
                              labels={"dias_exercicio": "Dias de exercício/semana", "nivel_estresse": "Estresse (0-10)"})
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Estresse vs Qualidade do Sono")
    if "nivel_estresse" in df.columns and "qualidade_sono" in df.columns:
        fig = px.box(df, x="qualidade_sono", y="nivel_estresse",
                     color="qualidade_sono",
                     category_orders={"qualidade_sono": ["Ruim", "Regular", "Boa", "Excelente"]},
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Dados brutos")
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Baixar CSV completo",
        df.to_csv(index=False).encode("utf-8"),
        file_name="dados_sono.csv",
        mime="text/csv",
    )


# ============================================================
# ROTEAMENTO PRINCIPAL
# ============================================================
def render_consentimento():
    """Tela de consentimento obrigatória antes do questionário.
    Exibida uma vez por sessão, quando o usuário clica em 'Começar Questionário'."""
    st.title("📋 Termo de Consentimento")
    st.markdown(
        """
        Antes de começar, leia com atenção:

        **O que coletamos**
        Nome, e-mail, idade, sexo, profissão e informações sobre seus hábitos de sono,
        alimentação, atividade física e bem-estar geral.

        **Como usamos**
        Seus dados são utilizados exclusivamente para gerar seu relatório personalizado
        e alimentar análises estatísticas agregadas (sem identificação individual)
        que ajudam a melhorar o sistema.

        **Quem tem acesso**
        Somente os responsáveis pela plataforma e, se aplicável, o profissional de
        saúde que te convidou a participar. Seus dados não são vendidos ou
        compartilhados com terceiros.

        **Seus direitos (LGPD)**
        Você pode solicitar a exclusão dos seus dados a qualquer momento pelo
        e-mail de contato disponível nesta plataforma.

        **Armazenamento**
        Os dados são armazenados em servidor seguro e protegido.

        **Importante**
        As dicas geradas por este sistema são de caráter **educativo e informativo**,
        e **não substituem consulta com nutricionista, médico ou outro profissional de saúde**.
        """
    )

    st.divider()
    aceite = st.checkbox(
        "Li e concordo com os termos acima e autorizo o uso dos meus dados conforme descrito."
    )

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Voltar", use_container_width=True):
        ir_para("home")
    if col2.button(
        "✅ Concordo e quero continuar",
        type="primary",
        use_container_width=True,
        disabled=not aceite,
    ):
        st.session_state["consentimento_aceito"] = True
        ir_para("perfil")


ROTAS = {
    "home": render_home,
    "consentimento": render_consentimento,
    "perfil": render_perfil,
    "sono": render_sono,
    "cronotipo": render_cronotipo,
    "alimentacao": render_alimentacao,
    "bemestar": render_bemestar,
    "atividade": render_atividade,
    "resumo": render_resumo,
    "dashboard": render_dashboard,
}

ROTAS[st.session_state.step]()