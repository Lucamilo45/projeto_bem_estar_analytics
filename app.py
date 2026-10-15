import os
import time

import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

import ai_advisor
import analysis
import auth
import database
import styles
from database import salvar_dados

load_dotenv()  # lê o arquivo .env, se existir (chave da IA e senhas das nutricionistas)

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Análise de Sono, Cronotipo e Qualidade de Vida",
    page_icon="🌙",
    layout="wide",
)

# Ilustração da página inicial. A versão .webp (95 KB) é uma cópia leve do
# banner_home.png original (1,6 MB), para carregar rápido no celular.
BANNER_PATH = "assets/banner_home.webp"

# O visual (fontes, cores de cada página, cards) fica em styles.py.
# O tema certo é aplicado no roteamento, no final deste arquivo.

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

# Nutricionista que convidou a pessoa, lida do link (ex: ...?nutri=ana).
# Só é aceita se existir uma senha configurada para esse código; assim
# um link digitado errado não liga respostas a uma nutricionista que não existe.
if "nutricionista_id" not in st.session_state:
    codigo_link = auth.normalizar_codigo(st.query_params.get("nutri"))
    st.session_state.nutricionista_id = codigo_link if auth.nutricionista_existe(codigo_link) else ""


def ir_para(etapa: str) -> None:
    st.session_state.step = etapa
    st.rerun()


def barra_progresso() -> None:
    """Mostra a barra de progresso do questionário, com uma cor por etapa,
    destacando onde a pessoa está e quanto falta."""
    if st.session_state.step not in _CHAVES_ETAPAS:
        return

    idx_atual = _CHAVES_ETAPAS.index(st.session_state.step)
    styles.progresso_etapas([rotulo for _, rotulo in ETAPAS_QUESTIONARIO], idx_atual)
    faltam = len(ETAPAS_QUESTIONARIO) - idx_atual - 1
    st.caption(
        f"Etapa {idx_atual + 1} de {len(ETAPAS_QUESTIONARIO)} · "
        + ("última etapa! 🎉" if faltam == 0 else f"falta{'m' if faltam > 1 else ''} {faltam}")
    )


# ============================================================
# ETAPA: HOME
# ============================================================
def render_home():
    # Texto à esquerda e ilustração à direita; no celular as colunas
    # empilham e o título aparece acima da imagem.
    col_texto, col_imagem = st.columns([1, 1.45], gap="large", vertical_alignment="center")

    with col_texto:
        st.markdown(
            '<div class="home-selo">✨ Leva só 3 minutinhos</div>'
            '<h1 class="home-titulo">Cuide do seu <span class="destaque">sono, energia e bem-estar</span></h1>'
            '<p class="home-subtitulo">Responda perguntas rápidas sobre sua rotina, alimentação '
            "e atividade física e descubra como seus hábitos influenciam o seu dia a dia.</p>",
            unsafe_allow_html=True,
        )
        if st.button("🚀 Começar o questionário", type="primary", width="stretch"):
            ir_para("consentimento")
        if st.button("📊 Ver Dashboard", width="stretch"):
            ir_para("dashboard")

    with col_imagem:
        if os.path.exists(BANNER_PATH):
            st.image(BANNER_PATH, width="stretch")

    styles.cards_coloridos([
        ("rosa", "🌙", "Sono e rotina", "Mapeie seus horários, a qualidade do sono e as vezes em que acorda à noite."),
        ("amarelo", "⚡", "Energia no dia a dia", "Veja como alimentação, água e exercícios se conectam ao seu bem-estar."),
        ("verde_agua", "🥗", "Alimentação", "Entenda seus hábitos de frutas, água, café e alimentos processados."),
        ("roxo", "💡", "Dicas para você", "Receba seu índice de bem-estar e dicas práticas ao final."),
    ])


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
    nutricionista_id = st.session_state.nutricionista_id
    if email_valido and nutricionista_id and database.email_ja_respondeu(email, nutricionista_id):
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
            # Liga a resposta à nutricionista do link (vazio = nenhuma).
            database.COLUNA_NUTRICIONISTA: st.session_state.nutricionista_id,
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
    primeiro_nome = (dados.get("nome") or "").strip().split(" ")[0]
    styles.hero(
        "🎉",
        f"Parabéns{', ' + primeiro_nome if primeiro_nome else ''}!",
        "Você concluiu o questionário. Aqui está o seu relatório personalizado.",
        claro=True,
    )

    indice = analysis.calcular_indice_bem_estar(dados)
    classificacao = analysis.classificar_indice_bem_estar(indice)

    styles.cards_indicadores([
        ("🌟", "Índice de bem-estar", f"{indice}/100", classificacao),
        ("😴", "Horas de sono", f"{dados.get('horas_sono', '-')}h", "por noite"),
        ("🌅", "Cronotipo", str(dados.get("cronotipo", "-")), "seu ritmo natural"),
        ("⚡", "Energia", f"{dados.get('energia', '-')}/10", "durante o dia"),
    ], "resultado")
    st.caption(
        "O índice combina sono, água, exercício, frutas, estresse, energia e humor. "
        "É um índice próprio deste projeto, não uma medida clínica."
    )

    st.subheader("💡 Dicas para você")
    for dica in gerar_dicas(dados):
        icone, _, texto = dica.partition(" ")
        styles.cartao_recomendacao(icone, "Recomendação", texto)

    st.subheader("🍽️ Dica de alimentação")
    dica_ia = None
    if ai_advisor.ia_disponivel():
        with st.spinner("Preparando uma dica especial para você..."):
            periodo = ai_advisor.periodo_do_dia_atual()
            dica_ia = ai_advisor.gerar_dica_alimentacao_ia(
                cronotipo=dados.get("cronotipo", "Intermediário"),
                nivel_estresse=dados.get("nivel_estresse", 5),
                periodo=periodo,
                porcoes_frutas=dados.get("porcoes_frutas"),
            )
    if dica_ia:
        styles.cartao_recomendacao("🤖", "Sugestão da nossa assistente", dica_ia)
    else:
        styles.cartao_recomendacao(
            "🍎",
            "Sugestão para o seu dia",
            "Prefira refeições leves e bem distribuídas ao longo do dia, "
            "priorizando frutas, verduras e bastante água. "
            "Para orientação alimentar específica, consulte um nutricionista.",
        )

    render_contato_nutricionista()

    if st.button("🏠 Voltar ao início", type="primary"):
        st.session_state.user_data = {}
        ir_para("home")


