# ============================================================
#  CONFIGURAÇÕES DO MONITOR
# ============================================================

# --- Provider de IA ---
# "gemini" → Google Gemini 2.0 Flash (1.500 req/dia grátis)
# "groq"   → Groq Llama 3.3 70B     (14.400 req/dia grátis)
AI_PROVIDER = "groq"

GEMINI_API_KEY = "SUA_CHAVE_GEMINI_AQUI"   # https://aistudio.google.com/apikey
GROQ_API_KEY   = "SUA_CHAVE_GROQ_AQUI"     # https://console.groq.com/keys

# --- Telegram ---
TELEGRAM_TOKEN   = "SEU_TOKEN_AQUI"        # Gerado pelo @BotFather
TELEGRAM_CHAT_ID = "SEU_CANAL_AQUI"        # @username ou ID numérico do canal

# --- Intervalo de verificação (minutos) ---
CHECK_INTERVAL_MINUTES = 5

# --- Controle de alertas ---
MAX_ALERTAS_POR_DIA = 1   # Máximo de alertas por ativo por dia calendário

# ── HORÁRIOS DE PREGÃO POR MERCADO (UTC) ────────────────────────────
# Formato: (hora_abertura, min_abertura, hora_fechamento, min_fechamento)
# O monitor só verifica cada ativo dentro da janela do seu pregão regular.
MARKET_HOURS_UTC = {
    "forex":       ( 0,  0, 23, 59),  # Forex: 24h dias úteis
    "crypto":      ( 0,  0, 23, 59),  # Crypto: 24h, 7 dias
    "us_equities": (13, 30, 20,  0),  # NYSE/Nasdaq: 09:30–16:00 ET
    "us_futures":  (13, 30, 20,  0),  # CBOT, NYMEX, COMEX
    "eu_equities": ( 8,  0, 16, 30),  # Bolsas europeias
    "uk_equities": ( 8,  0, 16, 30),  # LSE
    "asia_japan":  ( 0,  0,  6,  0),  # Nikkei: 09:00–15:00 JST
    "asia_china":  ( 1, 30,  7,  0),  # Shanghai: 09:30–15:00 CST
    "asia_hk":     ( 1, 30,  8,  0),  # Hang Seng: 09:30–16:00 HKT
    "brazil":      (13,  0, 21,  0),  # B3: 10:00–18:00 BRT
    "ice_softs":   (10, 30, 19,  0),  # ICE Softs (KC, SB, CT, RC)
}

