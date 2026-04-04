# 🤖 Market Monitor

Monitor automático de moedas e commodities com alertas via Telegram.
Usa **Groq (Llama 3.3)** ou **Gemini 2.0 Flash** + **RSS gratuito** para análise em tempo real.
Custo total: **R$ 0,00/mês**.

---

## 📁 Arquivos

| Arquivo | Função |
|---|---|
| `config.py` | ⚙️ Chaves, ativos e thresholds — **edite aqui** |
| `monitor.py` | Loop principal com scheduler e anti-spam |
| `price_fetcher.py` | Preços intraday via yfinance |
| `news_fetcher.py` | Headlines em tempo real via RSS |
| `ai_analyst.py` | Groq / Gemini com fallback automático |
| `notifier.py` | Alertas via Telegram |
| `requirements.txt` | Dependências Python |
| `market-monitor.service` | Serviço systemd para VPS |

---

## 🔑 Credenciais necessárias

| Serviço | Onde obter | Custo |
|---|---|---|
| Groq API | https://console.groq.com/keys | Grátis |
| Gemini API | https://aistudio.google.com/apikey | Grátis |
| Telegram Bot | @BotFather no Telegram | Grátis |

---

## 🚀 Deploy no VPS

```bash
# 1. Instalar dependências
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Editar credenciais
nano config.py

# 3. Testar
python monitor.py

# 4. Subir como serviço permanente
sudo cp market-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now market-monitor
```

## Comandos úteis

```bash
# Logs em tempo real
tail -f monitor.log

# Reiniciar após editar config.py
sudo systemctl restart market-monitor

# Status do serviço
sudo systemctl status market-monitor
```
