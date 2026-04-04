"""
price_fetcher.py
Busca preços e calcula variação intraday via Yahoo Finance (yfinance).
"""

import yfinance as yf
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def get_intraday_variation(ticker: str) -> Optional[dict]:
    """
    Retorna variação percentual do ativo desde a abertura do pregão atual.

    Returns:
        dict com ticker, preco_atual, abertura, variacao_pct, horario
        None se não conseguir buscar os dados
    """
    try:
        t    = yf.Ticker(ticker)
        info = t.fast_info

        preco_atual = info.last_price
        abertura    = info.open

        if not preco_atual or not abertura or abertura == 0:
            logger.warning(f"Dados inválidos para {ticker}: preco={preco_atual}, abertura={abertura}")
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
