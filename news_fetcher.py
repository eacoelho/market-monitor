"""
news_fetcher.py
Busca headlines reais via RSS gratuito (Reuters, Investing.com, OilPrice, Kitco, etc.)
e filtra as mais relevantes para cada ativo antes de passar ao LLM.
Sem API key — 100% gratuito.
"""

import feedparser
import logging
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Optional

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  FEEDS RSS POR CATEGORIA                                             #
# ------------------------------------------------------------------ #
RSS_FEEDS = {
    "macro": [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://feeds.reuters.com/reuters/topNews",
        "https://feeds.marketwatch.com/marketwatch/realtimeheadlines/",
        "https://www.investing.com/rss/news_25.rss",
        "https://www.investing.com/rss/news_11.rss",
    ],
    "brasil": [
        "https://www.investing.com/rss/news_285.rss",
        "https://feeds.reuters.com/reuters/latamTopNews",
        "https://braziljournal.com/feed/",
    ],
    "agro": [
        "https://www.investing.com/rss/news_11.rss",
        "https://feeds.reuters.com/reuters/commoditiesNews",
        "https://www.agweb.com/rss.xml",
    ],
    "energia": [
        "https://feeds.reuters.com/reuters/energyNews",
        "https://www.investing.com/rss/news_11.rss",
        "https://oilprice.com/rss/main",
    ],
    "metais": [
        "https://feeds.reuters.com/reuters/commoditiesNews",
        "https://www.investing.com/rss/news_11.rss",
        "https://www.kitco.com/rss/kitco-news.xml",
    ],
    "crypto": [
        "https://cointelegraph.com/rss",
        "https://coindesk.com/arc/outboundfeeds/rss/",
        "https://feeds.reuters.com/reuters/technologyNews",
    ],
}

# Mapeamento ticker → categorias de feed
TICKER_FEEDS = {
    "USDBRL=X": ["macro", "brasil"],
    "EURBRL=X": ["macro", "brasil"],
    "EURUSD=X": ["macro"],
    "BTC-USD":  ["crypto", "macro"],
    "GC=F":     ["metais", "macro"],
    "SI=F":     ["metais", "macro"],
    "CL=F":     ["energia", "macro"],
    "ZC=F":     ["agro", "macro"],
    "ZS=F":     ["agro", "brasil"],
    "SB=F":     ["agro", "brasil"],
}

# Palavras-chave por ticker para filtrar notícias relevantes
TICKER_KEYWORDS = {
    "USDBRL=X": ["real", "brl", "brazil", "brasil", "copom", "lula", "fazenda", "dollar", "fed", "dólar"],
    "EURBRL=X": ["real", "euro", "eur", "ecb", "bce", "brazil", "brasil"],
    "EURUSD=X": ["euro", "eur", "dollar", "usd", "fed", "ecb", "bce", "inflation", "rate"],
    "BTC-USD":  ["bitcoin", "btc", "crypto", "cryptocurrency", "sec", "etf", "blockchain"],
    "GC=F":     ["gold", "ouro", "fed", "inflation", "rate", "treasury", "yields"],
    "SI=F":     ["silver", "prata", "metal", "industrial"],
    "CL=F":     ["oil", "petróleo", "crude", "opec", "opep", "eia", "energy", "brent"],
    "ZC=F":     ["corn", "milho", "grain", "usda", "crop", "climate", "ethanol"],
    "ZS=F":     ["soy", "soja", "soybean", "china", "usda", "crop", "brazil", "brasil"],
    "SB=F":     ["sugar", "açúcar", "cane", "ethanol", "india", "brazil", "brasil"],
}

# Cache em memória — evita rebuscar feeds no mesmo ciclo de 5 min
_cache: dict = {}
CACHE_TTL_SECONDS = 300


def buscar_noticias(ticker: str, max_headlines: int = 8) -> str:
    """
    Busca e filtra headlines relevantes para o ativo via RSS.
    Retorna string formatada para embutir no prompt do LLM,
    ou string vazia se não encontrar nada relevante.
    """
    cache_key = f"{ticker}_{int(time.time() // CACHE_TTL_SECONDS)}"
    if cache_key in _cache:
        return _cache[cache_key]

    categorias       = TICKER_FEEDS.get(ticker, ["macro"])
    keywords         = [kw.lower() for kw in TICKER_KEYWORDS.get(ticker, [])]
    headlines_vistas = set()
    headlines        = []

    for categoria in categorias:
        for feed_url in RSS_FEEDS.get(categoria, []):
            try:
                feed    = feedparser.parse(feed_url)
                entries = feed.entries[:30]

                for entry in entries:
                    titulo = entry.get("title", "").strip()
                    if not titulo:
                        continue

                    titulo_lower = titulo.lower()
                    if titulo_lower in headlines_vistas:
                        continue

                    summary     = entry.get("summary", "").lower()
                    texto_busca = titulo_lower + " " + summary
                    if not any(kw in texto_busca for kw in keywords):
                        continue

                    headlines_vistas.add(titulo_lower)
                    headlines.append({
                        "titulo": titulo,
                        "data":   _extrair_data(entry),
                        "fonte":  _extrair_fonte(feed_url),
                    })

            except Exception as e:
                logger.warning(f"Erro ao buscar feed {feed_url}: {e}")
                continue

    if not headlines:
        resultado = ""
    else:
        resultado = _formatar_headlines(headlines[:max_headlines])

    _cache[cache_key] = resultado
    return resultado


def _extrair_data(entry) -> str:
    try:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            dt       = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            dt_local = dt.astimezone(ZoneInfo("America/Sao_Paulo"))
            return dt_local.strftime("%d/%m %H:%M")
    except Exception:
        pass
    return "recente"


def _extrair_fonte(url: str) -> str:
    if "reuters"       in url: return "Reuters"
    if "investing"     in url: return "Investing.com"
    if "marketwatch"   in url: return "MarketWatch"
    if "cointelegraph" in url: return "CoinTelegraph"
    if "coindesk"      in url: return "CoinDesk"
    if "oilprice"      in url: return "OilPrice"
    if "kitco"         in url: return "Kitco"
    if "agweb"         in url: return "AgWeb"
    if "braziljournal" in url: return "Brazil Journal"
    return "Feed"


def _formatar_headlines(headlines: list) -> str:
    linhas = ["📡 NOTÍCIAS EM TEMPO REAL (RSS):"]
    for h in headlines:
        linhas.append(f"  [{h['fonte']} — {h['data']}] {h['titulo']}")
    return "\n".join(linhas)
