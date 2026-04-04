"""
monitor.py
Loop principal do robô de monitoramento de ativos.
Verifica preços a cada N minutos e dispara alertas via Telegram
quando a variação intraday superar o threshold configurado.
"""

import schedule
import time
import logging
import sys
from datetime import datetime, timedelta
from collections import defaultdict

from config        import ASSETS, CHECK_INTERVAL_MINUTES, HORARIO_INICIO, HORARIO_FIM, MAX_ALERTAS_POR_HORA
from price_fetcher import get_intraday_variation
from ai_analyst    import gerar_analise
from notifier      import enviar_alerta, enviar_heartbeat

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

historico_alertas: dict = defaultdict(list)


def _dentro_do_horario() -> bool:
    agora = datetime.now().strftime("%H:%M")
    return HORARIO_INICIO <= agora <= HORARIO_FIM


def _pode_alertar(ticker: str) -> bool:
    agora  = datetime.now()
    janela = agora - timedelta(hours=1)
    historico_alertas[ticker] = [t for t in historico_alertas[ticker] if t > janela]
    return len(historico_alertas[ticker]) < MAX_ALERTAS_POR_HORA


def verificar_ativos():
    if not _dentro_do_horario():
        logger.debug(f"Fora do horário ({HORARIO_INICIO}–{HORARIO_FIM}). Pulando.")
        return

    logger.info(f"🔍 Verificando {len(ASSETS)} ativos...")
    alertas_disparados = 0

    for ticker, cfg in ASSETS.items():
        dados = get_intraday_variation(ticker)
        if dados is None:
            continue

        variacao = dados["variacao_pct"]
        preco    = dados["preco_atual"]
        abertura = dados["abertura"]

        logger.info(f"  {cfg['nome']}: {variacao:+.2f}% (threshold: ±{cfg['threshold']}%)")

        if abs(variacao) < cfg["threshold"]:
            continue

        if not _pode_alertar(ticker):
            logger.info(f"  🔇 Anti-spam ativo para {cfg['nome']}")
            continue

        logger.info(f"  🧠 Gerando análise para {cfg['nome']}...")
        analise = gerar_analise(cfg["nome"], ticker, cfg["tipo"], variacao, preco)

        sucesso = enviar_alerta(cfg["nome"], ticker, variacao, preco, abertura, analise)
        if sucesso:
            historico_alertas[ticker].append(datetime.now())
            alertas_disparados += 1
            logger.info(f"  ✅ Alerta enviado: {cfg['nome']} {variacao:+.2f}%")
        else:
            logger.error(f"  ❌ Falha ao enviar: {cfg['nome']}")

        time.sleep(8)  # Pausa entre chamadas à API (evita rate limit)

    if alertas_disparados == 0:
        logger.info("  → Nenhum alerta disparado nesta rodada.")
    else:
        logger.info(f"  → {alertas_disparados} alerta(s) enviado(s).")


def main():
    logger.info("=" * 50)
    logger.info("  🤖 MARKET MONITOR INICIADO")
    logger.info(f"  📊 Ativos: {len(ASSETS)}")
    logger.info(f"  ⏱️  Intervalo: {CHECK_INTERVAL_MINUTES} min")
    logger.info(f"  🕐 Horário: {HORARIO_INICIO} – {HORARIO_FIM}")
    logger.info("=" * 50)

    schedule.every().day.at("08:00").do(enviar_heartbeat)
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(verificar_ativos)

    verificar_ativos()  # Roda imediatamente ao iniciar

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
