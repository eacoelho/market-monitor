# ============================================================
#  CONFIGURAÇÕES DO MONITOR — edite aqui para personalizar
# ============================================================

# --- Provider de IA ---
# "gemini" → Google Gemini 2.0 Flash (1.500 req/dia grátis)
# "groq"   → Groq Llama 3.3 70B     (14.400 req/dia grátis)
AI_PROVIDER = "groq"

GEMINI_API_KEY = "SUA_CHAVE_GEMINI_AQUI"   # https://aistudio.google.com/apikey
GROQ_API_KEY   = "SUA_CHAVE_GROQ_AQUI"     # https://console.groq.com/keys

# --- Telegram ---
TELEGRAM_TOKEN   = "SEU_TOKEN_AQUI"        # Gerado pelo @BotFather
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"      # Obtido via /getUpdates

# --- Intervalo e horário de operação ---
CHECK_INTERVAL_MINUTES = 5
HORARIO_INICIO         = "08:00"
HORARIO_FIM            = "22:00"

# --- Controle anti-spam ---
MAX_ALERTAS_POR_HORA = 1

# --- Ativos monitorados ---
ASSETS = {

    # ── MOEDAS ──────────────────────────────────────────────────────
    "USDBRL=X": {
        "nome":      "Dólar / Real (USD/BRL)",
        "threshold": 0.8,
        "tipo":      "par de moedas emergentes, sensível ao cenário fiscal brasileiro e ao dólar global",
    },
    "EURBRL=X": {
        "nome":      "Euro / Real (EUR/BRL)",
        "threshold": 0.8,
        "tipo":      "par de moedas, influenciado pelo BCE e pelo cenário fiscal brasileiro",
    },
    "EURUSD=X": {
        "nome":      "Euro / Dólar (EUR/USD)",
        "threshold": 0.5,
        "tipo":      "principal par de forex global, sensível ao Fed e BCE",
    },
    "BTC-USD": {
        "nome":      "Bitcoin (BTC/USD)",
        "threshold": 3.0,
        "tipo":      "criptomoeda líder, sensível a regulação, macro e fluxo de ETFs",
    },

    # ── ÍNDICE DO DÓLAR E VOLATILIDADE ──────────────────────────────
    "DX-Y.NYB": {
        "nome":      "Índice do Dólar (DXY)",
        "threshold": 0.5,
        "tipo":      "índice do dólar contra cesta de moedas, termômetro do apetite global a risco",
    },
    "^VIX": {
        "nome":      "VIX (Volatilidade S&P 500)",
        "threshold": 5.0,
        "tipo":      "índice de medo do mercado, sobe em crises e cai em rallies de risco",
    },

    # ── ÍNDICES — EUA ────────────────────────────────────────────────
    "^GSPC": {
        "nome":      "S&P 500",
        "threshold": 1.0,
        "tipo":      "principal índice de ações dos EUA, referência global de risco",
    },
    "^IXIC": {
        "nome":      "Nasdaq Composite",
        "threshold": 1.2,
        "tipo":      "índice de tecnologia dos EUA, muito sensível a juros e resultados de big techs",
    },
    "^DJI": {
        "nome":      "Dow Jones Industrial",
        "threshold": 1.0,
        "tipo":      "índice das 30 maiores empresas industriais dos EUA",
    },
    "^RUT": {
        "nome":      "Russell 2000",
        "threshold": 1.5,
        "tipo":      "índice de small caps dos EUA, barômetro da economia doméstica americana",
    },

    # ── ÍNDICES — EUROPA ─────────────────────────────────────────────
    "^STOXX50E": {
        "nome":      "Euro Stoxx 50 (Europa)",
        "threshold": 1.0,
        "tipo":      "índice das 50 maiores empresas da zona do euro",
    },
    "^FTSE": {
        "nome":      "FTSE 100 (Reino Unido)",
        "threshold": 1.0,
        "tipo":      "principal índice de ações do Reino Unido, sensível ao petróleo e mineração",
    },

    # ── ÍNDICES — ÁSIA ───────────────────────────────────────────────
    "^N225": {
        "nome":      "Nikkei 225 (Japão)",
        "threshold": 1.0,
        "tipo":      "principal índice japonês, sensível ao iene e exportações",
    },
    "000001.SS": {
        "nome":      "Shanghai Composite (China)",
        "threshold": 1.0,
        "tipo":      "principal índice chinês, sensível a estímulos do governo e dados de atividade",
    },
    "^HSI": {
        "nome":      "Hang Seng (Hong Kong)",
        "threshold": 1.0,
        "tipo":      "índice de Hong Kong, termômetro do fluxo de capital para a China",
    },

    # ── ÍNDICES — BRASIL ─────────────────────────────────────────────
    "^BVSP": {
        "nome":      "Ibovespa (Brasil)",
        "threshold": 1.0,
        "tipo":      "principal índice de ações brasileiro, sensível ao câmbio, commodities e fiscal",
    },

    # ── METAIS ───────────────────────────────────────────────────────
    "GC=F": {
        "nome":      "Ouro (Gold Futures)",
        "threshold": 1.0,
        "tipo":      "commodity refúgio, sensível ao dólar, juros reais e geopolítica",
    },
    "SI=F": {
        "nome":      "Prata (Silver Futures)",
        "threshold": 1.5,
        "tipo":      "commodity metálica com uso industrial e reserva de valor",
    },
    "HG=F": {
        "nome":      "Cobre (Copper Futures)",
        "threshold": 1.5,
        "tipo":      "commodity industrial, barômetro da atividade econômica global, muito sensível à China",
    },

    # ── ENERGIA ──────────────────────────────────────────────────────
    "CL=F": {
        "nome":      "Petróleo WTI (Crude Oil)",
        "threshold": 1.5,
        "tipo":      "referência de petróleo nos EUA, sensível à OPEP, estoques EIA e geopolítica",
    },
    "BZ=F": {
        "nome":      "Petróleo Brent",
        "threshold": 1.5,
        "tipo":      "referência global de petróleo, sensível à geopolítica do Oriente Médio e OPEP+",
    },
    "NG=F": {
        "nome":      "Gás Natural (Natural Gas)",
        "threshold": 2.0,
        "tipo":      "commodity energética volátil, sensível a clima, estoques EIA e demanda europeia",
    },
    "RB=F": {
        "nome":      "Gasolina (RBOB Gasoline)",
        "threshold": 1.5,
        "tipo":      "derivado do petróleo, sensível à demanda de verão nos EUA e margens de refino",
    },

    # ── GRÃOS E OLEAGINOSAS — CBOT ───────────────────────────────────
    "ZS=F": {
        "nome":      "Soja CBOT (Soybean Futures)",
        "threshold": 1.5,
        "tipo":      "commodity agrícola estratégica para o Brasil, sensível à demanda chinesa e clima",
    },
    "ZC=F": {
        "nome":      "Milho CBOT (Corn Futures)",
        "threshold": 1.5,
        "tipo":      "commodity agrícola, sensível ao clima no Midwest, etanol e exportações dos EUA",
    },
    "ZW=F": {
        "nome":      "Trigo CBOT (Wheat Futures)",
        "threshold": 1.5,
        "tipo":      "commodity agrícola, sensível à geopolítica (Rússia/Ucrânia) e clima global",
    },
    "ZM=F": {
        "nome":      "Farelo de Soja CBOT (Soybean Meal)",
        "threshold": 1.5,
        "tipo":      "subproduto da soja, demanda ligada à proteína animal e crushing de soja",
    },
    "ZL=F": {
        "nome":      "Óleo de Soja CBOT (Soybean Oil)",
        "threshold": 1.5,
        "tipo":      "subproduto da soja, sensível à demanda de biodiesel e consumo alimentar",
    },

    # ── SOFTS ────────────────────────────────────────────────────────
    "CT=F": {
        "nome":      "Algodão NY (Cotton Futures)",
        "threshold": 1.5,
        "tipo":      "commodity têxtil, sensível à demanda asiática, clima nos EUA e Brasil",
    },
    "SB=F": {
        "nome":      "Açúcar NY (Sugar #11)",
        "threshold": 1.5,
        "tipo":      "commodity agrícola, sensível ao câmbio brasileiro, produção da Índia e etanol",
    },
    "KC=F": {
        "nome":      "Café NY (Coffee Arabica)",
        "threshold": 1.5,
        "tipo":      "commodity agrícola, sensível ao clima no Brasil e Colômbia e demanda global",
    },
    "RC=F": {
        "nome":      "Café Robusta ICE (Coffee Robusta)",
        "threshold": 1.5,
        "tipo":      "café de menor qualidade, sensível à produção do Vietnã e demanda de solúvel",
    },
}
