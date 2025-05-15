import asyncio
from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from morphology_core import analyze_word, analyze_words

app = FastAPI(title="Azerbaijani Morphology API", description="LLM-powered morphological analysis for Azerbaijani words. All endpoints require an api_key header with your Gemini API key.")
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

class SingleWordRequest(BaseModel):
    word: str

class BatchWordsRequest(BaseModel):
    words: List[str]

@app.post("/analyze", summary="Analyze a single word or a list of words", response_description="Morphological analysis results")
async def analyze(
    word: Optional[str] = None,
    words: Optional[List[str]] = None,
    body: Optional[Union[SingleWordRequest, BatchWordsRequest]] = None,
    api_key: str = Header(..., description="Your Gemini API key")
):
    # Accept input via query or JSON body
    if word:
        return await analyze_word(word, api_key)
    elif words:
        return await analyze_words(words, api_key)
    elif body:
        if hasattr(body, 'word'):
            return await analyze_word(body.word, api_key)
        elif hasattr(body, 'words'):
            return await analyze_words(body.words, api_key)
        else:
            raise HTTPException(status_code=400, detail="Invalid request body.")
    else:
        raise HTTPException(status_code=400, detail="Provide either 'word' or 'words' as query or in JSON body.")

@app.post("/analyze/single", summary="Analyze a single word", response_description="Morphological analysis result for a word")
async def analyze_single(request: SingleWordRequest, api_key: str = Header(..., description="Your Gemini API key")):
    return await analyze_word(request.word, api_key)

@app.post("/analyze/batch", summary="Analyze a batch of words", response_description="Morphological analysis results for words")
async def analyze_batch(request: BatchWordsRequest, api_key: str = Header(..., description="Your Gemini API key")):
    return await analyze_words(request.words, api_key)

@app.post("/analyze/upload", summary="Analyze words from uploaded file", response_description="Morphological analysis results for words in file")
async def analyze_upload(
    file: UploadFile = File(..., description="Text file with one Azerbaijani word per line"),
    api_key: str = Header(..., description="Your Gemini API key")
):
    content = await file.read()
    text = content.decode("utf-8")
    words = [line.strip() for line in text.splitlines() if line.strip()]
    if not words:
        raise HTTPException(status_code=400, detail="No words found in file.")
    return await analyze_words(words, api_key)

@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}
