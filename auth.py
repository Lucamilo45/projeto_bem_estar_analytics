"""
Cadastro e login das nutricionistas.

Cada nutricionista tem um código (ex: "ana") e até quatro variáveis de
ambiente com esse código em MAIÚSCULAS no nome:

    SENHA_NUTRI_ANA      senha da área da nutricionista (obrigatória)
    NOME_NUTRI_ANA       nome mostrado aos pacientes (opcional)
    WHATSAPP_NUTRI_ANA   WhatsApp com DDI e DDD, só números (opcional)
    INSTAGRAM_NUTRI_ANA  usuário do Instagram, sem @ (opcional)

Onde ficam:
- no computador: arquivo .env (formato NOME=valor);
- no Streamlit Cloud: Settings > Secrets (formato NOME = "valor"), que o
  Streamlit transforma em variáveis de ambiente ao iniciar o app;
- no Railway: Variables.
Nenhuma senha ou contato fica escrito no código (o repositório é público).

Uma nutricionista "existe" para o app quando a senha dela está
configurada. É assim que o link de convite (?nutri=ana) é validado e
que o dashboard sabe de quem são os dados.
"""

import hmac
import os
import re

# Só letras minúsculas, números e "_" — evita códigos estranhos que
# poderiam virar nomes de variáveis inválidos.
_FORMATO_CODIGO = re.compile(r"^[a-z0-9_]{2,30}$")
_FORMATO_INSTAGRAM = re.compile(r"^[A-Za-z0-9._]{1,30}$")


def normalizar_codigo(codigo: str | None) -> str:
    """Remove espaços e coloca em minúsculas ("  Ana " -> "ana")."""
    return (codigo or "").strip().lower()


def _variavel(prefixo: str, codigo: str) -> str:
    return f"{prefixo}_NUTRI_{codigo.upper()}"


def nutricionista_existe(codigo: str | None) -> bool:
    """Indica se o código tem formato válido e uma senha configurada."""
    codigo = normalizar_codigo(codigo)
    return bool(_FORMATO_CODIGO.match(codigo)) and bool(os.environ.get(_variavel("SENHA", codigo)))


def verificar_login(codigo: str | None, senha: str | None) -> bool:
    """Confere código e senha. Retorna False para qualquer dado inválido."""
    codigo = normalizar_codigo(codigo)
    if not senha or not nutricionista_existe(codigo):
        return False
    senha_correta = os.environ[_variavel("SENHA", codigo)]
    # compare_digest compara em tempo constante (não "vaza" pela demora
    # quantos caracteres da senha estavam certos).
    return hmac.compare_digest(senha.encode("utf-8"), senha_correta.encode("utf-8"))


def perfil(codigo: str | None) -> dict | None:
    """Dados públicos da nutricionista, para mostrar aos pacientes dela.

    Retorna None se a nutricionista não existir. Campos não preenchidos ou
    em formato inválido voltam vazios (e o botão correspondente some),
    em vez de levar o paciente a um número ou perfil errado.
    """
    codigo = normalizar_codigo(codigo)
    if not nutricionista_existe(codigo):
        return None

    nome = os.environ.get(_variavel("NOME", codigo), "").strip()

    # Aceita "+55 (11) 98888-7777" e guarda só os números: 5511988887777.
    whatsapp = re.sub(r"\D", "", os.environ.get(_variavel("WHATSAPP", codigo), ""))
    if not 10 <= len(whatsapp) <= 15:
        whatsapp = ""

    instagram = os.environ.get(_variavel("INSTAGRAM", codigo), "").strip().lstrip("@")
    if not _FORMATO_INSTAGRAM.match(instagram):
        instagram = ""

    return {
        "codigo": codigo,
        "nome": nome or codigo.capitalize(),
        "whatsapp": whatsapp,
        "instagram": instagram,
    }
