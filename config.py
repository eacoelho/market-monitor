# ============================================================
#  CONFIGURAÇÕES DO MONITOR — edite aqui para personalizar
# ============================================================

# --- Provider de IA ---
# "gemini" → Google Gemini 2.0 Flash (1.500 req/dia grátis)
# "groq"   → Groq Llama 3.3 70B     (14.400 req/dia grátis)
AI_PROVIDER = "gemini"

# --- Chaves de API (preencha apenas o provider que for usar) ---
GEMINI_API_KEY = "SUA_CHAVE_GEMINI_AQUI"   # https://aistudio.google.com/apikey
GROQ_API_KEY   = "SUA_CHAVE_GROQ_AQUI"     # https://console.groq.com/keys

# --- CallMeBot WhatsApp ---
# Setup: https://www.callmebot.com/blog/free-api-whatsapp-messages/
# 1. Salve +34 644 44 74 67 nos contatos
# 2. Envie "I allow callmebot to send me messages" por WhatsApp
# 3. Aguarde a apikey chegar (~2 min)
TELEGRAM_TOKEN   = "SEU_NOVO_TOKEN_AQUI"   # Token novo gerado pelo BotFather
TELEGRAM_CHAT_ID = "8100324093"

# --- Intervalo e horário de operação ---
CHECK_INTERVAL_MINUTES = 5
HORARIO_INICIO         = "08:00"
HORARIO_FIM            = "22:00"

# --- Controle anti-spam ---
MAX_ALERTAS_POR_HORA = 1                    # Máximo de alertas por ativo por hora

# --- Ativos monitorados ---
# threshold: variação mínima (%) para disparar alerta
# tipo     : contexto passado à IA para enriquecer a análise
ASSETS = {
    # Moedas
    "USDBRL=X": {
        "nome":      "Dólar / Real (USD/BRL)",
        "threshold": 0.8,
        "tipo":      "par de moedas emergentes, muito sensível ao cenário fiscal brasileiro e ao dólar global",
    },
    "EURBRL=X": {
        "nome":      "Euro / Real (EUR/BRL)",
        "threshold": 0.8,
        "tipo":      "par de moedas, influenciado pelo BCE e pelo cenário fiscal brasileiro",
    },
    "EURUSD=X": {
        "nome":      "Euro / Dólar (EUR/USD)",
        "threshold": 0.5,
        "tipo":      "principal par de forex global, muito sensível ao Fed e BCE",
    },
    "BTC-USD": {
        "nome":      "Bitcoin (BTC/USD)",
        "threshold": 3.0,
        "tipo":      "criptomoeda líder, sensível a regulação, macro e fluxo de ETFs",
    },
    # Commodities
    "GC=F": {
        "nome":      "Ouro (Gold Futures)",
        "threshold": 1.0,
        "tipo":      "commodity refúgio, sensível ao dólar, juros reais e geopolítica",
    },
    "CL=F": {
        "nome":      "Petróleo WTI (Crude Oil)",
        "threshold": 1.5,
        "tipo":      "commodity energética, sensível à OPEP, estoques EIA e geopolítica",
    },
    "SI=F": {
        "nome":      "Prata (Silver Futures)",
        "threshold": 1.5,
        "tipo":      "commodity metálica com uso industrial e reserva de valor",
    },
    "ZC=F": {
        "nome":      "Milho (Corn Futures)",
        "threshold": 1.5,
        "tipo":      "commodity agrícola, sensível ao clima no Midwest e exportações",
    },
    "ZS=F": {
        "nome":      "Soja (Soybean Futures)",
        "threshold": 1.5,
        "tipo":      "commodity agrícola estratégica para o Brasil, sensível à demanda chinesa",
    },
    "SB=F": {
        "nome":      "Açúcar (Sugar Futures)",
        "threshold": 1.5,
        "tipo":      "commodity agrícola, sensível ao câmbio brasileiro e produção da Índia",
    },
}
