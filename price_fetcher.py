"""
price_fetcher.py
Busca preços e calcula variação intraday via Yahoo Finance (yfinance).
Usa history() em vez de fast_info — mais estável contra mudanças de API.
"""

import yfinance as yf
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def get_intraday_variation(ticker: str) -> Optional[dict]:
    """
    Retorna variação percentual do ativo desde a abertura do pregão atual.
    Usa period='1d' + interval='1m' para pegar abertura e último preço do dia.
    """
    try:
        t    = yf.Ticker(ticker)
        hist = t.history(period="1d", interval="1m")

        if hist.empty or len(hist) < 2:
            logger.warning(f"Histórico vazio ou insuficiente para {ticker}")
            return None

        abertura    = float(hist["Open"].iloc[0])   # Primeiro candle do dia
        preco_atual = float(hist["Close"].iloc[-1])  # Último candle disponível

        if abertura == 0:
            logger.warning(f"Abertura zero para {ticker}")
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
