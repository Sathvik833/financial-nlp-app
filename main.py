from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from nlp_engine import finalPrediction, insertDB, nlp_engine, split_sentences


app = FastAPI(title="Financial NLP Sentiment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReceiveText(BaseModel):
    financialText: str = Field(..., min_length=1)


class ParseTextResponse(BaseModel):
    prediction: str
    counts: dict[str, int]
    sentences: list[str]
    labels: list[str]
    databaseSaved: bool


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parseText", response_model=ParseTextResponse)
def parse_text(payload: ReceiveText) -> ParseTextResponse:
    try:
        get_sentences = split_sentences(payload.financialText)
        count_predictions = nlp_engine(get_sentences)
        final_label_count = finalPrediction(count_predictions)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    label = get_final_label(final_label_count)
    database_saved = insertDB(get_sentences, count_predictions)

    return ParseTextResponse(
        prediction=label,
        counts=final_label_count,
        sentences=get_sentences,
        labels=count_predictions,
        databaseSaved=database_saved,
    )


def get_final_label(final_label_count: dict[str, int]) -> str:
    max_count = max(final_label_count.values())

    if final_label_count["negative"] == max_count:
        return "negative"
    if final_label_count["positive"] == max_count:
        return "positive"
    return "neutral"
