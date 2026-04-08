"""
ai_analyst.py
Gera análise fundamentalista usando Gemini 2.0 Flash ou Groq (Llama 3.3),
enriquecida com headlines reais via RSS (news_fetcher).
Fallback automático: se o provider principal falhar, tenta o outro.
"""

import requests
import logging
import time
from typing import Optional
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
    noticias = buscar_noticias(ticker)
    bloco    = f"\n\n{noticias}" if noticias else "\n\n(Sem headlines relevantes no momento.)"
    prompt   = _montar_prompt(nome, tipo, variacao, preco, bloco)

    if AI_PROVIDER == "groq":
        resultado = _chamar_groq(prompt)
        if resultado is None:
            logger.warning("Groq falhou — tentando Gemini como fallback...")
            resultado = _chamar_gemini(prompt)
    else:
        resultado = _chamar_gemini(prompt)
        if resultado is None:
            logger.warning("Gemini falhou — tentando Groq como fallback...")
            resultado = _chamar_groq(prompt)

    return resultado or "⚠️ Análise indisponível no momento."


def _montar_prompt(nome: str, tipo: str, variacao: float, preco: float, bloco_noticias: str) -> str:
    direcao     = "alta" if variacao > 0 else "baixa"
    intensidade = _intensidade(abs(variacao))
    return (
        f"Hoje, {nome} está em {direcao} de {abs(variacao):.2f}% no intraday ({intensidade}).\n"
        f"Preço atual: {preco:.4f} | Contexto: {tipo}."
        f"{bloco_noticias}\n\n"
        f"Com base nas headlines acima, responda EXATAMENTE neste formato:\n\n"
        f"📌 *CAUSA PRINCIPAL*\n"
        f"[principal driver do movimento, cite a fonte quando possível]\n\n"
        f"📰 *CONTEXTO DO MOMENTO*\n"
        f"• [Fator 1]\n• [Fator 2]\n• [Fator 3]\n\n"
        f"🎯 *O QUE MONITORAR AGORA*\n"
        f"[eventos que podem ampliar ou reverter o movimento]\n\n"
        f"⚠️ *NÍVEL DE CONVICÇÃO*\n"
        f"[Alta / Média / Baixa] — [motivo em 1 linha]\n\n"
        f"Máximo 180 palavras. Seja técnico e direto."
    )


def _chamar_gemini(prompt: str, tentativas: int = 3) -> Optional[str]:
    payload = {
        "contents":          [{"parts": [{"text": prompt}]}],
        "generationConfig":  {"temperature": 0.2, "maxOutputTokens": 500},
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
    }
    for i in range(1, tentativas + 1):
        try:
            r = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", json=payload, timeout=30)
            if r.status_code == 429:
                espera = 15 * i
                logger.warning(f"Gemini 429 — aguardando {espera}s ({i}/{tentativas})")
                time.sleep(espera)
                continue
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except requests.exceptions.HTTPError:
            logger.error(f"Gemini HTTP {r.status_code}: {r.text[:150]}")
            return None
        except Exception as e:
            logger.error(f"Gemini erro: {e}")
            return None
    logger.error("Gemini esgotou tentativas")
    return None


def _chamar_groq(prompt: str, tentativas: int = 3) -> Optional[str]:
    payload = {
        "model":    "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens":  500,
    }
    for i in range(1, tentativas + 1):
        try:
            r = requests.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            if r.status_code == 429:
                espera = 10 * i
                logger.warning(f"Groq 429 — aguardando {espera}s ({i}/{tentativas})")
                time.sleep(espera)
                continue
            if r.status_code != 200:
                logger.error(f"Groq HTTP {r.status_code}: {r.text[:150]}")
                return None
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.HTTPError:
            logger.error(f"Groq HTTPError: {r.text[:150]}")
            return None
        except Exception as e:
            logger.error(f"Groq erro: {type(e).__name__}: {e}")
            return None
    logger.error("Groq esgotou tentativas")
    return None


def _intensidade(v: float) -> str:
    if v >= 5:   return "movimento EXTREMO"
    if v >= 3:   return "movimento FORTE"
    if v >= 1.5: return "movimento RELEVANTE"
    return "movimento moderado"
