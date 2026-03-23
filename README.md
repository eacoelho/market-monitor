# 🤖 Market Monitor — Guia de Deploy no VPS

Monitor automático de moedas e commodities com alertas via WhatsApp.
Usa **Perplexity sonar-pro** para buscar notícias em tempo real e explicar cada movimento.

---

## 📁 Estrutura do Projeto

```
market-monitor/
├── config.py               ← ⚙️  EDITE AQUI (chaves, ativos, thresholds)
├── monitor.py              ← Loop principal
├── price_fetcher.py        ← Busca preços (Yahoo Finance)
├── ai_analyst.py           ← Análise com Perplexity sonar-pro
├── notifier.py             ← Envia WhatsApp via CallMeBot
├── requirements.txt        ← Dependências Python
└── market-monitor.service  ← Serviço systemd (auto-start)
```

---

## 🔑 PASSO 1 — Obter as credenciais

### Perplexity API
1. Acesse https://www.perplexity.ai/settings/api
2. Crie uma conta e gere uma API Key
3. O modelo `sonar-pro` custa ~$3/1000 chamadas — para 5 ativos verificados a cada 5min, gasta ~$5–15/mês

### CallMeBot WhatsApp (gratuito)
1. Salve o número **+34 644 44 74 67** como contato no seu celular
2. Envie a mensagem exata pelo WhatsApp:
   ```
   I allow callmebot to send me messages
   ```
3. Aguarde a resposta com sua **apikey** (chega em ~2 minutos)
4. Anote o número e a apikey

---

## 🖥️ PASSO 2 — Configurar o VPS

### Opções recomendadas (gratuitas ou baratas)
| Provedor | Plano | Custo |
|---|---|---|
| Oracle Cloud | Always Free (1 OCPU, 1GB RAM) | Grátis |
| DigitalOcean | Droplet Basic | ~$6/mês |
| Hetzner | CX11 | ~€3.29/mês |

### Setup inicial (Ubuntu 22.04+)
```bash
# Conectar ao VPS
ssh ubuntu@SEU_IP_DO_VPS

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e pip
sudo apt install python3 python3-pip python3-venv git -y

# Clonar / copiar projeto
mkdir ~/market-monitor
cd ~/market-monitor
# (copie os arquivos via scp ou git clone)
```

---

## ⚙️ PASSO 3 — Instalar dependências

```bash
cd ~/market-monitor

# Criar ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate

# Instalar bibliotecas
pip install -r requirements.txt
```

---

## 🔧 PASSO 4 — Editar o config.py

```bash
nano config.py
```

Preencha:
```python
PERPLEXITY_API_KEY = "pplx-xxxxxxxxxxxxxxxxxxxx"
CALLMEBOT_PHONE    = "5511999999999"   # sem + e sem espaços
CALLMEBOT_APIKEY   = "1234567"
```

Salve com `Ctrl+O`, `Enter`, `Ctrl+X`.

---

## 🧪 PASSO 5 — Testar antes de subir em produção

```bash
# Ativar venv se não estiver ativo
source venv/bin/activate

# Teste rápido (roda uma vez e mostra no terminal)
python monitor.py
```

Você deve ver no terminal:
```
🤖 MARKET MONITOR INICIADO
📊 Ativos: 10
⏱️  Intervalo: 5 minutos
🔍 Verificando 10 ativos...
  Dólar / Real: +0.32% (threshold: ±0.8%)
  ...
```

E se algum ativo ultrapassar o threshold, receberá o WhatsApp!

---

## 🚀 PASSO 6 — Rodar como serviço (auto-start + sempre ativo)

```bash
# Copiar arquivo de serviço
sudo cp market-monitor.service /etc/systemd/system/

# Editar o usuário se não for 'ubuntu'
sudo nano /etc/systemd/system/market-monitor.service
# Ajuste: User=SEU_USUARIO e WorkingDirectory/ExecStart com o caminho correto

# Ativar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable market-monitor
sudo systemctl start market-monitor

# Verificar se está rodando
sudo systemctl status market-monitor
```

### Comandos úteis no dia a dia
```bash
# Ver logs em tempo real
sudo journalctl -u market-monitor -f

# Ver últimas 50 linhas do log
tail -50 ~/market-monitor/monitor.log

# Reiniciar após editar config.py
sudo systemctl restart market-monitor

# Parar o robô
sudo systemctl stop market-monitor
```

---

## 📱 Exemplo de mensagem que você receberá

```
🔴 ALERTA DE MERCADO 🔴
━━━━━━━━━━━━━━━━━━━
Dólar / Real (USD/BRL)
📊 Variação: -1.24% no intraday
💰 Preço atual: R$ 5.1230
📂 Abertura: R$ 5.1874
🕐 Horário: 14/03 10:47
━━━━━━━━━━━━━━━━━━━
📌 CAUSA PRINCIPAL
Ata do Copom mais hawkish que o esperado...

📰 CONTEXTO DO MOMENTO
• BC manteve tom firme sobre juros elevados por mais tempo
• Fluxo de capital externo para renda fixa brasileira
• Dólar global (DXY) recuando 0.3% após payroll...

🎯 O QUE MONITORAR AGORA
Discurso do presidente do Fed às 15h e dados de...

⚠️ NÍVEL DE CONVICÇÃO: Alta — múltiplas fontes confirmam
━━━━━━━━━━━━━━━━━━━
⚙️ Monitor automático — verifique antes de operar.
```

---

## 🔧 Personalização avançada

### Adicionar novo ativo
Em `config.py`, adicione em `ASSETS`:
```python
"IBOV.SA": {
    "nome":      "Ibovespa",
    "threshold": 1.0,
    "tipo":      "índice de ações brasileiro, sensível ao câmbio e política fiscal",
},
```

### Alterar threshold de um ativo
Mude o valor de `"threshold"` — por exemplo, `0.5` para alertar a partir de 0.5% de variação.

### Mudar intervalo de verificação
Em `config.py`: `CHECK_INTERVAL_MINUTES = 3`

### Alertar grupo do WhatsApp
No CallMeBot há suporte a grupos. Consulte: https://www.callmebot.com/blog/free-api-whatsapp-messages/

---

## 💰 Custo estimado mensal

| Item | Custo |
|---|---|
| VPS Oracle Free Tier | Grátis |
| Perplexity API (sonar-pro) | ~$5–15/mês |
| CallMeBot WhatsApp | Grátis |
| **Total** | **~$5–15/mês** |

---

## ❓ Problemas comuns

| Sintoma | Solução |
|---|---|
| Não recebe WhatsApp | Refaça o processo do CallMeBot; verifique o número sem `+` |
| `ModuleNotFoundError` | Rode `source venv/bin/activate` antes do python |
| Análise retorna erro | Verifique a chave do Perplexity e saldo na conta |
| Dados None para ativo | Ticker incorreto — confira no Yahoo Finance |
| Serviço não sobe | `sudo journalctl -u market-monitor -n 50` para ver o erro |
