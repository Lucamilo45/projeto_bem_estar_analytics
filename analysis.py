"""
Camada de análise estatística do projeto.

Mantém o cálculo de correlações e regressões separado da interface (app.py)
e da persistência (database.py), seguindo o mesmo princípio de
responsabilidade única usado no resto do projeto.
"""

import pandas as pd
import statsmodels.formula.api as smf

# Abaixo deste número de respostas, regressões e correlações ficam
# estatisticamente instáveis (R² inflado, p-valor sem sentido — testamos
# isso na prática: com 2-4 respostas o statsmodels chega a devolver
# R²=1.000, o que pareceria "perfeito" mas não significa nada).
AMOSTRA_MINIMA = 8

# Pares (variável explicativa, variável de resultado, rótulo amigável)
# que fazem sentido testar dado o que o questionário coleta.
# Ambas as variáveis precisam ser numéricas: regressão OLS simples não
# é o teste certo para uma variável de resultado categórica (ex: qualidade
# do sono é "Ruim"/"Regular"/"Boa"/"Excelente", não um número).
PARES_ANALISE = [
    ("horas_sono", "energia", "Horas de sono → Energia"),
    ("porcoes_frutas", "energia", "Porções de frutas → Energia"),
    ("dias_exercicio", "energia", "Dias de exercício → Energia"),
    ("nivel_estresse", "energia", "Nível de estresse → Energia"),
    ("litros_agua", "energia", "Litros de água → Energia"),
    ("nivel_estresse", "humor", "Nível de estresse → Humor"),
    ("dias_exercicio", "nivel_estresse", "Dias de exercício → Nível de estresse"),
]

# Rótulos legíveis para usar nas frases de interpretação e nos insights.
ROTULOS_LEGIVEIS = {
    "horas_sono": "horas de sono",
    "porcoes_frutas": "porções de frutas",
    "dias_exercicio": "dias de exercício",
    "nivel_estresse": "nível de estresse",
    "litros_agua": "consumo de água",
    "energia": "energia",
    "humor": "humor",
    "produtividade": "produtividade",
}


def classificar_forca_correlacao(r2: float) -> str:
    """Classifica a força da relação a partir do R² (coeficiente de determinação).

    Usa a convenção comum em ciências sociais/saúde, aplicada sobre o
    coeficiente de correlação r = sqrt(r2):
    r<0.1 muito fraca, <0.3 fraca, <0.5 moderada, <0.7 forte, >=0.7 muito forte.
    """
    r = r2 ** 0.5
    if r < 0.1:
        return "Muito fraca"
    elif r < 0.3:
        return "Fraca"
    elif r < 0.5:
        return "Moderada"
    elif r < 0.7:
        return "Forte"
    else:
        return "Muito forte"


def amostra_suficiente(df: pd.DataFrame) -> bool:
    """Indica se há respostas suficientes para uma análise estatística confiável."""
    return len(df) >= AMOSTRA_MINIMA


def regressao_simples(df: pd.DataFrame, x: str, y: str) -> dict | None:
    """Roda uma regressão linear simples (y em função de x) e retorna um resumo.

    Retorna None se as colunas não existirem ou não houver dados válidos
    suficientes (depois de remover linhas com NaN) para o cálculo.
    """
    if x not in df.columns or y not in df.columns:
        return None

    # Segunda camada de proteção: regressão OLS exige variáveis numéricas.
    # Mesmo que PARES_ANALISE só liste pares numéricos, essa checagem evita
    # um erro feio do statsmodels se a função for chamada com outros pares.
    if not pd.api.types.is_numeric_dtype(df[x]) or not pd.api.types.is_numeric_dtype(df[y]):
        return None

    dados = df[[x, y]].dropna()
    if len(dados) < AMOSTRA_MINIMA:
        return None

    # Variável precisa de alguma variação; sem isso o modelo não tem o que explicar.
    if dados[x].nunique() <= 1 or dados[y].nunique() <= 1:
        return None

    modelo = smf.ols(f"{y} ~ {x}", data=dados).fit()

    coef = float(modelo.params[x])
    p_valor = float(modelo.pvalues[x])
    r2 = float(modelo.rsquared)

    return {
        "x": x,
        "y": y,
        "n": len(dados),
        "coeficiente": round(coef, 3),
        "p_valor": round(p_valor, 4),
        "r2": round(r2, 3),
        "significativo": p_valor < 0.05,
        "direcao": "positiva" if coef > 0 else "negativa",
        "forca": classificar_forca_correlacao(r2),
    }


