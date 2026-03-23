"""
ai_analyst.py
Chama a API do Perplexity (modelo sonar-pro) para gerar análise fundamentalista
com busca em tempo real sobre o movimento do ativo.
"""

import requests
import logging
from config import PERPLEXITY_API_KEY

logger = logging.getLogger(__name__)

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"


def gerar_analise(nome: str, ticker: str, tipo: str, variacao: float, preco: float) -> str:
    """
    Chama o Perplexity sonar-pro para buscar notícias reais e explicar
    o movimento do ativo com fundamentos.

    Args:
        nome:     Nome amigável do ativo (ex: "Ouro (Gold Futures)")
        ticker:   Código Yahoo Finance (ex: "GC=F")
        tipo:     Contexto do ativo para a IA
        variacao: Variação percentual intraday
        preco:    Preço atual

    Returns:
        String com a análise formatada
    """

    direcao = "alta" if variacao > 0 else "baixa"
    intensidade = _classificar_intensidade(abs(variacao))

    prompt = f"""Hoje, {nome} está em {direcao} de {abs(variacao):.2f}% no intraday ({intensidade}).
Preço atual: {preco:.4f} | Contexto do ativo: {tipo}.

Pesquise agora mesmo as principais notícias e dados de hoje que explicam esse movimento.

Responda EXATAMENTE neste formato (use os emojis e marcadores como estão):

📌 *CAUSA PRINCIPAL*
[1 frase direta com o principal driver do movimento hoje, cite fonte se souber]

📰 *CONTEXTO DO MOMENTO*
• [Fator 1 — dado ou notícia concreta de hoje]
• [Fator 2 — contexto macro ou setorial relevante]
• [Fator 3 — se houver, dado técnico ou de fluxo]

🎯 *O QUE MONITORAR AGORA*
[1-2 eventos ou dados que podem ampliar ou reverter o movimento nas próximas horas]

⚠️ *NÍVEL DE CONVICÇÃO DA ANÁLISE*
[Alta / Média / Baixa] — [motivo em 1 linha]

Seja direto, use dados reais, cite datas/valores quando souber. Máximo 180 palavras no total."""

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type":  "application/json",
    }

    payload = {
        "model":    "sonar-pro",          # Modelo com busca web em tempo real
        "messages": [
            {
                "role":    "system",
                "content": (
                    "Você é um analista de mercado sênior especializado em câmbio e commodities. "
                    "Sempre busque dados e notícias reais e atuais antes de responder. "
                    "Seja conciso, técnico e objetivo. Nunca invente dados — se não encontrar, diga."
                ),
            },
            {
                "role":    "user",
                "content": prompt,
            },
        ],
        "max_tokens":   500,
        "temperature":  0.2,              # Baixa temperatura = mais factual
        "return_citations": True,         # Perplexity retorna fontes
    }

    try:
        response = requests.post(
            PERPLEXITY_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        analise = data["choices"][0]["message"]["content"].strip()

        # Adiciona fontes se disponíveis
        citations = data.get("citations", [])
        if citations:
            fontes = "\n".join([f"  • {url}" for url in citations[:3]])
            analise += f"\n\n🔗 *Fontes consultadas agora:*\n{fontes}"

        return analise

    except requests.exceptions.Timeout:
        logger.error("Timeout na API do Perplexity")
        return "⚠️ Análise indisponível (timeout). Consulte Reuters, Bloomberg ou Investing.com."

    except requests.exceptions.HTTPError as e:
        logger.error(f"Erro HTTP Perplexity: {e} | Response: {response.text}")
        return f"⚠️ Erro na análise (HTTP {response.status_code}). Verifique sua chave API."

    except Exception as e:
        logger.error(f"Erro inesperado no Perplexity: {e}")
        return "⚠️ Análise temporariamente indisponível."


def _classificar_intensidade(variacao_abs: float) -> str:
    """Classifica a intensidade do movimento para enriquecer o contexto."""
    if variacao_abs >= 5:
        return "movimento EXTREMO"
    elif variacao_abs >= 3:
        return "movimento FORTE"
    elif variacao_abs >= 1.5:
        return "movimento RELEVANTE"
    else:
        return "movimento moderado"
