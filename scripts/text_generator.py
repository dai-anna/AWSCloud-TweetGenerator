# %%
import nltk
from typing import Dict, List
import numpy as np
import numba
# %%


def test_generator():
    """Test Markov text generator."""
    corpus = nltk.corpus.gutenberg.raw('austen-sense.txt')
    corpus = nltk.word_tokenize(corpus.lower())

    words = finish_sentence(
        ['she', 'was', 'not'],
        3,
        corpus,
        deterministic=True,
    )
    assert words == ['she', 'was', 'not', 'in', 'the', 'world', '.']


# %%

def dict_normalize(d: Dict[str, float]):
    """ Normalize dict of word: count pairs s.t. values sum to one """
    s = sum(d.values())
    return {k: v/s for k, v in d.items()}


def build_proba_dict(n: int, corpus: str):
    """ Build probability dictionary which maps (word1, ..., wordn): {successor1: proba1, ...} """
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




def get_pdist_from_proba_dict(proba_dict: Dict[str, Dict[str, float]], key: List[str], n: int, corpus: List[str]):
    """ Lookup n-gram key in proba_dict. If not found, iteratively back off """
    proba_dict = proba_dict.copy()
    found_key = False

    while not found_key:
        try:
            p_dist = proba_dict[" ".join(key)]
            found_key = True
        except KeyError:
            key = key[1:]
            proba_dict = build_proba_dict(n-1, corpus)  # new n-1gram dict
            n = n - 1
            print(f"[INFO] Backed off. {n = }")

    return p_dist


def finish_sentence(sentence: List[str], n: int, corpus: List[str], deterministic=False):
    """ Finish sentence using n-grams built on corpus. """
    proba_dict = build_proba_dict(n, corpus)

    # Sample next words
    response = sentence.copy()
    for _ in range(15):
        base = response[-n+1:]

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

        if any([x in response for x in ".!?"]):
            break

    return response


test_generator()


# %%

# Backoff test
corpus = nltk.corpus.gutenberg.raw('austen-sense.txt')
corpus = nltk.word_tokenize(corpus.lower())

print(finish_sentence("THISWORDDOESNOTEXIST she was not".split(), n=5, corpus=corpus))
print(finish_sentence("she was not".split(), n=3, corpus=corpus, deterministic=True))
print(finish_sentence("i found that".split(), n=4, corpus=corpus))
print(finish_sentence("when she saw".split(), n=2, corpus=corpus))

#%%
%%timeit
print(finish_sentence("when she saw".split(), n=3, corpus=corpus))


#%%
import cProfile

with cProfile.Profile() as pr:
    finish_sentence("she was not".split(), n=3, corpus=corpus)

pr.print_stats(sort="tottime")