"""
notifier.py
Envia alertas via WhatsApp usando CallMeBot (API gratuita).
Documentação: https://www.callmebot.com/blog/free-api-whatsapp-messages/
"""

import requests
import urllib.parse
import logging
from datetime import datetime
from config import CALLMEBOT_PHONE, CALLMEBOT_APIKEY

logger = logging.getLogger(__name__)

CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"


def enviar_alerta(
    nome:     str,
    ticker:   str,
    variacao: float,
    preco:    float,
    abertura: float,
    analise:  str,
) -> bool:
    """
    Monta e envia a mensagem de alerta via WhatsApp (CallMeBot).

    Returns:
        True se enviado com sucesso, False caso contrário.
    """

    # --- Emojis e direção ---
    if variacao >= 3:
        emoji_dir = "🚀"
    elif variacao >= 1:
        emoji_dir = "🟢"
    elif variacao <= -3:
        emoji_dir = "💥"
    elif variacao <= -1:
        emoji_dir = "🔴"
    else:
        emoji_dir = "🟡"

    direcao_texto = f"+{variacao:.2f}%" if variacao > 0 else f"{variacao:.2f}%"
    horario       = datetime.now().strftime("%d/%m %H:%M")

    # --- Monta a mensagem ---
    mensagem = f"""{emoji_dir} *ALERTA DE MERCADO* {emoji_dir}
━━━━━━━━━━━━━━━━━━━
*{nome}*
📊 Variação: *{direcao_texto}* no intraday
💰 Preço atual: *{_fmt_preco(ticker, preco)}*
📂 Abertura: {_fmt_preco(ticker, abertura)}
🕐 Horário: {horario}
━━━━━━━━━━━━━━━━━━━
{analise}
━━━━━━━━━━━━━━━━━━━
_⚙️ Monitor automático — verifique antes de operar._"""

    # --- Envia ---
    try:
        params = {
            "phone":  CALLMEBOT_PHONE,
            "text":   mensagem,
            "apikey": CALLMEBOT_APIKEY,
        }

        # CallMeBot exige URL encoding da mensagem
        url = (
            f"{CALLMEBOT_URL}"
            f"?phone={CALLMEBOT_PHONE}"
            f"&text={urllib.parse.quote(mensagem)}"
            f"&apikey={CALLMEBOT_APIKEY}"
        )

        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            logger.info(f"✅ WhatsApp enviado: {nome} {direcao_texto}")
            return True
        else:
            logger.error(f"Erro CallMeBot {response.status_code}: {response.text}")
            return False

    except requests.exceptions.Timeout:
        logger.error("Timeout ao enviar WhatsApp")
        return False

    except Exception as e:
        logger.error(f"Erro inesperado ao enviar WhatsApp: {e}")
        return False


def enviar_heartbeat() -> bool:
    """
    Envia uma mensagem de status diária para confirmar que o robô está rodando.
    Chamado automaticamente às 08:00 todos os dias.
    """
    horario = datetime.now().strftime("%d/%m/%Y %H:%M")
    mensagem = (
        f"🤖 *Monitor de Mercado — Ativo*\n"
        f"✅ Robô rodando normalmente\n"
        f"🕐 {horario}\n"
        f"_Alertas serão enviados conforme variações detectadas._"
    )

    try:
        url = (
            f"{CALLMEBOT_URL}"
            f"?phone={CALLMEBOT_PHONE}"
            f"&text={urllib.parse.quote(mensagem)}"
            f"&apikey={CALLMEBOT_APIKEY}"
        )
        response = requests.get(url, timeout=15)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Erro no heartbeat: {e}")
        return False


def _fmt_preco(ticker: str, preco: float) -> str:
    """Formata preço de acordo com o tipo de ativo."""
    if "BRL" in ticker:
        return f"R$ {preco:.4f}"
    elif "BTC" in ticker or "ETH" in ticker:
        return f"$ {preco:,.2f}"
    elif ticker in ("GC=F", "SI=F"):
        return f"$ {preco:,.2f}/oz"
    elif ticker == "CL=F":
        return f"$ {preco:,.2f}/bbl"
    else:
        return f"$ {preco:.4f}"
