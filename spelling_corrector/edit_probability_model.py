import math


class BaseEditProbabilityModel:
    def get_edit_logp(self, edited, original):
        """Gets the log-probability of editing `original` to arrive at `edited`.
        The `original` and `edited` arguments are both single terms that are at
        most one edit apart.

        Note: The order of the arguments is chosen so that it reads like an
        assignment expression:
            > edited := EDIT_FUNCTION(original)
        or, alternatively, you can think of it as a (unnormalized) conditional probability:
            > log P(edited | original)

        Args:
            edited (str): Edited term.
            original (str): Original term.

        Returns:
            logp (float): Log-probability of `edited` given `original`
                under this `EditProbabilityModel`.
        """
        raise NotImplementedError  # Force subclass to implement this method


class UniformEditProbabilityModel(BaseEditProbabilityModel):
    def __init__(self, edit_prob=0.05):
        """
        Args:
            edit_prob (float): Probability of a single edit occurring, where
                an edit is an insertion, deletion, substitution, or transposition,
                as defined by the Damerau-Levenshtein distance.
        """
        self.edit_prob = edit_prob

    def get_edit_logp(self, edited: str, original: str) -> float:
        """Gets the log-probability of editing `original` to arrive at `edited`.
        The `original` and `edited` arguments are both single terms that are at
        most one edit apart.

        Note: The order of the arguments is chosen so that it reads like an
        assignment expression:
            > edited := EDIT_FUNCTION(original)
        or, alternatively, you can think of it as a (unnormalized) conditional probability:
            > log P(edited | original)

        Args:
            edited (str): Edited term.
            original (str): Original term.

        Returns:
            logp (float): Log-probability of `edited` given `original`
                under this `EditProbabilityModel`.
        """
        if edited == original:
            return math.log(1 - self.edit_prob)
        else:
            return math.log(self.edit_prob)
