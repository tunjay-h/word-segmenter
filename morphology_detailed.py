import os
import json
import re
import asyncio
import sqlite3
from typing import List, Dict, Optional, Literal
import google.generativeai as genai
from pydantic import BaseModel, ValidationError

# Configuration
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))
INPUT_FILE = os.getenv("INPUT_FILE", "words.txt")
DB_FILE = os.getenv("DB_FILE", "morphology_detailed.db")
ERROR_LOG = os.getenv("ERROR_LOG", "morphology_errors.jsonl")
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyChHQCcMkc1KBuEoPIH3YHGz6_wXddk2wI")

if not API_KEY:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")

genai.configure(api_key=API_KEY)

# Pydantic models
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
    features: Optional[Dict[str, str]] = None
    definition: Optional[str] = None

async def segment_batch(words, model):
    # Example to guide the model
    example = [{
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
    }]
    example_json = json.dumps(example, ensure_ascii=False)

    # Schema description
    schema = """
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
    """

    prompt = (
        "You are an expert Azerbaijani linguist and lexicographer.\n"
        "You MUST return ONLY a JSON array matching the schema below. NO extra text.\n"
        f"Schema:{schema}\n"
        f"Example:{example_json}\n"
        f"Analyze the following words and return your JSON array:\n{json.dumps(words, ensure_ascii=False)}"
    )

    response = model.generate_content(prompt)
    text = response.text
    # Extract JSON array
    match = re.search(r'(\[.*\])', text, re.S)
    if not match:
        with open(ERROR_LOG, "a", encoding="utf-8") as ef:
            ef.write(text + "\n")
        print("No JSON array in response:", text)
        return []
    payload = match.group(1)

    # Clean trailing commas
    cleaned = re.sub(r',\s*([}\]])', r'\1', payload)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        with open(ERROR_LOG, "a", encoding="utf-8") as ef:
            ef.write(cleaned + "\n")
        print("JSON parsing failed:", e)
        return []

    # Validate with Pydantic
    validated = []
    for item in data:
        try:
            obj = DetailedAnalysis.model_validate(item)
            validated.append(obj.model_dump())
        except ValidationError as e:
            with open(ERROR_LOG, "a", encoding="utf-8") as ef:
                ef.write(json.dumps(item, ensure_ascii=False) + "\n")
            print("Validation error for item:", item, e)
    return validated

async def main():
    # Setup SQLite DB
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS morphology(
            word TEXT PRIMARY KEY,
            pos TEXT,
            type TEXT,
            segments TEXT,
            usage TEXT,
            field TEXT,
            etymology TEXT,
            gloss TEXT,
            features TEXT,
            definition TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS progress(
            id INTEGER PRIMARY KEY,
            batch_index INTEGER
        )
        """
    )
    conn.commit()

    # Get last processed batch
    cursor.execute("SELECT batch_index FROM progress WHERE id=1")
    row = cursor.fetchone()
    start = row[0] if row else 0
    if not row:
        cursor.execute("INSERT INTO progress(id,batch_index) VALUES(1,0)")
        conn.commit()

    # Read input words
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        words = [w.strip() for w in f if w.strip()]
    total = len(words)

    # Initialize model
    model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")

    # Process in batches
    for i in range(start, total, BATCH_SIZE):
        if i >= 20:
            break
        batch = words[i : i + BATCH_SIZE]
        print(f"Processing words {i+1} to {min(i+BATCH_SIZE, total)} of {total}")
        results = await segment_batch(batch, model)
        with open("result.jsonl", "a", encoding="utf-8") as result_file:
            for obj in results:
                # Write to JSONL
                result_file.write(json.dumps(obj, ensure_ascii=False) + "\n")
                segments_json = json.dumps(obj["segments"], ensure_ascii=False)
                features_json = (
                    json.dumps(obj.get("features", {}), ensure_ascii=False)
                    if obj.get("features")
                    else None
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO morphology(word,pos,type,segments,usage,field,etymology,gloss,features,definition) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (
                        obj["word"], obj["pos"], obj["type"], segments_json,
                        obj["usage"], obj.get("field"), obj.get("etymology"),
                        obj.get("gloss"), features_json, obj.get("definition")
                    ),
                )
        # Update progress
        cursor.execute("UPDATE progress SET batch_index = ? WHERE id=1", (i + BATCH_SIZE,))
        conn.commit()

    conn.close()

if __name__ == "__main__":
    print("Starting detailed morphology analysis...")
    asyncio.run(main())
