# Azerbaijani Morphology Automation Project

## Overview

This repository contains tools to automate morphological segmentation and detailed analysis of Azerbaijani words using Google Gemini LLM and Python.

### Main Scripts

- **morphology_detailed.py**: Rich morphological analysis producing part-of-speech, word-formation type, segments, usage, etymology, English gloss, UD features, and Azerbaijani definition. Stores results in SQLite.

## Dependencies

- Python 3.8+
- google-generativeai
- pydantic

Standard library: `json`, `re`, `asyncio`, `sqlite3`.

## Setup

1. **Clone repository**
   ```powershell
   git clone <repo_url>
   cd <repo_dir>
   ```
2. **Create virtual environment**
   ```powershell
   uv sync
   ```
3. **Install packages**
   ```powershell
   uv add google-generativeai pydantic fastapi
   ```
4. **Set API key**
   ```powershell
   set GEMINI_API_KEY=YOUR_GEMINI_API_KEY
   ```
5. **Prepare input**
   - Place each Azerbaijani word on its own line in `words.txt`.


## morphology_detailed.py

### Purpose

- Detailed morphological analysis for lexicographic and NLP use:
  - **word**: original string
  - **pos**: part-of-speech (Azerbaijani terms)
  - **type**: word-formation type (`Sadə`,`Düzəltmə`,`Mürəkkəb`)
  - **segments**: ordered list of `{element,type}` morphemes
  - **usage**: `Ümumi` or `Terminologiya` (with `field`)
  - **etymology**: origin note
  - **gloss**: English translation
  - **features**: UD-style inflectional features
  - **definition**: short Azerbaijani gloss
- Saves to `morphology_detailed.db`, tables `morphology` and `progress`.

### Prompt Template

```text
You are an expert Azerbaijani linguist and lexicographer.
You MUST return ONLY a JSON array matching the schema below—no extra text.

Schema:
[
  {
    "word": "<string>",
    "pos": "<İsim,Sifət,Say,Əvəzlik,Feil,Zərf,Qoşma,Bağlayıcı,Ədat,Nida,Modal söz,Feil (Məsdər),İsim (Məsdər)>",
    "type": "<Sadə,Düzəltmə,Mürəkkəb>",
    "segments": [
      {"element":"<string>","type":"<Kök|Leksik Şəkilçi|Qrammatik Şəkilçi|Birləşdirici tire>"},
      …
    ],
    "usage":"<Ümumi|Terminologiya>",
    "field":"<string> (if Terminologiya)",
    "etymology":"<string> (optional)",
    "gloss":"<string> (English)",
    "features":{
      "Number":"<Sing|Plur>",
      "Case":"<Nom|Gen|Dat|Acc|Loc|Abl|Ins|Voc>",
      "Person":"<1|2|3>",
      "Tense":"<Pres|Past|Fut>",
      "Mood":"<Ind|Imp|Subj>",
      "Aspect":"<Imp|Perf>",
      "Voice":"<Act|Pass>",
      "Degree":"<Pos|Comp|Sup>",
      "Polarity":"<Pos|Neg>"
    },
    "definition":"<string>"
  },
  …
]

Example:
[{
  "word":"abadlıq-quruculuq",
  "pos":"İsim",
  "type":"Mürəkkəb",
  "segments":[
    {"element":"abad","type":"Kök"},
    {"element":"-lıq","type":"Leksik Şəkilçi"},
    {"element":"-","type":"Birləşdirici tire"},
    {"element":"qur","type":"Kök"},
    {"element":"-ucu","type":"Leksik Şəkilçi"},
    {"element":"-luq","type":"Leksik Şəkilçi"}
  ],
  "usage":"Ümumi",
  "gloss":"development",
  "features":{"Number":"Sing"},
  "definition":"Şəhərin bərpası üçün edilən işlər"
}]
```

### Database Schema (`morphology_detailed.db`)

```sql
CREATE TABLE IF NOT EXISTS morphology(
  word TEXT PRIMARY KEY,
  pos TEXT,
  type TEXT,
  segments TEXT,   -- JSON array
  usage TEXT,
  field TEXT,
  etymology TEXT,
  gloss TEXT,
  features TEXT,   -- JSON object
  definition TEXT
);
CREATE TABLE IF NOT EXISTS progress(
  id INTEGER PRIMARY KEY,
  batch_index INTEGER
);
```

## Examples

### Sample JSON Output from `morphology_detailed.py`

```json
[
  {
    "word": "abajurlu",
    "pos": "Sifət",
    "type": "Düzəltmə",
    "segments":[
      {"element":"abajur","type":"Kök"},
      {"element":"-lu","type":"Leksik Şəkilçi"}
    ],
    "usage":"Ümumi",
    "gloss":"lampshaded",
    "features": {"Number":"Sing"},
    "definition":"Abajurun olduğu vəziyyət"
  }
]
```

## Morphological Features Explained

- **Number**: Sing (tək) / Plur (çox)
- **Case**: Nom, Gen, Dat, Acc, Loc, Abl, Ins, Voc
- **Person**: 1, 2, 3
- **Tense**: Pres, Past, Fut
- **Mood**: Ind, Imp, Subj
- **Aspect**: Imp, Perf
- **Voice**: Act, Pass
- **Degree**: Pos, Comp, Sup
- **Polarity**: Pos, Neg

These align with Universal Dependencies conventions, providing a solid foundation for future morpho-tagging or parsing.

## Next Steps

- Use the detailed annotations to train a morphological tagger or dependency parser.
- Extend support for example sentences and context-aware analysis.
- Build a web UI or CLI for interactive lookups.
- Export data to CoNLL-U format for UD treebank development.
