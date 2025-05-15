import os
import json
import asyncio
import sqlite3
from morphology_core import analyze_words

# Configuration

# Configuration
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 10))
INPUT_FILE = os.getenv("INPUT_FILE", "words.txt")
DB_FILE = os.getenv("DB_FILE", "morphology_detailed.db")
ERROR_LOG = os.getenv("ERROR_LOG", "morphology_errors.jsonl")


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
        results = await analyze_words(batch)
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
