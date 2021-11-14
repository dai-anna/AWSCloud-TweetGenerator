# %%
import nltk
from typing import Dict, List
import numpy as np
import boto3
import os
import joblib
from train import build_proba_dict, get_pdist_from_proba_dict
import tempfile

ROOT_DIR = "./"

s3 = boto3.resource(
    service_name="s3",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
)

bucket = s3.Bucket(os.getenv("BUCKET_NAME"))
# bucket.download_file("text-generator/proba_dict.joblib", f"{ROOT_DIR}artifacts/proba_dict.joblib")

with tempfile.TemporaryFile() as f:
    bucket.download_fileobj("text-generator/proba_dict.joblib", f)
    f.seek(0)
    proba_dict = joblib.load(f)

print("[INFO] Model downloaded from S3.")
# proba_dict = joblib.load(f"{ROOT_DIR}artifacts/proba_dict.joblib")

corpus = nltk.corpus.gutenberg.raw("austen-sense.txt")
corpus = nltk.word_tokenize(corpus.lower())


def finish_sentence(
    sentence: List[str], n: int, corpus: List[str], deterministic=False
):
    """Finish sentence using n-grams built on corpus."""

    # Sample next words
    response = sentence.copy()
    for _ in range(15):
        base = response[-n + 1 :]

        # Get distribution over successors. Includes backoff.
        p_dist = get_pdist_from_proba_dict(proba_dict, base, n, corpus)

        if deterministic:
            try:
                generated_word = max(p_dist.items(), key=lambda t: t[1])[0]  # argmax
            except:
                generated_word = "<NA>"
        else:
            generated_word = np.random.choice(
                list(p_dist.keys()), p=list(p_dist.values())
            )

        # print(generated_word)
        response.append(generated_word)

        if any([x in response for x in ".!?"]):
            break

    return response


# %%

# Backoff test

if __name__ == "__main__":
    print(finish_sentence("when she saw".split(), n=3, corpus=corpus))
