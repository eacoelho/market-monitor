"""
notifier.py
Envia alertas via Telegram Bot API.
"""

import requests
import logging
from datetime import datetime
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)
TELEGRAM_URL = "https://api.telegram.org/bot{token}/sendMessage"


def enviar_alerta(nome, ticker, variacao, preco, abertura, analise) -> bool:
    if   variacao >=  3: emoji = "🚀"
    elif variacao >=  1: emoji = "🟢"
    elif variacao <= -3: emoji = "💥"
    elif variacao <= -1: emoji = "🔴"
    else:                emoji = "🟡"

    sinal   = "+" if variacao > 0 else ""
    horario = datetime.now().strftime("%d/%m %H:%M")

    msg = (
        f"{emoji} *ALERTA DE MERCADO* {emoji}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"*{nome}*\n"
        f"📊 Variação: *{sinal}{variacao:.2f}%* no intraday\n"
        f"💰 Preço atual: *{_fmt(ticker, preco)}*\n"
        f"📂 Abertura: {_fmt(ticker, abertura)}\n"
        f"🕐 Horário: {horario}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"{analise}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"_⚙️ Monitor automático — verifique antes de operar._"
    )

    return _enviar(msg)


def enviar_heartbeat() -> bool:
    msg = (
        f"🤖 *Monitor de Mercado — Ativo*\n"
        f"✅ Robô rodando normalmente\n"
        f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        f"_Alertas serão enviados conforme variações detectadas._"
    )
    return _enviar(msg)


def _enviar(msg: str) -> bool:
    try:
        r = requests.post(
            TELEGRAM_URL.format(token=TELEGRAM_TOKEN),
            json={
                "chat_id":    TELEGRAM_CHAT_ID,
                "text":       msg,
                "parse_mode": "Markdown",
            },
            timeout=15,
        )
        if r.status_code == 200:
            return True
        logger.error(f"Telegram erro {r.status_code}: {r.text[:200]}")
        return False
    except Exception as e:
        logger.error(f"Erro ao enviar Telegram: {e}")
        return False


def _fmt(ticker: str, preco: float) -> str:
    if "BRL"  in ticker:           return f"R$ {preco:.4f}"
    if "BTC"  in ticker:           return f"$ {preco:,.2f}"
    if ticker in ("GC=F", "SI=F"): return f"$ {preco:,.2f}/oz"
    if ticker == "CL=F":           return f"$ {preco:,.2f}/bbl"
    return f"$ {preco:.4f}"
