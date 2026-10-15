"""
Login das nutricionistas.

Cada nutricionista tem um código (ex: "ana") e uma senha guardada numa
variável de ambiente chamada SENHA_NUTRI_<CÓDIGO EM MAIÚSCULAS>
(ex: SENHA_NUTRI_ANA). No computador ela fica no arquivo .env; no
Railway, em Variables. Nenhuma senha fica escrita no código.

Uma nutricionista "existe" para o app quando a variável dela está
configurada. É assim que o link de convite (?nutri=ana) é validado e
que o dashboard sabe de quem são os dados.
"""

import hmac
import os
import re

# Só letras minúsculas, números e "_" — evita códigos estranhos que
# poderiam virar nomes de variáveis inválidos.
_FORMATO_CODIGO = re.compile(r"^[a-z0-9_]{2,30}$")


def normalizar_codigo(codigo: str | None) -> str:
    """Remove espaços e coloca em minúsculas ("  Ana " -> "ana")."""
    return (codigo or "").strip().lower()


def _variavel_senha(codigo: str) -> str:
    return f"SENHA_NUTRI_{codigo.upper()}"


def nutricionista_existe(codigo: str | None) -> bool:
    """Indica se o código tem formato válido e uma senha configurada."""
    codigo = normalizar_codigo(codigo)
    return bool(_FORMATO_CODIGO.match(codigo)) and bool(os.environ.get(_variavel_senha(codigo)))


def verificar_login(codigo: str | None, senha: str | None) -> bool:
    """Confere código e senha. Retorna False para qualquer dado inválido."""
    codigo = normalizar_codigo(codigo)
    if not senha or not nutricionista_existe(codigo):
        return False
    senha_correta = os.environ[_variavel_senha(codigo)]
    # compare_digest compara em tempo constante (não "vaza" pela demora
    # quantos caracteres da senha estavam certos).
    return hmac.compare_digest(senha.encode("utf-8"), senha_correta.encode("utf-8"))
