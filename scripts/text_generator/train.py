#%%
import nltk
from typing import Dict, List
import numpy as np
import boto3
import os
import joblib
import tempfile
import re
import io

ROOT_DIR = "./"
DATE_REGEX = re.compile(r"\d\d\d\d-\d\d-\d\d")

#%%
s3 = boto3.resource(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
)

bucket = s3.Bucket(os.getenv("BUCKET_NAME"))

# with tempfile.TemporaryFile() as f:
#     bucket.download_fileobj("2021-11-15/clean_out_0.txt", f)
#     f.seek(0)
#     tweets = [x.decode("utf-8").strip() for x in f.readlines()]

# %%


def dict_normalize(d: Dict[str, float]):
    """Normalize dict of word: count pairs s.t. values sum to one"""
    s = sum(d.values())
    return {k: v / s for k, v in d.items()}


def build_proba_dict(n: int, corpus: list[str]):
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
    corpus: list[str],
    upload_to_s3: bool = True,
    most_current_date: str = None,
    model_id: int = 99
):
    """Train model and upload to S3"""
    print("[INFO] Starting training.")
    proba_dict = build_proba_dict(n, corpus)

    # S3 upload
    # joblib.dump(proba_dict, f"{ROOT_DIR}artifacts/proba_dict.joblib")

    if upload_to_s3:
        # bucket.upload_file(
        #     f"{ROOT_DIR}artifacts/proba_dict.joblib",
        #     f"text-generator/proba_dict.joblib",
        # )

        with io.BytesIO() as f:
            joblib.dump(proba_dict, f)
            f.seek(0)
            # bucket.upload_fileobj(f, f"{most_current_date}/model_{model_id}.joblib")


        print("[INFO] Uploaded model artifacts to S3.")
    print("[INFO] Done with training.")


def get_most_current_date_in_s3():
    """Returns the most current folder name in `bucket`"""
    return max([obj.key for obj in bucket.objects.all() if DATE_REGEX.match(obj.key)]).split("/")[0]


def get_available_hashtags(date_aka_folder: str):
    with io.BytesIO() as f:
        bucket.download_fileobj(f"{date_aka_folder}/hashtags.txt", f)
        f.seek(0)
        hashtags = f.read().decode("utf-8").splitlines()
    return hashtags


def get_corpora_for_hashtags(hashtags: list[str]):
    """Returns all available corpora in `bucket/most_current_date`"""

    num_regex = re.compile(r"\/clean_out_(?P<num>\d+).txt")
    corpora_names = [obj.key for obj in bucket.objects.all() if "clean_out_" in obj.key]
    print(f"Found the following corpora: {corpora_names}")

    corpora = dict()
    corpora_numbers = []

    print(corpora_names)
    for corpus_name in corpora_names:
        try:
            number = int(num_regex.search(corpus_name)["num"])
        except ValueError:
            print(f"[ERROR] Could not decode number in file name, defaulting to zero.")
            number = 0
        corpora_numbers.append(number)

        print(f"{number = }")

        with io.BytesIO() as f:
            bucket.download_fileobj(f"{corpus_name}", f)
            f.seek(0)
            corpora[hashtags[number]] = ". ".join([x.decode("utf-8").strip() for x in f.readlines()]).split()

    # print(corpora)
    return corpora, corpora_numbers


if __name__ == "__main__":
    most_current_date = get_most_current_date_in_s3()
    print(f"most current date in s3: {most_current_date}")
    hashtags = get_available_hashtags(most_current_date)
    
    corpora: dict = None
    corpora_numbers: list[int] = None
    corpora, corpora_numbers = get_corpora_for_hashtags(hashtags)

    for corpus, idx in zip(corpora, corpora_numbers):
        print(f"[INFO] Training corpus number {idx}")
        corpus = nltk.word_tokenize(corpus.lower())
        train(3, corpus, most_current_date=most_current_date, model_id=idx)
