"""
ai_analyst.py
Gera análise fundamentalista usando Gemini (padrão) ou Groq (Llama),
enriquecida com headlines reais buscadas via RSS gratuito pelo news_fetcher.

Para trocar o provider, mude AI_PROVIDER em config.py:
  "gemini"  → Google Gemini 2.0 Flash (1.500 req/dia grátis)
  "groq"    → Groq Llama 3.3 70B     (14.400 req/dia grátis)
"""

import requests
import logging
from config import AI_PROVIDER, GEMINI_API_KEY, GROQ_API_KEY
from news_fetcher import buscar_noticias

logger = logging.getLogger(__name__)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = (
    "Você é um analista de mercado sênior especializado em câmbio e commodities. "
    "Quando receber headlines reais, use-as como base principal da análise. "
    "Seja conciso, técnico e objetivo. Sinalize incerteza quando necessário."
)


def gerar_analise(nome: str, ticker: str, tipo: str, variacao: float, preco: float) -> str:
    """
    Busca notícias reais via RSS e passa ao LLM configurado (Gemini ou Groq)
    para gerar análise fundamentalista do movimento intraday.
    """

    # 1. Busca headlines reais (gratuito, via RSS)
    noticias = buscar_noticias(ticker)
    bloco_noticias = f"\n\n{noticias}" if noticias else "\n\n(Nenhuma headline relevante encontrada agora.)"

    # 2. Monta o prompt com as notícias embutidas
    prompt = _montar_prompt(nome, tipo, variacao, preco, bloco_noticias)

    # 3. Chama o provider configurado
    if AI_PROVIDER == "groq":
        return _chamar_groq(prompt)
    else:
        return _chamar_gemini(prompt)


# ------------------------------------------------------------------ #
#  PROMPT                                                              #
# ------------------------------------------------------------------ #

def _montar_prompt(nome, tipo, variacao, preco, bloco_noticias) -> str:
    direcao     = "alta" if variacao > 0 else "baixa"
    intensidade = _classificar_intensidade(abs(variacao))

    return f"""Hoje, {nome} está em {direcao} de {abs(variacao):.2f}% no intraday ({intensidade}).
Preço atual: {preco:.4f} | Contexto do ativo: {tipo}.
{bloco_noticias}

Com base nas headlines acima (use-as como fonte principal), responda EXATAMENTE neste formato:

📌 *CAUSA PRINCIPAL*
[1 frase direta com o principal driver do movimento, mencionando a fonte quando possível]

📰 *CONTEXTO DO MOMENTO*
• [Fator 1 — extraído das headlines ou contexto macro conhecido]
• [Fator 2 — contexto macro ou setorial relevante]
• [Fator 3 — dado técnico, de fluxo ou sazonalidade, se aplicável]

🎯 *O QUE MONITORAR AGORA*
[1-2 eventos ou dados que podem ampliar ou reverter o movimento nas próximas horas]

⚠️ *NÍVEL DE CONVICÇÃO*
[Alta / Média / Baixa] — [motivo em 1 linha, cite se baseou em headlines reais ou só em contexto geral]

Máximo 180 palavras no total. Seja técnico e direto."""


# ------------------------------------------------------------------ #
#  PROVIDERS                                                           #
# ------------------------------------------------------------------ #

def _chamar_gemini(prompt: str) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature":    0.2,
            "maxOutputTokens": 500,
        },
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
    }
    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    except requests.exceptions.HTTPError:
        logger.error(f"Erro HTTP Gemini {response.status_code}: {response.text[:200]}")
        return f"⚠️ Erro na análise (HTTP {response.status_code}). Verifique sua chave Gemini."
    except Exception as e:
        logger.error(f"Erro Gemini: {e}")
        return "⚠️ Análise temporariamente indisponível (Gemini)."


def _chamar_groq(prompt: str) -> str:
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens":  500,
    }
    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type":  "application/json",
            },
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except requests.exceptions.HTTPError:
        logger.error(f"Erro HTTP Groq {response.status_code}: {response.text[:200]}")
        return f"⚠️ Erro na análise (HTTP {response.status_code}). Verifique sua chave Groq."
    except Exception as e:
        logger.error(f"Erro Groq: {e}")
        return "⚠️ Análise temporariamente indisponível (Groq)."


# ------------------------------------------------------------------ #
#  UTILITÁRIO                                                          #
# ------------------------------------------------------------------ #

def _classificar_intensidade(v: float) -> str:
    if v >= 5:   return "movimento EXTREMO"
    if v >= 3:   return "movimento FORTE"
    if v >= 1.5: return "movimento RELEVANTE"
    return "movimento moderado"
