import math
from pathlib import Path

from spelling_corrector.candidate_generator import CandidateGenerator
from spelling_corrector.edit_probability_model import UniformEditProbabilityModel
from spelling_corrector.language_model import LanguageModel


def main():
    corpus_dir = Path("pa2-data/corpus")

    lm = LanguageModel(corpus_dir)
    epm = UniformEditProbabilityModel()
    cg = CandidateGenerator(lm, epm)

    while True:
        raw = input("Query: ")
        candidates = list(cg.get_candidates(raw))
        print(f"Candidates for '{raw}':")
        i = 0
        for candidate, logp in candidates:
            if i > 5:
                print("  ...")
                break
            print(f"  {candidate}")
            i += 1
        print(f"Total candidates: {len(candidates)}")


if __name__ == "__main__":
    main()
