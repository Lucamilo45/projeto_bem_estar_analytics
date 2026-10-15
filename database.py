import os
import shutil
from datetime import datetime

import pandas as pd
import streamlit as st

# Pode ser trocado pela variável de ambiente DADOS_CSV (útil para testes
# com dados fictícios, sem tocar no arquivo real).
CSV_PATH = os.environ.get("DADOS_CSV", "dados_sono.csv")

# Coluna que liga cada resposta à nutricionista que convidou a pessoa.
# Respostas sem nutricionista (ou salvas antes dessa coluna existir)
# ficam com esse campo vazio e não aparecem para nenhuma nutricionista.
COLUNA_NUTRICIONISTA = "nutricionista_id"

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
    """Carrega os dados do CSV e valida os tipos para evitar erros nos gráficos.

    ATENÇÃO: retorna as respostas de TODAS as nutricionistas. Telas que
    mostram dados devem usar carregar_dados_da_nutricionista().
    """
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame()

    try:
        # dtype=str no código da nutricionista: sem isso, uma coluna vazia
        # seria lida como número (NaN) e viraria o texto "nan".
        df = pd.read_csv(CSV_PATH, dtype={COLUNA_NUTRICIONISTA: str})
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


def carregar_dados_da_nutricionista(nutricionista_id: str) -> pd.DataFrame:
    """Retorna somente as respostas ligadas a essa nutricionista.

    Retorna DataFrame vazio se o código estiver vazio ou se o CSV ainda
    não tiver a coluna de nutricionista (dados antigos não são de ninguém).
    """
    nutricionista_id = (nutricionista_id or "").strip()
    df = carregar_dados()
    if not nutricionista_id or df.empty or COLUNA_NUTRICIONISTA not in df.columns:
        return pd.DataFrame()

    codigos = df[COLUNA_NUTRICIONISTA].fillna("").astype(str).str.strip()
    return df[codigos == nutricionista_id].reset_index(drop=True)


def _copia_de_seguranca() -> str:
    """Copia o CSV atual para dados_sono_backup_AAAAMMDD_HHMMSS.csv e
    retorna o nome da cópia. Usada antes de reescrever o arquivo."""
    base, ext = os.path.splitext(CSV_PATH)
    destino = f"{base}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    shutil.copy2(CSV_PATH, destino)
    return destino


def salvar_dados(dados: dict) -> None:
    """Adiciona uma linha ao CSV e invalida o cache para o dashboard atualizar na hora."""
    dados = dados.copy()
    dados["data_envio"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    df_novo = pd.DataFrame([dados])

    if not os.path.exists(CSV_PATH):
        df_novo.to_csv(CSV_PATH, mode="w", header=True, index=False)
    else:
        colunas_existentes = list(pd.read_csv(CSV_PATH, nrows=0).columns)
        colunas_novas = [c for c in df_novo.columns if c not in colunas_existentes]

        if colunas_novas:
            # O questionário ganhou campos novos (ex: nutricionista_id).
            # Faz uma cópia de segurança e reescreve o arquivo com as
            # colunas novas, deixando-as vazias nas respostas antigas.
            # dtype=str + keep_default_na=False preservam os valores
            # antigos exatamente como estavam escritos.
            _copia_de_seguranca()
            df_antigo = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)
            df_completo = pd.concat([df_antigo, df_novo], ignore_index=True)
            df_completo = df_completo[colunas_existentes + colunas_novas]
            df_completo.to_csv(CSV_PATH, mode="w", header=True, index=False)
        else:
            # Alinha a linha nova à ordem das colunas do arquivo.
            df_novo = df_novo.reindex(columns=colunas_existentes)
            df_novo.to_csv(CSV_PATH, mode="a", header=False, index=False)

    # IMPORTANTE: sem isso o dashboard mostraria dados desatualizados
    # até o Streamlit decidir invalidar o cache por conta própria.
    carregar_dados.clear()


def buscar_respostas_por_email(email: str, nutricionista_id: str) -> pd.DataFrame:
    """Retorna as respostas anteriores de um e-mail, dentro da mesma
    nutricionista, ordenadas da mais recente para a mais antiga. Retorna
    DataFrame vazio se não houver respostas ou se a coluna "email" ainda
    não existir no CSV."""
    df = carregar_dados_da_nutricionista(nutricionista_id)
    if df.empty or "email" not in df.columns:
        return pd.DataFrame()

    email_normalizado = email.strip().lower()
    respostas = df[df["email"].astype(str).str.strip().str.lower() == email_normalizado]
    if respostas.empty:
        return pd.DataFrame()

    if "data_envio" in respostas.columns:
        respostas = respostas.sort_values("data_envio", ascending=False)
    return respostas


def email_ja_respondeu(email: str, nutricionista_id: str) -> bool:
    """Indica se já existe ao menos uma resposta anterior para esse e-mail
    com a mesma nutricionista."""
    if not email or not email.strip():
        return False
    return not buscar_respostas_por_email(email, nutricionista_id).empty
