import math
from collections import Counter
from pathlib import Path

from tqdm import tqdm


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

        for file in tqdm(corpus_dir.iterdir()):
            tokens = file.read_text().split()
            unigrams = tokens
            bigrams = [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]

            self.total_num_tokens += len(tokens)
            self.unigram_counts.update(unigrams)
            self.bigram_counts.update(bigrams)

    def get_unigram_logp(self, unigram: str) -> float:
        """Computes the log-probability of `unigram` under this `LanguageModel`.

        Args:
            unigram (str): Unigram for which to compute the log-probability.

        Returns:
            log_p (float): Log-probability of `unigram` under this
                `LanguageModel`.
        """
        prob = self.unigram_counts[unigram] / self.total_num_tokens
        return math.log(prob)

    def get_bigram_logp(self, w_1: str, w_2: str) -> float:
        """Computes the log-probability of `unigram` under this `LanguageModel`.

        Note:
            Use self.lambda_ for the unigram-bigram interpolation factor.

        Args:
            w_1 (str): First word in bigram.
            w_2 (str): Second word in bigram.

        Returns:
            log_p (float): Log-probability of `bigram` under this
                `LanguageModel`.
        """
        prob_seq = self.bigram_counts[(w_1, w_2)] / self.unigram_counts[w_1]
        prob_uni = self.unigram_counts[w_2] / self.total_num_tokens

        interpolation = self.lambda_ * prob_uni + (1 - self.lambda_) * prob_seq
        return math.log(interpolation)

    def get_query_logp(self, query: str) -> float:
        """Computes the log-probability of `query` under this `LanguageModel`.

        Args:
            query (str): Whitespace-delimited sequence of terms in the query.

        Returns:
            log_p (float): Log-probability assigned to the query under this
                `LanguageModel`.
        """
        tokens = query.split()

        probs = self.get_unigram_logp(tokens[0])
        for i in range(1, len(tokens)):
            probs += self.get_bigram_logp(tokens[i - 1], tokens[i])
        return probs
