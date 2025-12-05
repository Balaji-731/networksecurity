from flask import Flask, render_template, request, redirect, session, url_for
import pandas as pd
import os

from networksecurity.utils.main_utils.feature_extracter import extract_features
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# SECRET KEY FIX
app.secret_key = os.getenv("SESSION_KEY") or "fallback_secret_key"

PREPROCESSOR_PATH = "final_model/preprocessor.pkl"
MODEL_PATH = "final_model/model.pkl"

preprocessor_obj = load_object(PREPROCESSOR_PATH)
model_obj = load_object(MODEL_PATH)

final_model = NetworkModel(preprocessor=preprocessor_obj, model=model_obj)


@app.route("/")
def home():
    result = session.pop("result", None)
    url = session.pop("url", None)
    return render_template("index.html", result=result, url=url)


@app.route("/predict", methods=["POST"])
def predict():
    url = request.form["url"]

    # Extract features
    features = extract_features(url)

    # INVALID URL case
    if features == "INVALID":
        session["result"] = "INVALID_URL"
        session["url"] = url
        return redirect(url_for("home"))

    # Normal case
    df = pd.DataFrame([features])
    prediction = final_model.predict(df)[0]
    result = "SAFE" if prediction == 1 else "UNSAFE"

    session["result"] = result
    session["url"] = url

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
