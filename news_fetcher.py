"""
news_fetcher.py
Busca headlines reais via RSS gratuito e filtra por relevância para cada ativo.
Sem API key — 100% gratuito. Cache de 5 minutos em memória.
"""

import feedparser
import logging
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

RSS_FEEDS = {
    "macro": [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://feeds.reuters.com/reuters/topNews",
        "https://feeds.marketwatch.com/marketwatch/realtimeheadlines/",
        "https://www.investing.com/rss/news_25.rss",
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
    ],
    "acoes": [
        "https://feeds.marketwatch.com/marketwatch/realtimeheadlines/",
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.investing.com/rss/news_25.rss",
    ],
    "asia": [
        "https://feeds.reuters.com/reuters/topNews",
        "https://www.investing.com/rss/news_95.rss",
    ],
}

TICKER_FEEDS = {
    "USDBRL=X":  ["macro", "brasil"],
    "EURBRL=X":  ["macro", "brasil"],
    "EURUSD=X":  ["macro"],
    "BTC-USD":   ["crypto"],
    "DX-Y.NYB":  ["macro"],
    "^VIX":      ["macro", "acoes"],
    "^GSPC":     ["macro", "acoes"],
    "^IXIC":     ["macro", "acoes"],
    "^DJI":      ["macro", "acoes"],
    "^RUT":      ["macro", "acoes"],
    "^STOXX50E": ["macro", "acoes"],
    "^FTSE":     ["macro", "acoes"],
    "^N225":     ["macro", "asia"],
    "000001.SS": ["macro", "asia"],
    "^HSI":      ["macro", "asia"],
    "^BVSP":     ["macro", "brasil"],
    "GC=F":      ["metais", "macro"],
    "SI=F":      ["metais", "macro"],
    "HG=F":      ["metais", "macro"],
    "CL=F":      ["energia", "macro"],
    "BZ=F":      ["energia", "macro"],
    "NG=F":      ["energia"],
    "RB=F":      ["energia"],
    "ZS=F":      ["agro", "brasil"],
    "ZC=F":      ["agro", "macro"],
    "ZW=F":      ["agro", "macro"],
    "ZM=F":      ["agro", "brasil"],
    "ZL=F":      ["agro", "brasil"],
    "CT=F":      ["agro", "macro"],
    "SB=F":      ["agro", "brasil"],
    "KC=F":      ["agro", "brasil"],
    "RC=F":      ["agro", "macro"],
}

TICKER_KEYWORDS = {
    "USDBRL=X":  ["real", "brl", "brazil", "brasil", "copom", "lula", "fazenda", "dollar", "fed", "dólar"],
    "EURBRL=X":  ["real", "euro", "eur", "ecb", "bce", "brazil", "brasil"],
    "EURUSD=X":  ["euro", "eur", "dollar", "usd", "fed", "ecb", "bce", "inflation", "rate"],
    "BTC-USD":   ["bitcoin", "btc", "crypto", "cryptocurrency", "sec", "etf", "blockchain"],
    "DX-Y.NYB":  ["dollar", "dxy", "dollar index", "fed", "currency", "forex"],
    "^VIX":      ["vix", "volatility", "fear", "s&p", "market", "stocks", "risk"],
    "^GSPC":     ["s&p", "s&p 500", "stocks", "wall street", "equities", "fed", "earnings"],
    "^IXIC":     ["nasdaq", "tech", "technology", "apple", "microsoft", "nvidia", "meta", "google"],
    "^DJI":      ["dow jones", "dow", "industrial", "stocks", "wall street"],
    "^RUT":      ["russell", "small cap", "smallcap", "domestic", "economy"],
    "^STOXX50E": ["stoxx", "europe", "europa", "ecb", "eurozone", "european"],
    "^FTSE":     ["ftse", "uk", "britain", "london", "boe", "pound"],
    "^N225":     ["nikkei", "japan", "japão", "yen", "boj", "tokyo"],
    "000001.SS": ["shanghai", "china", "chinese", "pboc", "beijing", "yuan", "rmb"],
    "^HSI":      ["hang seng", "hong kong", "hsi", "china", "chinese"],
    "^BVSP":     ["ibovespa", "bovespa", "brasil", "brazil", "b3", "selic", "copom"],
    "GC=F":      ["gold", "ouro", "fed", "inflation", "rate", "treasury", "yields"],
    "SI=F":      ["silver", "prata", "metal", "industrial"],
    "HG=F":      ["copper", "cobre", "china", "industrial", "manufacturing"],
    "CL=F":      ["oil", "crude", "wti", "opec", "opep", "eia", "petróleo", "energy"],
    "BZ=F":      ["brent", "oil", "crude", "opec", "opep", "middle east", "petróleo"],
    "NG=F":      ["natural gas", "gas", "lng", "storage", "weather", "winter"],
    "RB=F":      ["gasoline", "gasolina", "rbob", "refinery", "fuel"],
    "ZS=F":      ["soy", "soja", "soybean", "china", "usda", "crop", "brazil", "brasil"],
    "ZC=F":      ["corn", "milho", "grain", "usda", "crop", "ethanol"],
    "ZW=F":      ["wheat", "trigo", "grain", "russia", "ukraine", "usda"],
    "ZM=F":      ["soybean meal", "farelo", "meal", "protein", "livestock", "crush"],
    "ZL=F":      ["soybean oil", "óleo de soja", "biodiesel", "vegetable oil", "crush"],
    "CT=F":      ["cotton", "algodão", "textile", "india", "china", "usda"],
    "SB=F":      ["sugar", "açúcar", "cane", "ethanol", "india", "brazil", "brasil"],
    "KC=F":      ["coffee", "café", "arabica", "brazil", "colombia", "frost", "crop"],
    "RC=F":      ["robusta", "coffee", "café", "vietnam", "indonesia", "soluble"],
}

_cache: dict = {}
CACHE_TTL_SECONDS = 300


def buscar_noticias(ticker: str, max_headlines: int = 8) -> str:
    """
    Retorna string com headlines relevantes para embutir no prompt do LLM.
    Retorna string vazia se não encontrar nada relevante.
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
                for entry in feedparser.parse(feed_url).entries[:30]:
                    titulo = entry.get("title", "").strip()
                    if not titulo:
                        continue
                    titulo_lower = titulo.lower()
                    if titulo_lower in headlines_vistas:
                        continue
                    texto = titulo_lower + " " + entry.get("summary", "").lower()
                    if not any(kw in texto for kw in keywords):
                        continue
                    headlines_vistas.add(titulo_lower)
                    headlines.append({
                        "titulo": titulo,
                        "data":   _extrair_data(entry),
                        "fonte":  _extrair_fonte(feed_url),
                    })
            except Exception as e:
                logger.warning(f"Erro feed {feed_url}: {e}")

    resultado = _formatar(headlines[:max_headlines]) if headlines else ""
    _cache[cache_key] = resultado
    return resultado


def _extrair_data(entry) -> str:
    try:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            return dt.astimezone(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m %H:%M")
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


def _formatar(headlines: list) -> str:
    linhas = ["📡 NOTÍCIAS EM TEMPO REAL:"]
    for h in headlines:
        linhas.append(f"  [{h['fonte']} — {h['data']}] {h['titulo']}")
    return "\n".join(linhas)
