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


def enviar_alerta(nome, ticker, variacao, preco, abertura, analise) -> bool:
    """
    Monta e envia a mensagem de alerta via WhatsApp (CallMeBot).

    Returns:
        True se enviado com sucesso, False caso contrário.
    """
    if   variacao >=  3: emoji = "🚀"
    elif variacao >=  1: emoji = "🟢"
    elif variacao <= -3: emoji = "💥"
    elif variacao <= -1: emoji = "🔴"
    else:                emoji = "🟡"

    sinal   = "+" if variacao > 0 else ""
    horario = datetime.now().strftime("%d/%m %H:%M")

    msg = f"""{emoji} *ALERTA DE MERCADO* {emoji}
━━━━━━━━━━━━━━━━━━━
*{nome}*
📊 Variação: *{sinal}{variacao:.2f}%* no intraday
💰 Preço atual: *{_fmt(ticker, preco)}*
📂 Abertura: {_fmt(ticker, abertura)}
🕐 Horário: {horario}
━━━━━━━━━━━━━━━━━━━
{analise}
━━━━━━━━━━━━━━━━━━━
_⚙️ Monitor automático — verifique antes de operar._"""

    try:
        url = (
            f"{CALLMEBOT_URL}"
            f"?phone={CALLMEBOT_PHONE}"
            f"&text={urllib.parse.quote(msg)}"
            f"&apikey={CALLMEBOT_APIKEY}"
        )
        r = requests.get(url, timeout=15)
        return r.status_code == 200
    except Exception as e:
        logger.error(f"Erro ao enviar WhatsApp: {e}")
        return False


def enviar_heartbeat() -> bool:
    """Envia mensagem diária confirmando que o robô está ativo."""
    msg = (
        f"🤖 *Monitor de Mercado — Ativo*\n"
        f"✅ Robô rodando normalmente\n"
        f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        f"_Alertas serão enviados conforme variações detectadas._"
    )
    try:
        url = (
            f"{CALLMEBOT_URL}"
            f"?phone={CALLMEBOT_PHONE}"
            f"&text={urllib.parse.quote(msg)}"
            f"&apikey={CALLMEBOT_APIKEY}"
        )
        r = requests.get(url, timeout=15)
        return r.status_code == 200
    except Exception as e:
        logger.error(f"Erro no heartbeat: {e}")
        return False


def _fmt(ticker: str, preco: float) -> str:
    """Formata preço de acordo com o tipo de ativo."""
    if "BRL"  in ticker:           return f"R$ {preco:.4f}"
    if "BTC"  in ticker:           return f"$ {preco:,.2f}"
    if ticker in ("GC=F", "SI=F"): return f"$ {preco:,.2f}/oz"
    if ticker == "CL=F":           return f"$ {preco:,.2f}/bbl"
    return f"$ {preco:.4f}"
