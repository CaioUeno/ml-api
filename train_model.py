import pickle

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from core import utils


def main():

    # read data
    df = pd.read_csv(
        "twitter_training.csv", header=None, names=["idx", "source", "class", "text"]
    )

    # map string to int
    df["class"] = df["class"].map({"Negative": -1, "Neutral": 0, "Positive": 1})

    # filter out nan/None values
    df = df[pd.notnull(df["text"]) & pd.notnull(df["class"])].copy()

    X = df["text"].tolist()
    y = df["class"].values

    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.75, random_state=1, stratify=y
    )

    # instantiate a pipe (vectorizer + model)
    pipe = Pipeline(
        [
            ("text_vectorizer", CountVectorizer(max_features=50_000, binary=True)),
            ("naive_bayes", MultinomialNB()),
        ]
    )

    # fit classifier (calibrated)
    calibrated_classifier = CalibratedClassifierCV(pipe, method="sigmoid", cv=10).fit(
        X_train, y_train
    )

    # evaluate and estimate rates
    print(
        f"Accuracy: {accuracy_score(y_valid, calibrated_classifier.predict(X_valid))}"
    )

    y_valid_pred = calibrated_classifier.predict_proba(X_valid)

    # calculate a "confusion matrix" based on probabilities' expected values - average
    estimated_rates = np.empty(shape=(3, 3))  # three classes

    for i, label in enumerate([-1, 0, 1]):

        if (y_valid == label).sum() > 0:
            estimated_rates[i] = y_valid_pred[y_valid == label].mean(axis=0)
        else:
            estimated_rates[i] = np.zeros(3)

    estimated_rates = estimated_rates.T

    # save model
    pickle.dump(
        calibrated_classifier, open(utils.get_config("ml", "model_filename"), "wb")
    )
    np.save("estimated_rates.npy", estimated_rates)


if __name__ == "__main__":
    main()
