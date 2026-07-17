# Financial NLP Sentiment Project

This project implements the PDF requirements as a working FastAPI backend and Next.js frontend.

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

## Deployment

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
