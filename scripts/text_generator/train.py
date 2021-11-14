#%%
import nltk
from typing import Dict, List
import numpy as np
import boto3
import os
import joblib

ROOT_DIR = "./"

#%%
s3 = boto3.resource(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
)

bucket = s3.Bucket(os.getenv("BUCKET_NAME"))

# %%


def dict_normalize(d: Dict[str, float]):
    """Normalize dict of word: count pairs s.t. values sum to one"""
    s = sum(d.values())
    return {k: v / s for k, v in d.items()}


def build_proba_dict(n: int, corpus: str):
    """Build probability dictionary which maps (word1, ..., wordn): {successor1: proba1, ...}"""
    ngrams = nltk.ngrams(corpus, n=n)
    count_dict = {}

    # Create ngrams
    for tup in ngrams:
        key = " ".join(tup[:-1])
        if key not in count_dict:
            count_dict[key] = {tup[-1]: 1}
        else:
            existing_successors = count_dict[key]
            if tup[-1] not in existing_successors.keys():
                existing_successors[tup[-1]] = 1
            else:
                existing_successors[tup[-1]] += 1

    proba_dict = {k: dict_normalize(v) for k, v in count_dict.items()}
    return proba_dict


def get_pdist_from_proba_dict(
    proba_dict: Dict[str, Dict[str, float]], key: List[str], n: int, corpus: List[str]
):
    """Lookup n-gram key in proba_dict. If not found, iteratively back off"""
    proba_dict = proba_dict.copy()
    found_key = False

    while not found_key:
        try:
            p_dist = proba_dict[" ".join(key)]
            found_key = True
        except KeyError:
            key = key[1:]
            proba_dict = build_proba_dict(n - 1, corpus)  # new n-1gram dict
            n = n - 1
            # print(f"[INFO] Backed off. {n = }")

    return p_dist


#%%
def train(
    n: int,
    corpus: List[str],
    upload_to_s3: bool = True,
):
    """Train model and upload to S3"""
    print("[INFO] Starting training.")
    proba_dict = build_proba_dict(n, corpus)

    # S3 upload
    joblib.dump(proba_dict, f"{ROOT_DIR}artifacts/proba_dict.joblib")

    if upload_to_s3:
        bucket.upload_file(
            f"{ROOT_DIR}artifacts/proba_dict.joblib", f"text-generator/proba_dict.joblib"
        )
        print("[INFO] Uploaded model artifacts to S3.")
    print("[INFO] Done with training.")


if __name__ == "__main__":
    corpus = nltk.corpus.gutenberg.raw("austen-sense.txt")
    corpus = nltk.word_tokenize(corpus.lower())
    train(3, corpus)