def gerar_resumo_estatistico(df: pd.DataFrame) -> list[dict]:
    """Roda todas as regressões definidas em PARES_ANALISE que forem possíveis.

    Retorna uma lista de resultados (dicts). Pares sem dados suficientes
    ou sem as colunas necessárias são simplesmente omitidos, não geram erro.
    """
    resultados = []
    for x, y, rotulo in PARES_ANALISE:
        resultado = regressao_simples(df, x, y)
        if resultado is not None:
            resultado["rotulo"] = rotulo
            resultados.append(resultado)
    return resultados


def interpretar_resultado(resultado: dict) -> str:
    """Gera uma frase em português explicando o resultado de forma acessível,
    em tom natural mas sem afirmar mais do que os dados sustentam."""
    x_legivel = ROTULOS_LEGIVEIS.get(resultado["x"], resultado["x"].replace("_", " "))
    y_legivel = ROTULOS_LEGIVEIS.get(resultado["y"], resultado["y"].replace("_", " "))

    if not resultado["significativo"]:
        return (
            f"Entre os participantes analisados, não foi possível confirmar uma relação "
            f"entre **{x_legivel}** e **{y_legivel}** (p={resultado['p_valor']}). "
            f"Com apenas {resultado['n']} respostas, esse resultado pode mudar conforme "
            f"novos dados forem adicionados — não significa que a relação não exista, "
            f"só que ainda não há evidência suficiente para afirmá-la."
        )

    direcao_txt = "também tendem a ter valores mais altos" if resultado["direcao"] == "positiva" else "tendem a ter valores mais baixos"
    return (
        f"Entre os participantes analisados, observou-se que, quanto maior **{x_legivel}**, "
        f"maior a tendência de **{y_legivel}** apresentar valores {('mais altos' if resultado['direcao'] == 'positiva' else 'mais baixos')} "
        f"(correlação {resultado['forca'].lower()}, explicando "
        f"{round(resultado['r2'] * 100, 1)}% da variação observada). "
        f"Como a amostra possui apenas {resultado['n']} participantes, esse resultado "
        f"deve ser interpretado com cautela e poderá mudar conforme novos dados forem "
        f"adicionados."
    )


# ============================================================
# ÍNDICE DE BEM-ESTAR
# ============================================================
# Pesos somam 1.0. São uma escolha de produto, não uma medida clínica
# validada — exibidos com transparência na interface para deixar claro
# que é um índice de referência do projeto, não um diagnóstico de saúde.
PESOS_INDICE_BEM_ESTAR = {
    "sono": 0.20,
    "agua": 0.10,
    "exercicio": 0.15,
    "frutas": 0.10,
    "estresse": 0.15,
    "energia": 0.15,
    "humor": 0.15,
}

# Valores considerados "ideais" para normalizar cada fator em uma escala 0-10.
_METAS_NORMALIZACAO = {
    "horas_sono": 8,
    "litros_agua": 2,
    "dias_exercicio": 5,
    "porcoes_frutas": 5,
}


def calcular_indice_bem_estar(dados: dict) -> float:
    """Combina 7 fatores em um índice de 0 a 100.

    Cada fator é normalizado para uma escala 0-10 antes de ser ponderado.
    Valores ausentes usam um padrão neutro (não penalizam nem favorecem
    quem não respondeu a etapa correspondente). O resultado é sempre
    limitado entre 0 e 100, mesmo com entradas fora do intervalo esperado.
    """
    def normalizar(valor, meta, default):
        v = valor if valor is not None else default
        return max(0.0, min(v / meta * 10, 10.0))

    sono_norm = normalizar(dados.get("horas_sono"), _METAS_NORMALIZACAO["horas_sono"], 7)
    agua_norm = normalizar(dados.get("litros_agua"), _METAS_NORMALIZACAO["litros_agua"], 2)
    exercicio_norm = normalizar(dados.get("dias_exercicio"), _METAS_NORMALIZACAO["dias_exercicio"], 3)
    frutas_norm = normalizar(dados.get("porcoes_frutas"), _METAS_NORMALIZACAO["porcoes_frutas"], 3)

    estresse_bruto = dados.get("nivel_estresse")
    estresse_norm = max(0.0, min(10 - (estresse_bruto if estresse_bruto is not None else 5), 10.0))

    energia_norm = max(0.0, min(dados.get("energia") if dados.get("energia") is not None else 5, 10.0))
    humor_norm = max(0.0, min(dados.get("humor") if dados.get("humor") is not None else 5, 10.0))

    score = (
        sono_norm * PESOS_INDICE_BEM_ESTAR["sono"]
        + agua_norm * PESOS_INDICE_BEM_ESTAR["agua"]
        + exercicio_norm * PESOS_INDICE_BEM_ESTAR["exercicio"]
        + frutas_norm * PESOS_INDICE_BEM_ESTAR["frutas"]
        + estresse_norm * PESOS_INDICE_BEM_ESTAR["estresse"]
        + energia_norm * PESOS_INDICE_BEM_ESTAR["energia"]
        + humor_norm * PESOS_INDICE_BEM_ESTAR["humor"]
    )
    return round(max(0.0, min(score * 10, 100.0)), 1)


