import os
from datetime import datetime

import pandas as pd
import streamlit as st

CSV_PATH = "dados_sono.csv"

# Colunas que devem ser numéricas — protege os gráficos do Plotly
# contra valores corrompidos ou digitados manualmente no CSV.
COLUNAS_NUMERICAS = [
    "idade", "horas_sono", "interrupcoes_noturnas", "cronotipo_pontos",
    "porcoes_frutas", "litros_agua", "xicaras_cafe", "freq_processados",
    "energia", "humor", "produtividade",
    "dias_exercicio", "minutos_exercicio", "nivel_estresse",
]


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    """Carrega os dados do CSV e valida os tipos para evitar erros nos gráficos."""
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame()

    try:
        df = pd.read_csv(CSV_PATH)
    except pd.errors.ParserError:
        # Acontece se o CSV tiver linhas com números de colunas diferentes
        # (por exemplo, se o questionário ganhou novas perguntas depois que
        # algumas respostas antigas já tinham sido salvas com o formato anterior).
        st.error(
            "O arquivo de dados está com um formato inconsistente entre linhas "
            "(provavelmente respostas salvas com versões diferentes do questionário). "
            "Considere fazer backup do arquivo dados_sono.csv atual e começar um novo."
        )
        return pd.DataFrame()

    for col in COLUNAS_NUMERICAS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def salvar_dados(dados: dict) -> None:
    """Adiciona uma linha ao CSV e invalida o cache para o dashboard atualizar na hora."""
    dados = dados.copy()
    dados["data_envio"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    df_novo = pd.DataFrame([dados])

    if os.path.exists(CSV_PATH):
        df_novo.to_csv(CSV_PATH, mode="a", header=False, index=False)
    else:
        df_novo.to_csv(CSV_PATH, mode="w", header=True, index=False)

    # IMPORTANTE: sem isso o dashboard mostraria dados desatualizados
    # até o Streamlit decidir invalidar o cache por conta própria.
    carregar_dados.clear()


def buscar_respostas_por_email(email: str) -> pd.DataFrame:
    """Retorna todas as respostas anteriores de um e-mail, ordenadas da mais
    recente para a mais antiga. Retorna DataFrame vazio se não houver
    respostas ou se a coluna "email" ainda não existir no CSV (compatível
    com dados salvos antes dessa funcionalidade existir)."""
    df = carregar_dados()
    if df.empty or "email" not in df.columns:
        return pd.DataFrame()

    email_normalizado = email.strip().lower()
    respostas = df[df["email"].astype(str).str.strip().str.lower() == email_normalizado]
    if respostas.empty:
        return pd.DataFrame()

    if "data_envio" in respostas.columns:
        respostas = respostas.sort_values("data_envio", ascending=False)
    return respostas


def email_ja_respondeu(email: str) -> bool:
    """Indica se já existe ao menos uma resposta anterior para esse e-mail."""
    if not email or not email.strip():
        return False
    return not buscar_respostas_por_email(email).empty