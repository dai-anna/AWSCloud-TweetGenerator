#%%
import nltk
from typing import Dict, List
import numpy as np
import boto3
import os
import joblib

from helpers import build_proba_dict, get_pdist_from_proba_dict

#%%
def train(n: int, corpus: List[str],):
    print("[INFO] Starting training.")
    build_proba_dict(n, corpus)
    print("[INFO] Done with training.")

if __name__ == "__main__":
    corpus = nltk.corpus.gutenberg.raw("austen-sense.txt")
    corpus = nltk.word_tokenize(corpus.lower())
    train(3, corpus)