# ── ATIVOS MONITORADOS ───────────────────────────────────────────────
ASSETS = {

    # ── MOEDAS ──────────────────────────────────────────────────────
    "USDBRL=X": {
        "nome":      "Dólar / Real (USD/BRL)",
        "threshold": 0.8,
        "tipo":      "par de moedas emergentes, sensível ao fiscal brasileiro e dólar global",
        "market":    "forex",
    },
    "EURBRL=X": {
        "nome":      "Euro / Real (EUR/BRL)",
        "threshold": 0.8,
        "tipo":      "par de moedas influenciado pelo BCE e fiscal brasileiro",
        "market":    "forex",
    },
    "EURUSD=X": {
        "nome":      "Euro / Dólar (EUR/USD)",
        "threshold": 0.5,
        "tipo":      "principal par forex global, sensível ao Fed e BCE",
        "market":    "forex",
    },
    "BTC-USD": {
        "nome":      "Bitcoin (BTC/USD)",
        "threshold": 3.0,
        "tipo":      "criptomoeda líder, sensível a regulação, macro e ETFs",
        "market":    "crypto",
    },

    # ── ÍNDICE DO DÓLAR E VOLATILIDADE ──────────────────────────────
    "DX-Y.NYB": {
        "nome":      "Índice do Dólar (DXY)",
        "threshold": 0.5,
        "tipo":      "índice do dólar contra cesta de moedas, termômetro do apetite a risco global",
        "market":    "forex",
    },
    "^VIX": {
        "nome":      "VIX (Volatilidade S&P 500)",
        "threshold": 5.0,
        "tipo":      "índice de medo do mercado, sobe em crises e cai em rallies",
        "market":    "us_equities",
    },

    # ── ÍNDICES — EUA ────────────────────────────────────────────────
    "^GSPC": {
        "nome":      "S&P 500",
        "threshold": 1.0,
        "tipo":      "principal índice de ações dos EUA, referência global de risco",
        "market":    "us_equities",
    },
    "^IXIC": {
        "nome":      "Nasdaq Composite",
        "threshold": 1.2,
        "tipo":      "índice de tecnologia dos EUA, sensível a juros e big techs",
        "market":    "us_equities",
    },
    "^DJI": {
        "nome":      "Dow Jones Industrial",
        "threshold": 1.0,
        "tipo":      "índice das 30 maiores empresas industriais dos EUA",
        "market":    "us_equities",
    },
    "^RUT": {
        "nome":      "Russell 2000",
        "threshold": 1.5,
        "tipo":      "índice de small caps dos EUA, barômetro da economia doméstica americana",
        "market":    "us_equities",
    },

    # ── ÍNDICES — EUROPA ─────────────────────────────────────────────
    "^STOXX50E": {
        "nome":      "Euro Stoxx 50 (Europa)",
        "threshold": 1.0,
        "tipo":      "índice das 50 maiores empresas da zona do euro",
        "market":    "eu_equities",
    },
    "^FTSE": {
        "nome":      "FTSE 100 (Reino Unido)",
        "threshold": 1.0,
        "tipo":      "principal índice britânico, sensível a petróleo e mineração",
        "market":    "uk_equities",
    },

    # ── ÍNDICES — ÁSIA ───────────────────────────────────────────────
    "^N225": {
        "nome":      "Nikkei 225 (Japão)",
        "threshold": 1.0,
        "tipo":      "principal índice japonês, sensível ao iene e exportações",
        "market":    "asia_japan",
    },
    "000001.SS": {
        "nome":      "Shanghai Composite (China)",
        "threshold": 1.0,
        "tipo":      "principal índice chinês, sensível a estímulos do governo",
        "market":    "asia_china",
    },
    "^HSI": {
        "nome":      "Hang Seng (Hong Kong)",
        "threshold": 1.0,
        "tipo":      "índice de HK, termômetro do fluxo de capital para a China",
        "market":    "asia_hk",
    },

    # ── ÍNDICES — BRASIL ─────────────────────────────────────────────
    "^BVSP": {
        "nome":      "Ibovespa (Brasil)",
        "threshold": 1.0,
        "tipo":      "principal índice de ações brasileiro, sensível ao câmbio e fiscal",
        "market":    "brazil",
    },

    # ── METAIS ───────────────────────────────────────────────────────
    "GC=F": {
        "nome":      "Ouro (Gold Futures)",
        "threshold": 1.0,
        "tipo":      "commodity refúgio, sensível ao dólar, juros reais e geopolítica",
        "market":    "us_futures",
    },
    "SI=F": {
        "nome":      "Prata (Silver Futures)",
        "threshold": 1.5,
        "tipo":      "metal com uso industrial e reserva de valor",
        "market":    "us_futures",
    },
    "HG=F": {
        "nome":      "Cobre (Copper Futures)",
        "threshold": 1.5,
        "tipo":      "barômetro da atividade econômica global, muito sensível à China",
        "market":    "us_futures",
    },

    # ── ENERGIA ──────────────────────────────────────────────────────
    "CL=F": {
        "nome":      "Petróleo WTI (Crude Oil)",
        "threshold": 1.5,
        "tipo":      "referência de petróleo nos EUA, sensível à OPEP e estoques EIA",
        "market":    "us_futures",
    },
    "BZ=F": {
        "nome":      "Petróleo Brent",
        "threshold": 1.5,
        "tipo":      "referência global de petróleo, sensível ao Oriente Médio e OPEP+",
        "market":    "us_futures",
    },
    "NG=F": {
        "nome":      "Gás Natural",
        "threshold": 2.0,
        "tipo":      "commodity energética volátil, sensível a clima e estoques EIA",
        "market":    "us_futures",
    },
    "RB=F": {
        "nome":      "Gasolina (RBOB)",
        "threshold": 1.5,
        "tipo":      "derivado do petróleo, sensível à demanda dos EUA e margens de refino",
        "market":    "us_futures",
    },

    # ── GRÃOS E OLEAGINOSAS — CBOT ───────────────────────────────────
    "ZS=F": {
        "nome":      "Soja CBOT",
        "threshold": 1.5,
        "tipo":      "commodity estratégica para o Brasil, sensível à demanda chinesa",
        "market":    "us_futures",
    },
    "ZC=F": {
        "nome":      "Milho CBOT",
        "threshold": 1.5,
        "tipo":      "commodity agrícola, sensível ao clima no Midwest e etanol",
        "market":    "us_futures",
    },
    "ZW=F": {
        "nome":      "Trigo CBOT",
        "threshold": 1.5,
        "tipo":      "commodity agrícola, sensível à geopolítica Rússia/Ucrânia e clima",
        "market":    "us_futures",
    },
    "ZM=F": {
        "nome":      "Farelo de Soja CBOT",
        "threshold": 1.5,
        "tipo":      "subproduto da soja, demanda ligada à proteína animal",
        "market":    "us_futures",
    },
    "ZL=F": {
        "nome":      "Óleo de Soja CBOT",
        "threshold": 1.5,
        "tipo":      "subproduto da soja, sensível à demanda de biodiesel",
        "market":    "us_futures",
    },

    # ── SOFTS ────────────────────────────────────────────────────────
    "CT=F": {
        "nome":      "Algodão NY",
        "threshold": 1.5,
        "tipo":      "commodity têxtil, sensível à demanda asiática e clima nos EUA",
        "market":    "ice_softs",
    },
    "SB=F": {
        "nome":      "Açúcar NY (Sugar #11)",
        "threshold": 1.5,
        "tipo":      "sensível ao câmbio brasileiro, produção da Índia e etanol",
        "market":    "ice_softs",
    },
    "KC=F": {
        "nome":      "Café Arábica NY",
        "threshold": 1.5,
        "tipo":      "sensível ao clima no Brasil e Colômbia e demanda global",
        "market":    "ice_softs",
    },
}
