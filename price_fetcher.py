"""
price_fetcher.py
Busca variação intraday via yfinance, filtrando apenas candles do dia atual em UTC.
"""

import yfinance as yf
import logging
from datetime import datetime, timezone, date
from typing import Optional

logger = logging.getLogger(__name__)


def get_intraday_variation(ticker: str) -> Optional[dict]:
    """
    Retorna variação % desde a abertura do pregão atual (UTC).
    Retorna None se mercado fechado ou sem dados do dia.
    """
    try:
        hist = yf.Ticker(ticker).history(period="1d", interval="1m")

        if hist.empty:
            logger.info(f"{ticker}: sem dados")
            return None

        hist.index = hist.index.tz_convert("UTC")
        hoje_utc   = datetime.now(timezone.utc).date()
        hist_hoje  = hist[hist.index.date == hoje_utc]

        if len(hist_hoje) < 2:
            logger.info(f"{ticker}: sem candles hoje (UTC)")
            return None

        abertura    = float(hist_hoje["Open"].iloc[0])
        preco_atual = float(hist_hoje["Close"].iloc[-1])

        if abertura == 0:
            return None

        return {
            "ticker":       ticker,
            "preco_atual":  round(preco_atual, 6),
            "abertura":     round(abertura, 6),
            "variacao_pct": round(((preco_atual - abertura) / abertura) * 100, 3),
        }

    except Exception as e:
        logger.error(f"Erro ao buscar {ticker}: {e}")
        return None
