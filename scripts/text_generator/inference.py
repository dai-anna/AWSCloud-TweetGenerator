# %%
from typing import Dict, List
import numpy as np


try:
    from train import build_proba_dict, get_pdist_from_proba_dict
except ModuleNotFoundError:
    from scripts.text_generator.train import build_proba_dict, get_pdist_from_proba_dict


ROOT_DIR = "./"


def finish_sentence(
    sentence: List[str],
    n: int,
    corpus: list[str],
    deterministic=False,
    max_len: int = 15,
    proba_dict: dict = None,
):
    """Finish sentence using n-grams built on corpus."""

    # Sample next words
    response = sentence.copy()
    for _ in range(max_len):
        # print(f"PREDICTING num #{_}")
        base = response[-n + 1 :]

        # Get distribution over successors. Includes backoff.
        p_dist = get_pdist_from_proba_dict(proba_dict, base, n, corpus)

        if deterministic:
            try:
                generated_word = max(p_dist.items(), key=lambda t: t[1])[0]  # argmax
            except:
                generated_word = "<NA>"
        else:
            generated_word = np.random.choice(list(p_dist.keys()), p=list(p_dist.values()))

        # print(generated_word)
        response.append(generated_word)

        # if any([x in response for x in ".!?"]):
        #     break

    return response


