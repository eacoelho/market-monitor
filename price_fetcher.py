"""
price_fetcher.py
Busca preços e calcula variação intraday via yfinance.
Filtra candles pelo dia atual para evitar variações falsas fora do pregão.
"""

import yfinance as yf
import logging
from datetime import datetime, date
from typing import Optional

logger = logging.getLogger(__name__)


def get_intraday_variation(ticker: str) -> Optional[dict]:
    """
    Retorna variação percentual do ativo desde a abertura do pregão atual.
    Retorna None se o mercado estiver fechado ou sem dados do dia.
    """
    try:
        t    = yf.Ticker(ticker)
        hist = t.history(period="1d", interval="1m")

        if hist.empty:
            logger.info(f"{ticker}: sem dados (mercado fechado ou fora do pregão)")
            return None

        # Filtra apenas candles de hoje no horário de Brasília
        hoje      = date.today()
        hist.index = hist.index.tz_convert("America/Sao_Paulo")
        hist_hoje  = hist[hist.index.date == hoje]

        if len(hist_hoje) < 2:
            logger.info(f"{ticker}: sem candles de hoje — mercado fechado")
            return None

        abertura    = float(hist_hoje["Open"].iloc[0])
        preco_atual = float(hist_hoje["Close"].iloc[-1])

        if abertura == 0:
            logger.warning(f"{ticker}: abertura zerada, ignorando")
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
