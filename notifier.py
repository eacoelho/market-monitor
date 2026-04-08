"""
notifier.py
Envia alertas via Telegram (canal ou chat privado).
"""

import requests
import logging
from datetime import datetime, timezone
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def enviar_alerta(nome: str, ticker: str, variacao: float, preco: float, abertura: float, analise: str) -> bool:
    if   variacao >=  3: emoji = "🚀"
    elif variacao >=  1: emoji = "🟢"
    elif variacao <= -3: emoji = "💥"
    elif variacao <= -1: emoji = "🔴"
    else:                emoji = "🟡"

    sinal   = f"+{variacao:.2f}%" if variacao > 0 else f"{variacao:.2f}%"
    horario = datetime.now(timezone.utc).strftime("%d/%m %H:%M UTC")

    msg = (
        f"{emoji} *{nome}*\n"
        f"📊 `{sinal}` no intraday\n"
        f"💰 Preço: `{_fmt(ticker, preco)}` | Abertura: `{_fmt(ticker, abertura)}`\n"
        f"🕐 {horario}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{analise}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"_⚙️ Monitor automático — verifique antes de operar._"
    )
    return _send(msg)


def enviar_heartbeat() -> bool:
    msg = (
        f"🤖 *Monitor de Mercado ativo*\n"
        f"🕐 {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}"
    )
    return _send(msg)


def _send(msg: str) -> bool:
    try:
        r = requests.post(
            f"{BASE_URL}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=15,
        )
        if r.status_code == 200:
            return True
        logger.error(f"Telegram {r.status_code}: {r.text[:150]}")
        return False
    except Exception as e:
        logger.error(f"Telegram erro: {e}")
        return False


def _fmt(ticker: str, preco: float) -> str:
    if "BRL"  in ticker:           return f"R$ {preco:.4f}"
    if "BTC"  in ticker:           return f"$ {preco:,.2f}"
    if ticker in ("GC=F", "SI=F"): return f"$ {preco:,.2f}/oz"
    if ticker in ("CL=F", "BZ=F"): return f"$ {preco:,.2f}/bbl"
    return f"$ {preco:.4f}"
