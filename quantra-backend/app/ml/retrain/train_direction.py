"""Quantra — Direction classifier training script."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def train_direction_classifier(
    features_df: pd.DataFrame,
    target_col: str = "future_direction",
    output_path: str | None = None,
):
    """Train the XGBoost direction classifier (UP/DOWN/SIDEWAYS)."""
    import xgboost as xgb
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import TimeSeriesSplit

    label_map = {"DOWN": 0, "SIDEWAYS": 1, "UP": 2}

    if target_col not in features_df.columns:
        # Create target from future returns
        if "future_return_5d" in features_df.columns:
            features_df[target_col] = features_df["future_return_5d"].apply(
                lambda r: "UP" if r > 0.02 else ("DOWN" if r < -0.02 else "SIDEWAYS")
            )
        else:
            logger.error("Cannot create direction target")
            return None

    features_df["target_encoded"] = features_df[target_col].map(label_map)
    feature_cols = [c for c in features_df.columns if c not in [target_col, "target_encoded", "ticker", "date", "future_return_5d", "target_score"]]

    X = features_df[feature_cols].fillna(0)
    y = features_df["target_encoded"]

    tscv = TimeSeriesSplit(n_splits=5)
    accuracies = []

    for train_idx, val_idx in tscv.split(X):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = xgb.XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
            num_class=3, objective="multi:softprob",
            random_state=42, use_label_encoder=False, eval_metric="mlogloss",
        )
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        preds = model.predict(X_val)
        acc = accuracy_score(y_val, preds)
        accuracies.append(acc)
        logger.info("Fold accuracy: %.4f", acc)

    logger.info("Mean accuracy: %.4f", np.mean(accuracies))

    final_model = xgb.XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
        num_class=3, objective="multi:softprob",
        random_state=42, use_label_encoder=False, eval_metric="mlogloss",
    )
    final_model.fit(X, y, verbose=False)

    if output_path:
        final_model.save_model(output_path)
        logger.info("Direction model saved to %s", output_path)

    return final_model
