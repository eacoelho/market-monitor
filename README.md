# 🤖 Market Monitor

Monitor automático de 32 ativos com alertas via Telegram.
Usa **Gemini 2.0 Flash** ou **Groq (Llama 3.3)** + **RSS gratuito** para análise em tempo real.
Custo: R$ 0,00/mês.

## Arquivos

| Arquivo | Função |
|---|---|
| `config.py` | ⚙️ Chaves, ativos, thresholds e horários de pregão |
| `monitor.py` | Loop principal |
| `price_fetcher.py` | Preços intraday via yfinance (UTC) |
| `news_fetcher.py` | Headlines em tempo real via RSS |
| `ai_analyst.py` | Gemini / Groq com fallback automático |
| `notifier.py` | Alertas via Telegram |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nano config.py        # preencher chaves
python monitor.py     # testar

# Produção
sudo cp market-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now market-monitor
```

## Credenciais

| Serviço | Onde obter |
|---|---|
| Gemini API | https://aistudio.google.com/apikey |
| Groq API | https://console.groq.com/keys |
| Telegram Bot | @BotFather |

## Comandos úteis

```bash
tail -f monitor.log
sudo systemctl restart market-monitor
sudo systemctl status market-monitor
```
