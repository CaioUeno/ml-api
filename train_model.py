import pickle

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import cross_val_score
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

    # instantiate a pipe (vectorizer + model)
    pipe = Pipeline(
        [
            ("text_vectorizer", CountVectorizer(max_features=50_000, binary=True)),
            ("naive_bayes", MultinomialNB()),
        ]
    )

    scores = cross_val_score(pipe, X, y, n_jobs=-1, cv=10)
    print(f"Score average: {np.mean(scores):.4f}")

    # train model with the whole data and save it
    pipe.fit(X, y)

    # save model
    pickle.dump(pipe, open(utils.get_config("ml", "model_filename"), "wb"))


if __name__ == "__main__":
    main()
