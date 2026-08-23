# Financial NLP Sentiment Project

A web app that classifies financial text as positive, neutral, or negative. Paste in a paragraph, and the app splits it into sentences, classifies each one, and returns both the per-sentence labels and an overall verdict for the paragraph.

Team 5 — ISBA 2411: Sathvik Datla, Jiaru Li, Yujia Weng

Live Url: https://financial-nlp-frontend.vercel.app/

---

## Business, Problem, Stake Holder

We are targeting everyday people who need help analyzing financial texts. Most people who don't have ties to the industry have to read financial articles all by themselves and make a judgement on whether the paragraph is reading positively or not. With this tool though, they can just plug in the paragraph and double check their assumption to see whether what they were thinking was right or wrong.

## Problem Statement

Our original scope was to read whole corporate filings, news feeds, and exchange data in order to pull out which entity the sentiment is about. We also wanted to extract specific risks and not just sentiment. Another thing we wanted to do was verify claims against source text via RAG and weight sources by trustworthiness. After looking at our training data we realized that all the things listed above were not necessary, since our training data was largely sentiment based.

We ended up reducing the scope of the project to where the user pastes the text into an input box. That paragraph is then split up into smaller sentences using the NLTK Python library, and each sentence gets its own neutral, positive, or negative rating. At the end there is a voting system that checks which sentiment was the majority in that paragraph, and the entire paragraph ends up getting one result: positive, neutral, or negative.

## Project Architecture
<img width="901" height="576" alt="architecture" src="https://github.com/user-attachments/assets/f27b756e-4d80-4991-90ab-6b2af6bea07c" />


Tech Stack: FastAPI, Vercel, Render, next.js, and Airtable

## Findings

For our findings we use the MiniLM embeddings + logistic regression model from milestone 2 as our baseline, where the F1 scores for each class were positive = .677, negative = .366, and neutral = .839. Comparing that to the distilbert-base-uncased model using the LoRA method in milestone 5, the F1 scores for each category were positive = .82, neutral = .80, and negative = .47. Overall the macro F1 improved from 0.634 to 0.70, with 0.76 accuracy on a held-out test set of 2,920 sentences.

| Class | M2 baseline | M5 LoRA |
|---|---|---|
| negative | 0.366 | 0.47 |
| neutral | 0.839 | 0.80 |
| positive | 0.677 | 0.82 |
| **macro-F1** | **0.634** | **0.70** |

## Governance/Risk Appendix

The problem we were facing was bias. We realized that we did not actually have enough training data to have an equal balance of the three classes. This bias was detected when running the model in milestone 2, where the F1 score for the negative class was .366.

In order to fix this imbalance we first thought we could use Claude to generate extra data, but then we realized that generating data with Claude would not be authentic, since it is making up its own examples rather than using real world examples.

So we decided to use FinBERT to fix our class imbalance problem. The reason we decided to use FinBERT is that this model is trained on a huge financial phrase bank, which means it has a lot of examples of positive, neutral, and negative financial sentences. We ran this model and got .63 on the F1 score for our negative class, which was a significant improvement. But after further research we found out that our training data was already used in FinBERT's training data, which ends up leading to contamination.

We ended up scratching that out and decided to use the LoRA method from milestone 3, which uses the model distilbert-base-uncased, since this model has pretrained knowledge and can also train on the training data that you provide. We thought this might fix our class imbalance problem as well. After running the model and checking the F1 score for the negative class, it went up to 0.47, which is a slight improvement but not exactly what we were looking for.

### Other risks we looked at

**Privacy.** Text submitted by users gets stored in Airtable. We do not filter out personal information and we do not have a retention policy, so anyone deploying this for real use would need both.

**Out of domain input.** The model always returns one of the three labels even if the text is not financial at all. If you paste in a recipe you still get a confident sentiment score back. There is no "not applicable" output.

**Data quality.** Our dataset has 520 duplicated sentences and some of them are labeled inconsistently. 262 of our 2,920 test rows have a sentence that also shows up in the training half, and 261 of those have a conflicting label, meaning the same sentence is tagged one way in training and a different way in test. This puts a ceiling on any score we can get on this data.

**Feedback loop.** The predictions we save to Airtable are meant for human review and correction before we would ever use them as training data. Training straight on unreviewed model output would just teach the model to repeat its own mistakes.

## Deployment

We decided to use FinBERT because this model is trained on a huge financial phrase bank, which means it has a lot of examples of positive, neutral, and negative financial sentences. We also did a smoke test with random examples and did a side by side comparison of FinBERT and the distilbert model we trained, to see which one is better able to predict negative sentiment sentences. FinBERT was able to accurately predict sentences with negative sentiment a lot better.

---

## Backend

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn main:app --reload
```

Endpoint:

```http
POST http://127.0.0.1:8000/parseText
Content-Type: application/json

{
  "financialText": "Revenue growth beat expectations."
}
```

Response:

```json
{
  "prediction": "positive",
  "counts": {
    "positive": 1,
    "neutral": 0,
    "negative": 0
  },
  "sentences": ["Revenue growth beat expectations."],
  "labels": ["positive"],
  "databaseSaved": false
}
```

There is also a `GET /` health check that returns `{"status": "ok"}`. Render uses this to check whether the service is alive.

## Optional Airtable saving

Set `AIRTABLE_API_TOKEN` in your local `.env` file if you want sentence predictions saved to Airtable:

```env
AIRTABLE_API_TOKEN=your_airtable_personal_access_token
```

The `.env` file is ignored by git so your token stays local. If `AIRTABLE_API_TOKEN` is not set, the API still works and skips Airtable insertion.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

The UI includes:
- financial text input
- submit button
- loading spinner after submit
- prediction display
- finance-style positive, neutral, and negative result panels

## Deploying

### Render backend

Deploy the project root to Render as a Python web service.

Use this start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Use this build command:

```bash
pip install -r requirements.txt && python -m nltk.downloader punkt punkt_tab
```

Set this Render environment variable:

```env
AIRTABLE_API_TOKEN=your_airtable_personal_access_token
```

Do not include `Bearer`; the backend adds that automatically.

### Vercel frontend

Deploy the `frontend` folder to Vercel.

Set this Vercel environment variable:

```env
NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com/parseText
```

Replace the URL with your real Render backend URL. After setting it, redeploy the Vercel frontend.

Note: the Render free tier spins down when idle, so the first request after a period of inactivity can take 30 seconds or more while the container restarts and the model loads.
