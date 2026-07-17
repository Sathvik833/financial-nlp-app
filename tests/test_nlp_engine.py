import unittest
from unittest.mock import Mock, patch

from nlp_engine import finalPrediction, insertDB, nlp_engine, split_sentences


class TestNlpEngine(unittest.TestCase):
    def test_split_sentences_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            split_sentences("   ")

    def test_split_sentences_returns_sentence_list(self):
        self.assertEqual(
            split_sentences("Revenue increased. Profit rose."),
            ["Revenue increased.", "Profit rose."],
        )

    @patch("nlp_engine.pipeline")
    def test_nlp_engine_runs_finbert_predictions(self, mock_pipeline):
        mock_finbert = Mock()
        mock_finbert.side_effect = [
            [{"label": "positive"}],
            [{"label": "negative"}],
        ]
        mock_pipeline.return_value = mock_finbert

        predictions = nlp_engine(["Revenue increased.", "Debt risk fell."])

        self.assertEqual(predictions, ["positive", "negative"])
        mock_pipeline.assert_called_once_with(
            "sentiment-analysis",
            model="ProsusAI/finbert",
        )

    def test_final_prediction_counts_labels(self):
        counts = finalPrediction(["positive", "negative", "positive", "neutral"])

        self.assertEqual(
            counts,
            {
                "positive": 2,
                "neutral": 1,
                "negative": 1,
            },
        )

    def test_final_prediction_rejects_unknown_label(self):
        with self.assertRaises(ValueError):
            finalPrediction(["bullish"])

    @patch.dict("os.environ", {}, clear=True)
    def test_insert_db_returns_false_without_airtable_token(self):
        self.assertFalse(insertDB(["Sentence."], ["positive"]))

    @patch.dict("os.environ", {"AIRTABLE_API_TOKEN": "test-token"})
    @patch("nlp_engine.requests.post")
    def test_insert_db_posts_records_to_airtable(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        saved = insertDB(["Sentence one.", "Sentence two."], ["positive", "negative"])

        self.assertTrue(saved)
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(
            kwargs["json"],
            {
                "records": [
                    {
                        "fields": {
                            "sentence": "Sentence one.",
                            "model_prediction": "positive",
                        }
                    },
                    {
                        "fields": {
                            "sentence": "Sentence two.",
                            "model_prediction": "negative",
                        }
                    },
                ]
            },
        )
        self.assertEqual(
            kwargs["headers"]["Authorization"],
            "Bearer test-token",
        )

    @patch.dict("os.environ", {"AIRTABLE_API_TOKEN": "test-token"})
    @patch("nlp_engine.requests.post")
    def test_insert_db_batches_airtable_records_by_ten(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        sentences = [f"Sentence {number}." for number in range(12)]
        labels = ["positive"] * 12

        saved = insertDB(sentences, labels)

        self.assertTrue(saved)
        self.assertEqual(mock_post.call_count, 2)
        first_call = mock_post.call_args_list[0]
        second_call = mock_post.call_args_list[1]
        self.assertEqual(len(first_call.kwargs["json"]["records"]), 10)
        self.assertEqual(len(second_call.kwargs["json"]["records"]), 2)


if __name__ == "__main__":
    unittest.main()
