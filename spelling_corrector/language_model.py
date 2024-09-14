from collections import Counter
from pathlib import Path


class LanguageModel:
    """Models prior probability of unigrams and bigrams."""

    def __init__(
        self, corpus_dir: Path = Path("pa2-data/corpus"), lambda_: float = 0.1
    ):
        """Iterates over all whitespace-separated tokens in each file in
        `corpus_dir`, and counts the number of occurrences of each unigram and
        bigram. Also keeps track of the total number of tokens in the corpus.

        Args:
            corpus_dir (str): Path to directory containing corpus.
            lambda_ (float): Interpolation factor for smoothing by unigram-bigram
                interpolation. You only need to save `lambda_` as an attribute for now, and
                it will be used later in `LanguageModel.get_bigram_logp`. See Section
                IV.1.2. below for further explanation.
        """
        self.lambda_ = lambda_
        self.total_num_tokens = 0  # Counts total number of tokens in the corpus
        self.unigram_counts = Counter()  # Maps strings w_1 -> count(w_1)
        self.bigram_counts = Counter()  # Maps tuples (w_1, w_2) -> count((w_1, w_2))

        for file in corpus_dir.iterdir():
            tokens = file.read_text().split()
            unigrams = tokens
            bigrams = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]

            self.total_num_tokens += len(tokens)
            self.unigram_counts.update(unigrams)
            self.bigram_counts.update(bigrams)
