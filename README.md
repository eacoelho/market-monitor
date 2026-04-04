# 🤖 Market Monitor — Guia de Deploy no VPS

Monitor automático de moedas e commodities com alertas via WhatsApp.
Usa **Gemini 2.0 Flash** ou **Groq (Llama 3.3)** + **RSS gratuito** para análise em tempo real.
Custo total: **R$ 0,00/mês**.

---

## 📁 Estrutura do Projeto

```
market-monitor/
├── config.py                ← ⚙️  EDITE AQUI (provider, chaves, ativos)
├── monitor.py               ← Loop principal
├── price_fetcher.py         ← Busca preços (Yahoo Finance)
├── news_fetcher.py          ← Busca headlines reais via RSS (gratuito)
├── ai_analyst.py            ← Análise com Gemini ou Groq
├── notifier.py              ← Envia WhatsApp via CallMeBot
├── requirements.txt         ← Dependências Python
└── market-monitor.service   ← Serviço systemd (auto-start no VPS)
```

---

## 🔑 PASSO 1 — Obter credenciais (tudo gratuito)

### Opção A: Google Gemini (recomendado)
1. Acesse https://aistudio.google.com/apikey
2. Clique em **Create API Key**
3. Copie a chave gerada

### Opção B: Groq
1. Acesse https://console.groq.com/keys
2. Clique em **Create API Key**
3. Copie a chave gerada

### CallMeBot WhatsApp
1. Salve o número **+34 644 44 74 67** nos contatos do celular
2. Envie exatamente esta mensagem pelo WhatsApp para esse número:
   ```
   I allow callmebot to send me messages
   ```
3. Aguarde a resposta com sua **apikey** (~2 minutos)

---

## ⚙️ PASSO 2 — Editar o config.py

```python
AI_PROVIDER    = "gemini"              # ou "groq"
GEMINI_API_KEY = "AIza..."             # sua chave Gemini
GROQ_API_KEY   = "gsk_..."            # sua chave Groq (se usar)

CALLMEBOT_PHONE  = "5511999999999"    # DDI + número, sem + nem espaços
CALLMEBOT_APIKEY = "1234567"          # apikey recebida pelo WhatsApp
```

---

## 🖥️ PASSO 3 — Setup no VPS (Ubuntu 22.04+)

```bash
# Conectar ao VPS
ssh ubuntu@SEU_IP

# Atualizar sistema
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv -y

# Copiar projeto (ajuste o caminho conforme necessário)
mkdir ~/market-monitor
cd ~/market-monitor
# cole os arquivos via scp, git clone, ou editor de texto

# Criar ambiente virtual e instalar dependências
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🧪 PASSO 4 — Testar

```bash
source venv/bin/activate
python monitor.py
```

Saída esperada:
```
🤖 MARKET MONITOR INICIADO
📊 Ativos: 10
⏱️  Intervalo: 5 min
🔍 Verificando 10 ativos...
  Dólar / Real: +0.32% (threshold: ±0.8%)
  ...
```

---

## 🚀 PASSO 5 — Rodar como serviço permanente

```bash
# Ajuste o usuário no arquivo se necessário
sudo cp market-monitor.service /etc/systemd/system/

# Ativar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable market-monitor
sudo systemctl start market-monitor

# Verificar status
sudo systemctl status market-monitor
```

### Comandos úteis

```bash
# Logs em tempo real
sudo journalctl -u market-monitor -f

# Últimas 50 linhas do log local
tail -50 ~/market-monitor/monitor.log

# Reiniciar após editar config.py
sudo systemctl restart market-monitor
```

---

## 📱 Exemplo de mensagem recebida

```
🔴 ALERTA DE MERCADO 🔴
━━━━━━━━━━━━━━━━━━━
Dólar / Real (USD/BRL)
📊 Variação: -1.24% no intraday
💰 Preço atual: R$ 5.1230
📂 Abertura: R$ 5.1874
🕐 14/03 10:47
━━━━━━━━━━━━━━━━━━━
📌 CAUSA PRINCIPAL
Ata do Copom mais hawkish reforçou expectativa de juros altos...

📰 CONTEXTO DO MOMENTO
• [Reuters 10:31] BC manteve tom firme sobre Selic elevada
• Fluxo externo para renda fixa brasileira acelerou
• DXY recuando 0.3% após dados de emprego nos EUA

🎯 O QUE MONITORAR AGORA
Discurso do presidente do Fed às 15h e resultado do leilão...

⚠️ NÍVEL DE CONVICÇÃO
Alta — baseado em 3 headlines Reuters confirmando o movimento
━━━━━━━━━━━━━━━━━━━
⚙️ Monitor automático — verifique antes de operar.
```

---

## 💰 Custo total mensal: R$ 0,00

| Componente | Solução | Custo |
|---|---|---|
| Preços de mercado | Yahoo Finance (yfinance) | Grátis |
| Notícias em tempo real | RSS (Reuters, Investing.com) | Grátis |
| Inteligência Artificial | Gemini 2.0 Flash ou Groq | Grátis |
| Alertas WhatsApp | CallMeBot | Grátis |
| Servidor VPS | Oracle Cloud Free Tier | Grátis |
