"""
Quantra — FinBERT sentiment analysis model wrapper.

Singleton pattern — loads model once at worker startup.
Supports both ProsusAI/finbert and lighter distilroberta alternative.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None
_model_loaded = False

# Use lighter model by default for faster startup
DEFAULT_MODEL = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
FINBERT_MODEL = "ProsusAI/finbert"

LABEL_MAP = {
    "positive": "POSITIVE",
    "negative": "NEGATIVE",
    "neutral": "NEUTRAL",
    "LABEL_0": "POSITIVE",
    "LABEL_1": "NEGATIVE",
    "LABEL_2": "NEUTRAL",
}


def _load_model(model_name: str | None = None):
    """Load the sentiment model (singleton — called once)."""
    global _model, _tokenizer, _model_loaded

    if _model_loaded:
        return

    model_name = model_name or DEFAULT_MODEL
    logger.info("Loading sentiment model: %s", model_name)

    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForSequenceClassification.from_pretrained(model_name)
        _model.eval()

        _model_loaded = True
        logger.info("✅ Sentiment model loaded: %s", model_name)

    except Exception as e:
        logger.warning("⚠️  Failed to load sentiment model: %s", e)
        _model_loaded = False


class SentimentModel:
    """Wrapper for the sentiment analysis model."""

    def __init__(self, model_name: str | None = None):
        _load_model(model_name)

    def predict(self, text: str) -> dict[str, float]:
        """
        Run sentiment prediction on text.

        Returns:
            {"label": "POSITIVE/NEGATIVE/NEUTRAL", "score": -1.0 to 1.0, "confidence": 0-1}
        """
        if not _model_loaded or _model is None or _tokenizer is None:
            return {"label": "NEUTRAL", "score": 0.0, "confidence": 0.0}

        try:
            import torch

            inputs = _tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )

            with torch.no_grad():
                outputs = _model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=1)[0]

            # Get predicted class
            pred_idx = probs.argmax().item()
            confidence = probs[pred_idx].item()

            # Map to label
            id2label = getattr(_model.config, "id2label", {})
            raw_label = id2label.get(pred_idx, f"LABEL_{pred_idx}")
            label = LABEL_MAP.get(raw_label.lower(), "NEUTRAL")

            # Convert to score (-1 to +1)
            # For 3-class: positive=+1, neutral=0, negative=-1
            if label == "POSITIVE":
                score = confidence
            elif label == "NEGATIVE":
                score = -confidence
            else:
                score = 0.0

            return {"label": label, "score": round(score, 4), "confidence": round(confidence, 4)}

        except Exception as e:
            logger.error("Sentiment prediction error: %s", e)
            return {"label": "NEUTRAL", "score": 0.0, "confidence": 0.0}

    def predict_batch(self, texts: list[str]) -> list[dict[str, float]]:
        """Run sentiment prediction on a batch of texts."""
        return [self.predict(text) for text in texts]


# Singleton accessor
_singleton: SentimentModel | None = None


def get_sentiment_model(model_name: str | None = None) -> SentimentModel | None:
    """Get or create the singleton sentiment model."""
    global _singleton
    if _singleton is None:
        _singleton = SentimentModel(model_name)
    return _singleton if _model_loaded else None
