import os
import json
import re
from typing import List, Dict, Optional, Literal
import google.generativeai as genai
from pydantic import BaseModel, ValidationError


class Segment(BaseModel):
    element: str
    type: Literal["Kök", "Leksik Şəkilçi", "Qrammatik Şəkilçi", "Birləşdirici tire"]

class DetailedAnalysis(BaseModel):
    word: str
    pos: str
    type: Literal["Sadə", "Düzəltmə", "Mürəkkəb"]
    segments: List[Segment]
    usage: Literal["Ümumi", "Terminologiya"]
    field: Optional[str] = None
    etymology: Optional[str] = None
    gloss: Optional[str] = None
    features: Optional[Dict[str, str|None]] = None
    definition: Optional[str] = None

SCHEMA = '''
[
  {
    "word": "<string>",
    "pos": "<one of: İsim,Sifət,Say,Əvəzlik,Feil,Zərf,Qoşma,Bağlayıcı,Ədat,Nida,Modal söz,Feil (Məsdər),İsim (Məsdər)>",
    "type": "<one of: Sadə,Düzəltmə,Mürəkkəb>",
    "segments": [
      { "element": "<string>", "type": "<Kök|Leksik Şəkilçi|Qrammatik Şəkilçi|Birləşdirici tire>" },
      ...
    ],
    "usage": "<Ümumi|Terminologiya>",
    "field": "<string> (only if usage is Terminologiya)",
    "etymology": "<string> (etymology note)",
    "gloss": "<string> (English gloss)",
    "features": {
      "Number": "<Sing|Plur>",
      "Case": "<Nom|Gen|Dat|Abl|Loc>",
      "Person": "<1|2|3>",
      "Tense": "<Past|Pres|Fut>",
      "Mood": "<Ind|Imp|Cnd>",
      "Aspect": "<Prog|Imp|Perf>",
      "Voice": "<Act|Pass>",
      "Degree": "<Pos|Cmp|Sup>",
      "Polarity": "<Pos|Neg>"
    },
    "definition": "<string> (short Azerbaijani definition)"
  },
  ...
]
'''

EXAMPLE = [
    {
        "word": "abadlıq-quruculuq",
        "pos": "İsim",
        "type": "Mürəkkəb",
        "segments": [
            {"element": "abad", "type": "Kök"},
            {"element": "-lıq", "type": "Leksik Şəkilçi"},
            {"element": "-", "type": "Birləşdirici tire"},
            {"element": "qur", "type": "Kök"},
            {"element": "-ucu", "type": "Leksik Şəkilçi"},
            {"element": "-luq", "type": "Leksik Şəkilçi"}
        ],
        "usage": "Ümumi",
        "gloss": "development",
        "features": {"Number": "Sing"},
        "definition": "Şəhərin bərpası üçün edilən işlər"
    }
]
EXAMPLE_JSON = json.dumps(EXAMPLE, ensure_ascii=False)

MODEL_NAME = "gemini-2.5-flash-preview-04-17"

async def analyze_words(words: List[str], api_key: str) -> List[dict]:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = (
        "You are an expert Azerbaijani linguist and lexicographer.\n"
        "You MUST return ONLY a JSON array matching the schema below. NO extra text.\n"
        f"Schema:{SCHEMA}\n"
        f"Example:{EXAMPLE_JSON}\n"
        f"Analyze the following words and return your JSON array:\n{json.dumps(words, ensure_ascii=False)}"
    )
    response = model.generate_content(prompt)
    text = response.text
    match = re.search(r'(\[.*\])', text, re.S)
    if not match:
        # If no JSON array, return error for all words
        return [{"error": "No JSON array in LLM response", "llm_output": text, "input_words": words}]
    payload = match.group(1)
    cleaned = re.sub(r',\s*([}\]])', r'\1', payload)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return [{"error": f"JSON parsing failed: {e}", "llm_output": cleaned, "input_words": words}]
    validated = []
    for item in data:
        try:
            obj = DetailedAnalysis.model_validate(item)
            validated.append(obj.model_dump())
        except ValidationError as e:
            validated.append({
                "error": f"Validation error: {str(e)}",
                "item": item
            })
    return validated

async def analyze_word(word: str, api_key: str) -> dict:
    results = await analyze_words([word], api_key)
    return results[0] if results else {"error": "No result returned"}