# ============================================================
# DASHBOARD
# ============================================================
def render_login_nutricionista() -> None:
    """Formulário de entrada da nutricionista (código + senha)."""
    styles.hero(
        "🔐",
        "Área da nutricionista",
        "Entre com o seu código e a sua senha para ver as respostas dos seus pacientes.",
    )

    with st.form("form_login"):
        codigo = st.text_input("Seu código de nutricionista", key="login_codigo")
        senha = st.text_input("Senha", type="password", key="login_senha")
        entrou = st.form_submit_button("Entrar", width="stretch")

    if entrou:
        if auth.verificar_login(codigo, senha):
            st.session_state.nutri_logada = auth.normalizar_codigo(codigo)
            st.rerun()
        else:
            # Pequena espera dificulta tentativas automáticas de adivinhar a senha.
            time.sleep(1)
            st.error("Código ou senha incorretos. Confira e tente de novo.")

    if st.button("⬅️ Voltar ao início"):
        ir_para("home")


def _grafico(fig) -> None:
    """Mostra um gráfico do dashboard com as cores e fontes da página."""
    st.plotly_chart(styles.estilizar_grafico(fig, "dashboard"), width="stretch")


def render_dashboard():
    nutri = st.session_state.get("nutri_logada")
    if not nutri:
        render_login_nutricionista()
        return

    styles.hero(
        "📊",
        "Painel dos seus pacientes",
        f"Olá, {nutri}! Aqui você vê somente as respostas de quem entrou pelo seu link.",
    )

    col1, col2 = st.columns(2)
    if col1.button("⬅️ Voltar ao início", width="stretch"):
        ir_para("home")
    if col2.button("🚪 Sair", width="stretch"):
        st.session_state.nutri_logada = None
        ir_para("home")

    st.caption(
        f"🔗 Para convidar pacientes, envie o endereço deste app com **?nutri={nutri}** "
        f"no final (exemplo: https://seu-app.up.railway.app/?nutri={nutri})."
    )

    # Somente as respostas desta nutricionista. Nunca usar carregar_dados()
    # aqui: ela traz os dados de todas.
    df = database.carregar_dados_da_nutricionista(nutri)
    cores = styles.cores_graficos("dashboard")

    if df.empty:
        st.info(
            "🌱 Ainda não há respostas dos seus pacientes. Assim que alguém responder "
            "pelo seu link, os dados aparecem aqui."
        )
        return

    # Avisa se alguma linha tem dado numérico inválido (virou NaN na validação)
    colunas_checadas = [c for c in database.COLUNAS_NUMERICAS if c in df.columns]
    linhas_com_problema = df[df[colunas_checadas].isna().any(axis=1)]
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

    styles.cards_indicadores([
        ("👥", "Pacientes", str(len(df)), "respostas recebidas"),
        ("🌟", "Bem-estar médio", f"{indice_medio}/100" if indice_medio is not None else "-",
         "índice próprio, não clínico"),
        ("🔬", "Análises", str(len(resumo)), "relações testadas"),
        ("✅", "Significativas", str(len(significativos)), "com evidência (p < 0,05)"),
    ], "dashboard")

    # ------------------------------------------------------------
    # Insights descritivos (seguros mesmo com poucos dados)
    # ------------------------------------------------------------
    st.subheader("💡 Destaques")
    insights = analysis.gerar_insights_descritivos(df)
    if insights:
        for insight in insights:
            st.write(insight)
    else:
        st.caption("Ainda não há dados suficientes para gerar destaques.")

    st.divider()

    # ------------------------------------------------------------
    # Análise estatística (regressões, com aviso de amostra mínima)
    # ------------------------------------------------------------
    st.subheader("📈 Análise estatística")

    if not analysis.amostra_suficiente(df):
        st.info(
            f"São necessárias pelo menos {analysis.AMOSTRA_MINIMA} respostas para gerar "
            f"análises estatísticas confiáveis (você tem {len(df)}). "
            "Com poucos dados, qualquer relação encontrada seria pouco confiável. "
            "Continue convidando pacientes para liberar esta seção."
        )
    elif not resumo:
        st.info("Não há pares de variáveis suficientes para análise no momento.")
    else:
        if significativos:
            st.write(f"**{len(significativos)} relação(ões) com evidência estatística (p < 0,05):**")
            for r in significativos:
                st.success(f"**{r['forca']}** · {analysis.interpretar_resultado(r)}")
        else:
            st.write(
                "Nenhuma das relações testadas mostrou evidência estatística "
                "significativa até agora (todas com p ≥ 0,05). Isso é esperado com "
                "amostras pequenas e não significa que as relações não existam."
            )

        with st.expander("Ver todos os resultados testados, incluindo os não significativos"):
            for r in resumo:
                selo = "✅ significativo" if r["significativo"] else "⏳ ainda não confirmado"
                st.write(f"**{r['rotulo']}**: correlação {r['forca'].lower()} ({selo})")
                st.caption(analysis.interpretar_resultado(r))

    st.divider()

    # ------------------------------------------------------------
    # Gráficos (todos com a paleta turquesa / verde-água da página)
    # ------------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌅 Cronotipos")
        if "cronotipo" in df.columns:
            _grafico(px.pie(df, names="cronotipo", hole=0.45, color_discrete_sequence=cores))

    with col2:
        st.subheader("😴 Sono x energia")
        if "horas_sono" in df.columns and "energia" in df.columns:
            _grafico(px.scatter(df, x="horas_sono", y="energia", color="cronotipo",
                                trendline="ols", color_discrete_sequence=cores,
                                labels={"horas_sono": "Horas de sono", "energia": "Energia (0-10)"}))

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🍎 Frutas x energia")
        if "porcoes_frutas" in df.columns and "energia" in df.columns:
            _grafico(px.scatter(df, x="porcoes_frutas", y="energia",
                                trendline="ols", color_discrete_sequence=[cores[2]],
                                labels={"porcoes_frutas": "Porções de frutas/dia", "energia": "Energia (0-10)"}))

    with col4:
        st.subheader("🏃 Exercício x estresse")
        if "dias_exercicio" in df.columns and "nivel_estresse" in df.columns:
            _grafico(px.scatter(df, x="dias_exercicio", y="nivel_estresse",
                                trendline="ols", color_discrete_sequence=[cores[3]],
                                labels={"dias_exercicio": "Dias de exercício/semana", "nivel_estresse": "Estresse (0-10)"}))

    st.subheader("🧘 Estresse x qualidade do sono")
    if "nivel_estresse" in df.columns and "qualidade_sono" in df.columns:
        _grafico(px.box(df, x="qualidade_sono", y="nivel_estresse",
                        color="qualidade_sono",
                        category_orders={"qualidade_sono": ["Ruim", "Regular", "Boa", "Excelente"]},
                        color_discrete_sequence=cores,
                        labels={"qualidade_sono": "Qualidade do sono", "nivel_estresse": "Estresse (0-10)"}))

    st.subheader("📋 Respostas dos seus pacientes")
    st.dataframe(df, width="stretch")

    st.download_button(
        "⬇️ Baixar as respostas (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        file_name=f"respostas_{nutri}.csv",
        mime="text/csv",
    )


