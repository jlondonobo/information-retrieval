import itertools

from spelling_corrector.edit_probability_model import (
    BaseEditProbabilityModel,
)
from spelling_corrector.language_model import LanguageModel


class CandidateGenerator:
    # Alphabet to use for insertion and substitution
    alphabet = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        " ",
        ",",
        ".",
        "-",
    ]

    def __init__(self, lm: LanguageModel, epm: BaseEditProbabilityModel):
        """
        Args:
            lm (LanguageModel): Language model to use for prior probabilities, P(Q).
            epm (EditProbabilityModel): Edit probability model to use for P(R|Q).
        """
        self.lm = lm
        self.epm = epm

    def get_num_oov(self, query: str) -> int:
        """Get the number of out-of-vocabulary (OOV) words in `query`."""
        return sum(1 for w in query.strip().split() if w not in self.lm.unigram_counts)

    def filter_and_yield(self, query: str, lp: float):
        if query.strip() and self.get_num_oov(query) == 0:
            yield query, lp

    def generate_edit1(self, term: str) -> list[str]:
        splits = [(term[:i], term[i:]) for i in range(len(term) + 1)]
        delete = [L + R[1:] for L, R in splits if R]
        transpose = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replace = [
            L + c + R[1:] for L, R in splits if R for c in self.alphabet if c != R[0]
        ]
        insert = [L + c + R for L, R in splits for c in self.alphabet]
        return [
            candidate
            for candidate in set(delete + transpose + replace + insert)
            if candidate in self.lm.unigram_counts and candidate != term
        ]

    def get_candidates(self, query: str):
        """Starts from `query`, and performs EDITS OF DISTANCE <=2 to get candidates"

        Args:
            query (str): Starting query.

        Returns:
            Iterable over tuples (cdt, cdt_edit_logp) of candidates and
                their associated edit log-probabilities. Return value could be
                a list or a generator yielding tuples of this form.
        """
        # Yield the unedited query first
        # We provide this line as an example of how to use `self.filter_and_yield`
        yield from self.filter_and_yield(query, self.epm.get_edit_logp(query, query))

        terms = query.strip().split()

        single_candidates = []
        double_candidates = []
        for idx, term in enumerate(terms):
            single = self.generate_edit1(term)
            double = [e for edit in single for e in self.generate_edit1(edit)]
            single_candidates.append(single)
            double_candidates.append(double)

        # One edit
        for idx, term in enumerate(terms):
            for candidate in single_candidates[idx]:
                t = terms.copy()
                t[idx] = candidate
                new_query = " ".join(t)
                edit_logp = self.epm.get_edit_logp(query, new_query)
                yield from self.filter_and_yield(new_query, edit_logp)

        # Two edits
        for idx, term in enumerate(terms):
            for candidate in double_candidates[idx]:
                t = terms.copy()
                t[idx] = candidate
                new_query = " ".join(t)
                edit_logp = self.epm.get_edit_logp(query, new_query)
                yield from self.filter_and_yield(new_query, edit_logp)

        # Two single edits
        for i, j in itertools.combinations(range(len(terms)), 2):
            for cand_i, cand_j in itertools.product(
                single_candidates[i], single_candidates[j]
            ):
                if (
                    cand_i != terms[i] and cand_j != terms[j]
                ):  # Ensure at least one term changed
                    t = terms.copy()
                    t[i], t[j] = cand_i, cand_j
                    new_query = " ".join(t)
                    edit_logp = self.epm.get_edit_logp(query, new_query)
                    yield from self.filter_and_yield(new_query, edit_logp)
