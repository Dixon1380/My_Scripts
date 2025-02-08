import pandas as pd
import joblib
import os
from ai_logger import logger
from sklearn.ensemble import RandomForestRegressor
import ai_utils

INPUT_CSV = "ab_results.csv"
MODEL_FILE = "ab_predictor.pkl"

def train_ai_model():
    """
    Trains AI model to predict engagement (clicks, shares, views) from blog titles.
    """
    try:
        if not os.path.exists(INPUT_CSV):
            raise FileNotFoundError(f"❌ Training failed: {INPUT_CSV} not found.")

        df = pd.read_csv(INPUT_CSV)
        
        # Ensure dataset has necessary columns
        if not {"title", "clicks", "shares", "views"}.issubset(df.columns):
            raise ValueError("❌ CSV missing required columns!")

        # Convert titles into numerical representations using simple text length (improve later)
        df["title_length"] = df["title"].apply(len)

        # **New:** Predict engagement (clicks, shares, views) instead of predicting titles
        X = df[["title_length"]]
        y = df[["clicks", "shares", "views"]]

        model = RandomForestRegressor(n_estimators=100)
        model.fit(X, y)

        joblib.dump(model, MODEL_FILE)
        logger.info("✅ AI Model trained and saved.")

    except Exception as e:
        logger.error(f"❌ Training failed: {e}")

def predict_best_title():
    """
    Predicts the blog title most likely to get high engagement.
    """
    try:
        if not os.path.exists(MODEL_FILE):
            logger.error("❌ No trained model found! Run `train_ai_model()` first.")
            return None

        model = joblib.load(MODEL_FILE)

        if not os.path.exists(INPUT_CSV):
            logger.error("❌ No engagement data available for prediction.")
            return None

        df = pd.read_csv(INPUT_CSV)

        if df.empty or not {"title", "clicks", "shares", "views"}.issubset(df.columns):
            logger.error("❌ CSV missing required columns or is empty!")
            return None

        # Use text length as a feature to predict engagement
        df["title_length"] = df["title"].apply(len)
        X = df[["title_length"]]

        predicted_scores = model.predict(X)

        # Get the best title based on the **highest predicted engagement**
        best_index = predicted_scores[:, 0].argmax()  # Use `clicks` as primary ranking metric
        best_title = df.iloc[best_index]["title"]

        logger.info(f"🔮 Predicted best blog title: {best_title}")
        return best_title

    except Exception as e:
        logger.error(f"❌ Prediction failed: {e}")
        return None

if __name__ == "__main__":
    ai_utils.create_file(MODEL_FILE)
    train_ai_model()
    predict_best_title()