def classificar_indice_bem_estar(indice: float) -> str:
    """Classificação textual do índice de 0-100."""
    if indice >= 80:
        return "Excelente"
    elif indice >= 65:
        return "Bom"
    elif indice >= 45:
        return "Regular"
    else:
        return "Atenção necessária"


# ============================================================
# INSIGHTS DESCRITIVOS (estatística descritiva, não causal)
# ============================================================
# Importante: estes insights descrevem A AMOSTRA (contagens, médias),
# sem afirmar relação causal entre variáveis. Por isso são seguros de
# mostrar mesmo com poucas respostas (n < AMOSTRA_MINIMA) — diferente
# dos resultados de regressão, que exigem amostra mínima para serem confiáveis.
def gerar_insights_descritivos(df: pd.DataFrame) -> list[str]:
    """Gera observações descritivas simples sobre a amostra coletada."""
    insights = []
    n = len(df)
    if n == 0:
        return insights

    if "litros_agua" in df.columns:
        agua_valida = df["litros_agua"].dropna()
        if len(agua_valida) > 0:
            abaixo_meta = (agua_valida < 2).sum()
            pct = round(abaixo_meta / len(agua_valida) * 100)
            if pct > 0:
                insights.append(
                    f"💧 O consumo de água está abaixo de 2 litros/dia para "
                    f"{pct}% dos participantes ({abaixo_meta} de {len(agua_valida)})."
                )

    if "dias_exercicio" in df.columns:
        exercicio_valido = df["dias_exercicio"].dropna()
        if len(exercicio_valido) > 0:
            media_exercicio = exercicio_valido.mean()
            insights.append(
                f"🏃 Em média, os participantes praticam exercício "
                f"{media_exercicio:.1f} dia(s) por semana."
            )

    if "nivel_estresse" in df.columns:
        estresse_valido = df["nivel_estresse"].dropna()
        if len(estresse_valido) > 0:
            media_estresse = estresse_valido.mean()
            if media_estresse >= 7:
                insights.append(
                    f"😟 O nível médio de estresse da amostra está alto "
                    f"({media_estresse:.1f}/10)."
                )
            elif media_estresse <= 3:
                insights.append(
                    f"😌 O nível médio de estresse da amostra está baixo "
                    f"({media_estresse:.1f}/10)."
                )

    if "horas_sono" in df.columns:
        sono_valido = df["horas_sono"].dropna()
        if len(sono_valido) > 0:
            abaixo_7h = (sono_valido < 7).sum()
            pct = round(abaixo_7h / len(sono_valido) * 100)
            if pct > 0:
                insights.append(
                    f"😴 {pct}% dos participantes dormem menos de 7 horas por noite "
                    f"({abaixo_7h} de {len(sono_valido)})."
                )

    if "cronotipo" in df.columns:
        cronotipo_valido = df["cronotipo"].dropna()
        if len(cronotipo_valido) > 0:
            mais_comum = cronotipo_valido.mode()
            if len(mais_comum) > 0:
                contagem = (cronotipo_valido == mais_comum[0]).sum()
                pct = round(contagem / len(cronotipo_valido) * 100)
                insights.append(
                    f"🌙 O cronotipo mais comum entre os participantes é "
                    f"**{mais_comum[0]}** ({pct}% da amostra)."
                )

    return insights