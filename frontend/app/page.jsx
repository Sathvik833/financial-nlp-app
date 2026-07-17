"use client";

import { useMemo, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/parseText";

export default function Home() {
  const [financialText, setFinancialText] = useState("");
  const [prediction, setPrediction] = useState("");
  const [details, setDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const predictionClassName = useMemo(() => {
    if (prediction === "positive") return "prediction positive";
    if (prediction === "negative") return "prediction negative";
    if (prediction === "neutral") return "prediction neutral";
    return "prediction";
  }, [prediction]);

  async function handleSubmit(event) {
    event.preventDefault();
    setIsLoading(true);
    setPrediction("");
    setDetails(null);
    setErrorMessage("");

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ financialText }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to parse this financial text.");
      }

      setPrediction(data.prediction);
      setDetails(data);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="dashboard">
        <div className="hero">
          <div>
            <p className="eyebrow">FinBERT Market Intelligence</p>
            <h1>Financial Sentiment Analyzer</h1>
            <p className="description">
              Evaluate earnings commentary, market updates, and financial news using
              sentence-level sentiment classification.
            </p>
          </div>

          <aside className="market-card" aria-label="Model summary">
            <span className="market-label">Model</span>
            <strong>ProsusAI / FinBERT</strong>
            <span className="market-status">● Online</span>
          </aside>
        </div>

        <form onSubmit={handleSubmit} className="form">
          <div className="form-header">
            <label htmlFor="financialText">Financial text</label>
            <span>{financialText.length} characters</span>
          </div>

          <textarea
            id="financialText"
            value={financialText}
            onChange={(event) => setFinancialText(event.target.value)}
            placeholder="Example: Revenue declined 6% year-over-year, but cloud services posted record growth and management raised full-year guidance."
            rows={9}
          />

          <button type="submit" disabled={isLoading || !financialText.trim()}>
            {isLoading ? (
              <>
                <span className="spinner" aria-hidden="true" />
                Analyzing market sentiment...
              </>
            ) : (
              "Run sentiment analysis"
            )}
          </button>
        </form>

        {errorMessage && <p className="error">{errorMessage}</p>}

        {prediction && (
          <section className="results" aria-live="polite">
            <div className="result-header">
              <div>
                <span className="section-label">Overall signal</span>
                <p className={predictionClassName}>{prediction}</p>
              </div>
              <span className="database-status">
                Airtable saved: {details?.databaseSaved ? "Yes" : "No"}
              </span>
            </div>

            {details && (
              <div className="details">
                <article>
                  <span>Positive</span>
                  <strong>{details.counts.positive}</strong>
                </article>
                <article>
                  <span>Neutral</span>
                  <strong>{details.counts.neutral}</strong>
                </article>
                <article>
                  <span>Negative</span>
                  <strong>{details.counts.negative}</strong>
                </article>
              </div>
            )}
          </section>
        )}
      </section>
    </main>
  );
}
