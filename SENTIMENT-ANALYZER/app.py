from flask import Flask, render_template, request
import pickle
from pathlib import Path

app = Flask(__name__)

MODEL_FILE = Path("sentiment_model.pkl")
model = None
try:
    if MODEL_FILE.exists():
        with open(MODEL_FILE, 'rb') as f:
            model = pickle.load(f)
    else:
        model = None
except Exception as e:
    print(f"Failed to load model: {e}")
    model = None


def map_label(label: str) -> str:
    """Map model labels to friendly labels used in the UI."""
    if not isinstance(label, str):
        return str(label)
    l = label.lower()
    if l in ("pos", "positive"):
        return "positive"
    if l in ("neg", "negative"):
        return "negative"
    return l


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    text = request.form.get('text', '')

    if len(text.split()) < 2:
        label = 'neutral'
        confidence = None
        raw = None
        return render_template('index.html', text=text, label=label, confidence=confidence, raw=raw)

    if model is None:
        label = 'unknown'
        confidence = None
        raw = None
        return render_template('index.html', text=text, label=label, confidence=confidence, raw=raw)

    try:
        raw_pred = model.predict([text])[0]
    except Exception:
        raw_pred = None

    label = map_label(raw_pred) if raw_pred is not None else 'unknown'

    confidence = None
    try:
        if hasattr(model, 'predict_proba'):
            probs = model.predict_proba([text])[0]
            # find index of predicted class
            classes = list(model.classes_)
            if raw_pred in classes:
                idx = classes.index(raw_pred)
                confidence = float(probs[idx])
        elif hasattr(model, 'decision_function'):
            df = model.decision_function([text])
            try:
                score = float(df[0]) if hasattr(df[0], '__float__') else float(df)
            except Exception:
                score = None
            confidence = score
    except Exception:
        confidence = None

    return render_template('index.html', text=text, label=label, confidence=confidence, raw=raw_pred)


if __name__ == '__main__':
    app.run(debug=True)
