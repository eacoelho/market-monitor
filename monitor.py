"""
monitor.py
Loop principal do robô de monitoramento de ativos.
Verifica preços a cada N minutos e dispara alertas via WhatsApp
quando a variação intraday superar o threshold configurado.
"""

import schedule
import time
import logging
import sys
from datetime import datetime, timedelta
from collections import defaultdict

from config   import ASSETS, CHECK_INTERVAL_MINUTES, HORARIO_INICIO, HORARIO_FIM, MAX_ALERTAS_POR_HORA
from price_fetcher import get_intraday_variation
from ai_analyst    import gerar_analise
from notifier      import enviar_alerta, enviar_heartbeat

# --- Logging ---
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

# --- Controle anti-spam ---
# Estrutura: { ticker: [datetime_do_alerta, ...] }
historico_alertas: dict = defaultdict(list)


def _dentro_do_horario() -> bool:
    """Verifica se estamos dentro do horário de operação configurado."""
    agora     = datetime.now().strftime("%H:%M")
    return HORARIO_INICIO <= agora <= HORARIO_FIM


def _pode_alertar(ticker: str) -> bool:
    """
    Controle anti-spam: retorna True apenas se o ativo não recebeu
    alerta no último período configurado (MAX_ALERTAS_POR_HORA).
    """
    agora  = datetime.now()
    janela = agora - timedelta(hours=1)

    # Remove alertas fora da janela
    historico_alertas[ticker] = [
        t for t in historico_alertas[ticker] if t > janela
    ]

    return len(historico_alertas[ticker]) < MAX_ALERTAS_POR_HORA


def _registrar_alerta(ticker: str):
    historico_alertas[ticker].append(datetime.now())


def verificar_ativos():
    """Função principal — chamada a cada N minutos pelo scheduler."""

    if not _dentro_do_horario():
        logger.debug(f"Fora do horário de operação ({HORARIO_INICIO}–{HORARIO_FIM}). Pulando.")
        return

    logger.info(f"🔍 Verificando {len(ASSETS)} ativos...")

    alertas_disparados = 0

    for ticker, cfg in ASSETS.items():
        nome      = cfg["nome"]
        threshold = cfg["threshold"]
        tipo      = cfg["tipo"]

        # 1. Busca preço atual
        dados = get_intraday_variation(ticker)
        if dados is None:
            logger.warning(f"  ⚠️  {nome}: não foi possível obter dados")
            continue

        variacao = dados["variacao_pct"]
        preco    = dados["preco_atual"]
        abertura = dados["abertura"]

        logger.info(f"  {nome}: {variacao:+.2f}% (threshold: ±{threshold}%)")

        # 2. Verifica se ultrapassou o threshold
        if abs(variacao) < threshold:
            continue

        # 3. Verifica anti-spam
        if not _pode_alertar(ticker):
            logger.info(f"  🔇 {nome}: alerta suprimido (anti-spam ativo)")
            continue

        # 4. Gera análise com Perplexity
        logger.info(f"  🧠 Gerando análise Perplexity para {nome}...")
        analise = gerar_analise(nome, ticker, tipo, variacao, preco)

        # 5. Envia alerta no WhatsApp
        sucesso = enviar_alerta(nome, ticker, variacao, preco, abertura, analise)

        if sucesso:
            _registrar_alerta(ticker)
            alertas_disparados += 1
            logger.info(f"  ✅ Alerta enviado: {nome} {variacao:+.2f}%")
        else:
            logger.error(f"  ❌ Falha ao enviar alerta de {nome}")

        # Pequena pausa entre chamadas à API para não sobrecarregar
        time.sleep(2)

    if alertas_disparados == 0:
        logger.info("  → Nenhum alerta disparado nesta rodada.")
    else:
        logger.info(f"  → {alertas_disparados} alerta(s) enviado(s).")


def main():
    logger.info("=" * 55)
    logger.info("  🤖 MARKET MONITOR INICIADO")
    logger.info(f"  📊 Ativos: {len(ASSETS)}")
    logger.info(f"  ⏱️  Intervalo: {CHECK_INTERVAL_MINUTES} minutos")
    logger.info(f"  🕐 Horário: {HORARIO_INICIO} – {HORARIO_FIM}")
    logger.info("=" * 55)

    # Heartbeat diário às 08:00
    schedule.every().day.at("08:00").do(enviar_heartbeat)

    # Verificação periódica
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(verificar_ativos)

    # Roda uma vez imediatamente ao iniciar
    verificar_ativos()

    # Loop principal
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
