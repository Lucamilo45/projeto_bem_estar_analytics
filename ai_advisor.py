"""
Camada de dicas de alimentação geradas por IA (Claude).

Importante sobre o escopo deste módulo:
- As dicas geradas aqui são GENÉRICAS, baseadas em horário do dia e cronotipo.
- Este módulo NUNCA calcula nada a partir de peso, altura, IMC ou outras
  variáveis corporais/clínicas — isso seria orientação nutricional
  personalizada, que é uma atividade regulamentada (nutricionista/CRN),
  não um recurso de bem-estar genérico. O prompt abaixo é construído
  deliberadamente para não aceitar esse tipo de dado mesmo que o app
  um dia colete peso/altura para outros fins (ex: cálculo de IMC informativo).

Se a API não estiver configurada ou falhar, as funções aqui retornam None
e o chamador (app.py) deve usar as dicas fixas locais como alternativa —
o app precisa continuar funcionando sem IA.
"""

import os

try:
    import anthropic
    _ANTHROPIC_DISPONIVEL = True
except ImportError:
    _ANTHROPIC_DISPONIVEL = False

MODELO = "claude-haiku-4-5"

SYSTEM_PROMPT = (
    "Você dá dicas genéricas e educativas de alimentação saudável por horário "
    "do dia, para um app de bem-estar. Regras estritas:\n"
    "1. NUNCA calcule ou mencione calorias, gramas de macronutrientes, IMC, "
    "peso ou altura, mesmo que perguntado.\n"
    "2. NUNCA prescreva quantidades específicas de alimentos.\n"
    "3. Dê apenas sugestões gerais de TIPOS de alimentos adequados para o "
    "horário e contexto informado (ex: 'alimentos ricos em fibra pela manhã').\n"
    "4. Se a pessoa tiver nível de estresse alto, pode sugerir alimentos "
    "tradicionalmente associados a relaxamento, sem prometer efeito clínico.\n"
    "5. Sempre inclua, ao final, que isso não substitui orientação de um "
    "nutricionista.\n"
    "6. Responda em português do Brasil, em até 4 frases curtas, tom acolhedor."
)


def ia_disponivel() -> bool:
    """Indica se a integração de IA pode ser usada (biblioteca + chave configuradas)."""
    return _ANTHROPIC_DISPONIVEL and bool(os.environ.get("ANTHROPIC_API_KEY"))


def gerar_dica_alimentacao_ia(
    cronotipo: str, nivel_estresse: int, periodo: str, porcoes_frutas: int | None = None
) -> str | None:
    """Gera uma dica genérica de alimentação via IA.

    Parâmetros aceitos são deliberadamente limitados a cronotipo, nível de
    estresse (0-10), período do dia e porções de frutas/dia já informadas
    no questionário — nenhum dado corporal (peso, altura, IMC) é aceito
    aqui por design, para manter o escopo em educação alimentar genérica.

    Retorna None se a IA não estiver disponível ou se a chamada falhar
    por qualquer motivo (rede, autenticação, limite de uso, etc.) — o
    chamador deve tratar None usando uma dica padrão local.
    """
    if not ia_disponivel():
        return None

    prompt = (
        f"Período do dia: {periodo}. "
        f"Cronotipo da pessoa: {cronotipo}. "
        f"Nível de estresse relatado (0-10): {nivel_estresse}. "
    )
    if porcoes_frutas is not None:
        prompt += f"A pessoa relatou consumir {porcoes_frutas} porções de frutas/verduras por dia. "
    prompt += "Dê uma dica curta de tipos de alimentos adequados para este momento."

    try:
        client = anthropic.Anthropic()
        resposta = client.messages.create(
            model=MODELO,
            max_tokens=200,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        texto = "".join(
            bloco.text for bloco in resposta.content if bloco.type == "text"
        ).strip()
        return texto if texto else None
    except Exception:
        # Qualquer falha (chave inválida, sem internet, limite de uso,
        # erro da API) cai aqui — o app continua funcionando sem IA.
        return None


def periodo_do_dia_atual() -> str:
    """Classifica a hora atual em um período do dia, em português."""
    from datetime import datetime
    hora = datetime.now().hour
    if 5 <= hora < 12:
        return "manhã"
    elif 12 <= hora < 18:
        return "tarde"
    else:
        return "noite"