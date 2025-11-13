from pathlib import Path
import re
import random
import pickle
import numpy as np
import pandas as pd
import nltk
nltk.download('stopwords')

from nltk.corpus import movie_reviews, stopwords
from nltk.stem import WordNetLemmatizer

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix

MODEL_PATH = Path("sentiment_model.pkl")


def ensure_nltk_data():
    for r in ["movie_reviews", "wordnet", "omw-1.4", "stopwords"]:
        try:
            nltk.data.find(f"corpora/{r}")
        except LookupError:
            print(f"Downloading NLTK resource: {r}")
            nltk.download(r)


lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    words = [lemmatizer.lemmatize(w) for w in text.split() if w not in stop_words]
    return " ".join(words)


def load_movie_reviews_df():
    documents = [(list(movie_reviews.words(fileid)), category)
                 for category in movie_reviews.categories()
                 for fileid in movie_reviews.fileids(category)]
    random.shuffle(documents)
    reviews = [" ".join(words) for words, _ in documents]
    sentiments = [sent for _, sent in documents]
    df = pd.DataFrame({"review": reviews, "sentiment": sentiments})
    df["review"] = df["review"].map(clean_text)
    return df


def build_and_train(df: pd.DataFrame):
    X_train, X_test, y_train, y_test = train_test_split(
        df["review"], df["sentiment"], test_size=0.2, random_state=42, stratify=df["sentiment"]
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english")),
        ("clf", LinearSVC(class_weight="balanced", max_iter=3000))
    ])

    # Grid search for optimal parameters
    params = {
        "tfidf__ngram_range": [(1, 1), (1, 2), (1, 3)],
        "tfidf__max_features": [5000, 10000, 15000],
        "clf__C": [0.5, 1.0, 2.0]
    }

    print("Training model with GridSearchCV...")
    grid = GridSearchCV(pipeline, param_grid=params, cv=3, n_jobs=-1, verbose=2)
    grid.fit(X_train, y_train)

    best_model = grid.best_estimator_
    print(f"Best parameters: {grid.best_params_}")

    train_acc = best_model.score(X_train, y_train)
    test_acc = best_model.score(X_test, y_test)
    print(f"\nTrain accuracy: {train_acc:.3f}")
    print(f"Test  accuracy: {test_acc:.3f}")

    y_pred = best_model.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

    return best_model


def save_model(model, path: Path = MODEL_PATH):
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"Model saved to {path}")


def main():
    ensure_nltk_data()
    df = load_movie_reviews_df()
    model = build_and_train(df)
    save_model(model)

    examples = [
        "I absolutely loved this movie! So emotional and powerful.",
        "This was the worst thing I’ve ever seen. Completely boring.",
        "It’s okay, not too bad but not great either."
    ]
    preds = model.predict(examples)
    print("\nExample Predictions:")
    for text, pred in zip(examples, preds):
        print(f"{pred}\t{text}")


if __name__ == "__main__":
    main()
