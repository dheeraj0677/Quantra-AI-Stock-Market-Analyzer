"""Quantra — XGBoost scorer training script."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def train_scorer(
    features_df: pd.DataFrame,
    target_col: str = "future_return_5d",
    output_path: str | None = None,
):
    """
    Train the XGBoost stock scorer on historical features.

    Args:
        features_df: DataFrame with feature columns and target column
        target_col: Column with future returns (used to generate 0-100 score)
        output_path: Path to save trained model
    """
    import xgboost as xgb
    from sklearn.metrics import mean_squared_error
    from sklearn.model_selection import TimeSeriesSplit

    # Create score target (0-100) from future returns
    if target_col in features_df.columns:
        # Convert returns to 0-100 score using percentile rank
        features_df["target_score"] = features_df[target_col].rank(pct=True) * 100
    else:
        logger.error("Target column %s not found", target_col)
        return None

    feature_cols = [c for c in features_df.columns if c not in [target_col, "target_score", "ticker", "date"]]
    X = features_df[feature_cols].fillna(0)
    y = features_df["target_score"]

    # Walk-forward cross-validation
    tscv = TimeSeriesSplit(n_splits=5)
    scores = []

    for train_idx, val_idx in tscv.split(X):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=5,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
        )
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )
        preds = model.predict(X_val)
        rmse = np.sqrt(mean_squared_error(y_val, preds))
        scores.append(rmse)
        logger.info("Fold RMSE: %.4f", rmse)

    logger.info("Mean RMSE across folds: %.4f", np.mean(scores))

    # Final model on all data
    final_model = xgb.XGBRegressor(
        n_estimators=200, max_depth=6, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
        reg_alpha=0.1, reg_lambda=1.0, random_state=42,
    )
    final_model.fit(X, y, verbose=False)

    if output_path:
        final_model.save_model(output_path)
        logger.info("Scorer model saved to %s", output_path)

    return final_model
