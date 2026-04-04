"""
ai_analyst.py
Gemini 2.0 Flash como provider principal, Groq como fallback automático.
Inclui retry com backoff para lidar com rate limits (429).
"""

import requests
import logging
import time
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
    noticias       = buscar_noticias(ticker)
    bloco_noticias = f"\n\n{noticias}" if noticias else "\n\n(Nenhuma headline relevante encontrada agora.)"
    prompt         = _montar_prompt(nome, tipo, variacao, preco, bloco_noticias)

    # Tenta o provider configurado; se falhar por rate limit, cai no outro
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

    return resultado or "⚠️ Análise indisponível no momento. Ambos os providers falharam."


def _montar_prompt(nome, tipo, variacao, preco, bloco_noticias) -> str:
    direcao     = "alta" if variacao > 0 else "baixa"
    intensidade = _classificar_intensidade(abs(variacao))

    return f"""Hoje, {nome} está em {direcao} de {abs(variacao):.2f}% no intraday ({intensidade}).
Preço atual: {preco:.4f} | Contexto do ativo: {tipo}.
{bloco_noticias}

Com base nas headlines acima, responda EXATAMENTE neste formato:

📌 *CAUSA PRINCIPAL*
[principal driver do movimento, mencionando a fonte quando possível]

📰 *CONTEXTO DO MOMENTO*
- [Fator 1 — extraído das headlines ou contexto macro]
- [Fator 2 — contexto macro ou setorial]
- [Fator 3 — dado técnico ou de fluxo, se aplicável]

🎯 *O QUE MONITORAR AGORA*
[eventos que podem ampliar ou reverter nas próximas horas]

⚠️ *NÍVEL DE CONVICÇÃO*
[Alta / Média / Baixa] — [motivo em 1 linha]

Máximo 180 palavras. Seja técnico e direto."""


def _chamar_gemini(prompt: str, tentativas: int = 3) -> str | None:
    """Chama Gemini com retry automático em caso de 429."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 500},
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
    }

    for tentativa in range(1, tentativas + 1):
        try:
            response = requests.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                json=payload,
                timeout=30,
            )

            if response.status_code == 429:
                espera = 15 * tentativa  # 15s, 30s, 45s
                logger.warning(f"Gemini 429 — aguardando {espera}s (tentativa {tentativa}/{tentativas})")
                time.sleep(espera)
                continue

            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

        except requests.exceptions.HTTPError:
            logger.error(f"Gemini HTTP {response.status_code}: {response.text[:150]}")
            return None
        except Exception as e:
            logger.error(f"Gemini erro inesperado: {e}")
            return None

    logger.error("Gemini esgotou tentativas de retry")
    return None  # Sinaliza falha para acionar fallback


def _chamar_groq(prompt: str, tentativas: int = 3) -> str | None:
    """Chama Groq com retry automático em caso de 429."""
    payload = {
        "model":    "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens":  500,
    }

    for tentativa in range(1, tentativas + 1):
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

            if response.status_code == 429:
                espera = 10 * tentativa  # 10s, 20s, 30s
                logger.warning(f"Groq 429 — aguardando {espera}s (tentativa {tentativa}/{tentativas})")
                time.sleep(espera)
                continue

            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()

        except requests.exceptions.HTTPError:
            logger.error(f"Groq HTTP {response.status_code}: {response.text[:150]}")
            return None
        except Exception as e:
            logger.error(f"Groq erro inesperado: {e}")
            return None

    logger.error("Groq esgotou tentativas de retry")
    return None


def _classificar_intensidade(v: float) -> str:
    if v >= 5:   return "movimento EXTREMO"
    if v >= 3:   return "movimento FORTE"
    if v >= 1.5: return "movimento RELEVANTE"
    return "movimento moderado"
