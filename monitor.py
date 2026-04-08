"""
monitor.py
Loop principal do robô de monitoramento de ativos.
- Respeita horário de pregão de cada ativo (UTC)
- Máximo 1 alerta por ativo por dia calendário
- Morning Call às 10:00 UTC com headlines por categoria
- Verifica a cada CHECK_INTERVAL_MINUTES minutos
"""

import schedule
import time
import logging
import sys
from datetime import datetime, timezone, date
from collections import defaultdict

from config        import ASSETS, CHECK_INTERVAL_MINUTES, MARKET_HOURS_UTC, MAX_ALERTAS_POR_DIA
from price_fetcher import get_intraday_variation
from ai_analyst    import gerar_analise
from news_fetcher  import buscar_noticias
from notifier      import enviar_alerta, enviar_heartbeat, _send

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("monitor.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# { ticker: date } — registra o dia do último alerta enviado
alertas_hoje: dict = defaultdict(lambda: None)

# Categorias e tickers representativos para o morning call
MORNING_CALL_CATEGORIAS = {
    "🌍 Global": ["^GSPC", "^IXIC", "^VIX", "DX-Y.NYB", "EURUSD=X", "BTC-USD"],
    "🇧🇷 Brasil": ["^BVSP", "USDBRL=X", "EURBRL=X"],
    "⚡ Energia":  ["CL=F", "BZ=F", "NG=F"],
    "🥇 Metais":   ["GC=F", "SI=F", "HG=F"],
    "🌾 Agrícolas":["ZS=F", "ZC=F", "ZW=F", "SB=F", "KC=F"],
}


def _mercado_aberto(market: str) -> bool:
    """Verifica se o mercado está dentro do horário de pregão (UTC)."""
    h_open, m_open, h_close, m_close = MARKET_HOURS_UTC.get(market, (0, 0, 23, 59))

    agora      = datetime.now(timezone.utc)
    dia_semana = agora.weekday()  # 0=seg … 6=dom

    if market == "crypto":
        return True

    if dia_semana >= 5:
        return False

    minutos_agora = agora.hour * 60 + agora.minute
    return (h_open * 60 + m_open) <= minutos_agora <= (h_close * 60 + m_close)


def _pode_alertar(ticker: str) -> bool:
    """Retorna True se ainda não houve alerta hoje para este ativo."""
    return alertas_hoje[ticker] != date.today()


# ── MORNING CALL ─────────────────────────────────────────────────────

def morning_call():
    """
    Envia às 10:00 UTC um resumo com headlines reais por categoria de mercado.
    Usa o news_fetcher existente — sem chamadas à IA, sem custo extra.
    """
    logger.info("📰 Gerando Morning Call...")
    data_str = datetime.now(timezone.utc).strftime("%d/%m/%Y")

    linhas = [
        f"🌅 *MORNING CALL — {data_str}*",
        f"_Principais headlines de abertura dos mercados_",
        "━━━━━━━━━━━━━━━━━━━",
    ]

    for categoria, tickers in MORNING_CALL_CATEGORIAS.items():
        headlines_categoria = []
        vistas = set()

        for ticker in tickers:
            noticias_raw = buscar_noticias(ticker, max_headlines=3)
            if not noticias_raw:
                continue
            # Extrai apenas as linhas de headline (pula o cabeçalho "📡 NOTÍCIAS...")
            for linha in noticias_raw.splitlines():
                if linha.startswith("  [") and linha not in vistas:
                    vistas.add(linha)
                    headlines_categoria.append(linha.strip())

        if headlines_categoria:
            linhas.append(f"\n{categoria}")
            for h in headlines_categoria[:4]:  # Máx 4 headlines por categoria
                linhas.append(f"• {h}")

    linhas.append("\n━━━━━━━━━━━━━━━━━━━")
    linhas.append("_⚙️ Monitor automático_")

    msg = "\n".join(linhas)
    if _send(msg):
        logger.info("✅ Morning Call enviado.")
    else:
        logger.error("❌ Falha ao enviar Morning Call.")


# ── MONITORAMENTO ────────────────────────────────────────────────────

def verificar_ativos():
    agora_str = datetime.now(timezone.utc).strftime("%H:%M UTC")
    logger.info(f"🔍 Verificando ativos... [{agora_str}]")
    disparados = 0

    for ticker, cfg in ASSETS.items():

        # 1. Pregão aberto?
        if not _mercado_aberto(cfg["market"]):
            logger.debug(f"  {cfg['nome']}: fora do pregão")
            continue

        # 2. Busca preço
        dados = get_intraday_variation(ticker)
        if dados is None:
            continue

        variacao = dados["variacao_pct"]
        preco    = dados["preco_atual"]
        abertura = dados["abertura"]

        logger.info(f"  {cfg['nome']}: {variacao:+.2f}% (threshold ±{cfg['threshold']}%)")

        # 3. Threshold atingido?
        if abs(variacao) < cfg["threshold"]:
            continue

        # 4. Já alertou hoje?
        if not _pode_alertar(ticker):
            logger.info(f"  🔇 {cfg['nome']}: alerta já enviado hoje")
            continue

        # 5. Gera análise com notícias reais
        logger.info(f"  🧠 Gerando análise para {cfg['nome']}...")
        analise = gerar_analise(cfg["nome"], ticker, cfg["tipo"], variacao, preco)

        # 6. Envia alerta
        if enviar_alerta(cfg["nome"], ticker, variacao, preco, abertura, analise):
            alertas_hoje[ticker] = date.today()
            disparados += 1
            logger.info(f"  ✅ Alerta enviado: {cfg['nome']} {variacao:+.2f}%")
        else:
            logger.error(f"  ❌ Falha ao enviar: {cfg['nome']}")

        time.sleep(5)

    if disparados == 0:
        logger.info("  → Nenhum alerta disparado.")
    else:
        logger.info(f"  → {disparados} alerta(s) enviado(s).")


# ── MAIN ─────────────────────────────────────────────────────────────

def main():
    logger.info("=" * 50)
    logger.info("  🤖 MARKET MONITOR INICIADO")
    logger.info(f"  📊 Ativos: {len(ASSETS)}")
    logger.info(f"  ⏱️  Intervalo: {CHECK_INTERVAL_MINUTES} min")
    logger.info(f"  🌍 Horários de pregão em UTC")
    logger.info(f"  📰 Morning Call: 10:00 UTC")
    logger.info("=" * 50)

    enviar_heartbeat()

    schedule.every().day.at("00:01").do(enviar_heartbeat)
    schedule.every().day.at("10:00").do(morning_call)
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(verificar_ativos)

    verificar_ativos()

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
