"""
price_fetcher.py
Busca preços e calcula variação intraday via yfinance.
Filtra candles pelo dia atual para evitar variações falsas fora do pregão.
"""

import yfinance as yf
import requests
import logging
from datetime import datetime, date
from typing import Optional

logger = logging.getLogger(__name__)

# Sessão com user-agent de browser
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})


def get_intraday_variation(ticker: str) -> Optional[dict]:
    try:
        t    = yf.Ticker(ticker, session=session)
        hist = t.history(period="1d", interval="1m")

        if hist.empty:
            logger.warning(f"Histórico vazio para {ticker}")
            return None

        # --- Filtra apenas candles de hoje ---
        hoje = date.today()
        hist.index = hist.index.tz_convert("America/Sao_Paulo")
        hist_hoje  = hist[hist.index.date == hoje]

        if len(hist_hoje) < 2:
            logger.info(f"{ticker}: mercado fechado ou ainda sem candles de hoje ({len(hist_hoje)} candles)")
            return None

        abertura    = float(hist_hoje["Open"].iloc[0])
        preco_atual = float(hist_hoje["Close"].iloc[-1])

        if abertura == 0:
            return None

        variacao_pct = ((preco_atual - abertura) / abertura) * 100

        return {
            "ticker":       ticker,
            "preco_atual":  round(preco_atual, 6),
            "abertura":     round(abertura, 6),
            "variacao_pct": round(variacao_pct, 3),
            "horario":      datetime.now().strftime("%H:%M"),
            "data":         datetime.now().strftime("%d/%m/%Y"),
        }

    except Exception as e:
        logger.error(f"Erro ao buscar preço de {ticker}: {e}")
        return None
