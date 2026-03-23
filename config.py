# ============================================================
#  CONFIGURAÇÕES DO MONITOR — edite aqui para personalizar
# ============================================================

# --- Perplexity API ---
PERPLEXITY_API_KEY = "SUA_CHAVE_PERPLEXITY_AQUI"  # https://www.perplexity.ai/settings/api

# --- CallMeBot WhatsApp ---
# Siga: https://www.callmebot.com/blog/free-api-whatsapp-messages/
# 1. Adicione +34 644 44 74 67 nos seus contatos
# 2. Envie "I allow callmebot to send me messages" no WhatsApp para esse número
# 3. Você receberá uma apikey por mensagem
CALLMEBOT_PHONE  = "5511999999999"   # Seu número com DDI, sem + e sem espaços
CALLMEBOT_APIKEY = "SUA_APIKEY_CALLMEBOT_AQUI"

# --- Intervalo de verificação ---
CHECK_INTERVAL_MINUTES = 5           # A cada quantos minutos verificar

# --- Horário de operação (evita alertas de madrugada) ---
HORARIO_INICIO = "08:00"             # Começa a monitorar
HORARIO_FIM    = "22:00"             # Para de monitorar

# --- Ativos monitorados ---
# ticker   : código do Yahoo Finance
# nome     : nome amigável para a mensagem
# threshold: variação mínima (%) para disparar alerta
# tipo     : contexto para a IA entender o ativo
ASSETS = {
    # --- Moedas ---
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

    # --- Commodities ---
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

# --- Controle anti-spam ---
# Máximo de alertas por ativo por janela de tempo
MAX_ALERTAS_POR_HORA = 1             # Máximo 1 alerta por ativo a cada hora
