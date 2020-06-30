import nltk
from nltk.stem import WordNetLemmatizer
import matplotlib.pyplot as plt
from tabulate import tabulate
import math
import csv
from family_resemblance_tagger.common import config
import os


class PTagException(Exception):
    pass


def get_stops():
    stops = set()

    stopword_path = os.path.dirname(__file__) + "/resources/stopwords.csv"

    if not os.path.isfile(stopword_path):
        raise RuntimeError("Could not find stopwords.csv")

    with open(stopword_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            stops.update(row)
    return stops


def cleanup_text(text):
    text = text.lower()
    text = text.split()
    strip_punct = lambda w: "".join(list(filter(lambda c: c.isalnum(), w)))
    text = list(map(strip_punct, text))
    text = list(filter(lambda w: len(w) >= config.dict["min_token_length"], text))

    stops = get_stops()

    text = list(filter(lambda w: w not in stops, text))
    return list(filter(lambda w: w.isalpha(), text))

def length_threshold(text):
    return list(filter(lambda w: len(w) >= config.dict["min_tag_length"], text))


def lemmatize(text):
    lemmatizer = WordNetLemmatizer()
    return list(map(lambda w: lemmatizer.lemmatize(w), text))

def augment_with_ngrams(tokens):
    n = config.dict["ngram_max"]
    for i in range(2, n+1):
        ngrams_to_add = list(nltk.ngrams(tokens, i))
        for item in ngrams_to_add:
            tokens.append("_".join(item))
    return tokens

def count_tokens(tokens):
    counts = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    sorted_counts = {k: v for k,v in sorted(counts.items(), 
        key=lambda item: item[1], reverse=True)}
    return sorted_counts

def plot_counts(counts, ptags):
    rank_vals = list(range(1, len(counts)+1))
    rank_vals = list(map(lambda x: x / len(counts), rank_vals))

    count_vals = list(counts.values())
    thresh = len(ptags)

    plt.scatter(count_vals[:thresh], rank_vals[:thresh], 
        marker="o", s=30, alpha=0.3, c="green", 
        label="included, n={}".format(thresh))
    plt.scatter(count_vals[thresh:], rank_vals[thresh:], 
        marker="o", s=30, alpha=0.3, c="red", 
        label="excluded, n={}".format(len(counts) - thresh))
    plt.legend()
    plt.xlabel("token count")
    plt.ylabel("fraction of tokens with a greater count (CCDF)")
    plt.title("token distribution in text")
    plt.xscale("log")
    plt.yscale("log")
    plt.show()

def print_counts(counts, percentage=0.001):
    count_data = [(k, v) for k, v in counts.items()]
    end = int(len(count_data)*percentage)
    print(tabulate(count_data[:end]))
    total_count = sum(list(counts.values()))
    print("Total Count: {}".format(total_count))
    top_count = list(counts.values())
    top_count = sum(top_count[:end])
    print("Top {}% Count: {}".format(percentage*100, top_count))
    print("Ratio: {}".format(top_count / total_count))

def calculate_weights(counts):
    weights = counts.copy()
    total = sum(list(counts.values()))
    for key in weights.keys():
        weights[key] /= total

    return weights


def apply_threshold(counts):
    threshold = config.dict["keyword_threshold"]
    goal = sum(list(counts.values())) * threshold
    all_keys = list(counts.keys())

    i = 0
    total = 0

    while(total < goal):
        total += counts[all_keys[i]]
        i += 1
    
    chosen_subset = {}
    if i > 0:
        for key in all_keys[:i]:
            chosen_subset[key] = counts[key]
    else:
        chosen_subset = counts

    return chosen_subset


def extract_keywords(text):

    resource_dir = os.path.dirname(__file__)+"/resources"
    nltk.download("wordnet", download_dir=resource_dir, quiet=True)
    nltk.data.path.append(resource_dir)

    if not text:
        raise PTagException("Text passed to choose_ptags is empty.")
    text = cleanup_text(text)
    tokens = lemmatize(text)
    tokens = augment_with_ngrams(tokens)
    tokens = length_threshold(tokens)
    counts = count_tokens(tokens)
    weighted_counts = calculate_weights(counts)
    weighted_ptags = apply_threshold(weighted_counts)
    
    # print_counts(counts)
    # plot_counts(counts, ptags) 
    if text and not weighted_ptags:
        raise PTagException("Could not find any ptags.")

    return weighted_ptags


if __name__=="__main__":
    test_path = "/home/tim/Documents/projects/family_resemblance_tagger/family_resemblance_tagger/test/choose_ptag_tests/test_A.txt"
    with open(test_path, "r") as f:
        text = f.read()
    print(extract_keywords(text))