# ============================================================
# ROTEAMENTO PRINCIPAL
# ============================================================
def render_consentimento():
    """Tela de consentimento obrigatória antes do questionário.
    Exibida uma vez por sessão, quando o usuário clica em 'Começar Questionário'."""
    styles.hero(
        "📋",
        "Antes de começar",
        "Leia com atenção como cuidamos das suas informações.",
    )
    st.markdown(
        """
        **O que coletamos**
        Nome, e-mail, idade, sexo, profissão e informações sobre seus hábitos de sono,
        alimentação, atividade física e bem-estar geral.

        **Como usamos**
        Seus dados são utilizados para gerar seu relatório personalizado e para que a
        nutricionista que te convidou acompanhe suas respostas e sua evolução.

        **Quem tem acesso**
        Somente os responsáveis pela plataforma e a nutricionista que te convidou,
        com acesso protegido por senha. Seus dados não são vendidos nem
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
    if col1.button("⬅️ Voltar", width="stretch"):
        ir_para("home")
    if col2.button(
        "✅ Concordo e quero continuar",
        type="primary",
        width="stretch",
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

# Tema visual (cores) de cada tela. Telas do questionário ficam roxas.
TEMA_DA_TELA = {
    "home": "inicio",
    "resumo": "resultado",
    "dashboard": "dashboard",
}

styles.aplicar_tema(TEMA_DA_TELA.get(st.session_state.step, "questionario"))
ROTAS[st.session_state.step]()