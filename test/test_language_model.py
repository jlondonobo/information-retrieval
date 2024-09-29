import math
from collections import Counter
from pathlib import Path

import pytest

from spelling_corrector.candidate_generator import CandidateGenerator
from spelling_corrector.edit_probability_model import UniformEditProbabilityModel
from spelling_corrector.language_model import LanguageModel
from spelling_corrector.scorer import CandidateScorer


@pytest.fixture
def tmp_corpus_dir(tmp_path):
    (tmp_path / "doc1.txt").write_text("hello night")
    (tmp_path / "doc2.txt").write_text("hello bye hello night")
    return tmp_path


@pytest.fixture
def language_model(tmp_corpus_dir: Path):
    return LanguageModel(corpus_dir=tmp_corpus_dir)


@pytest.fixture
def real_language_model():
    return LanguageModel(corpus_dir=Path("pa2-data/corpus"))


@pytest.fixture
def edit_probability_model():
    return UniformEditProbabilityModel()


@pytest.fixture
def candidate_generator(
    real_language_model, edit_probability_model
) -> CandidateGenerator:
    return CandidateGenerator(lm=real_language_model, epm=edit_probability_model)


@pytest.fixture
def candidate_scorer(real_language_model, candidate_generator) -> CandidateScorer:
    return CandidateScorer(real_language_model, candidate_generator)


def test_initialization(tmp_corpus_dir: Path):
    model = LanguageModel(corpus_dir=tmp_corpus_dir)

    unigram_counts = Counter(hello=3, night=2, bye=1)
    bigram_counts = Counter(
        {("hello", "night"): 2, ("hello", "bye"): 1, ("bye", "hello"): 1}
    )

    assert model.unigram_counts == unigram_counts
    assert model.bigram_counts == bigram_counts
    assert model.total_num_tokens == 6


def test_full_corpus_init(real_language_model: LanguageModel):
    assert len(real_language_model.unigram_counts) == 347071
    assert len(real_language_model.bigram_counts) == 4497257
    assert real_language_model.total_num_tokens == 25498340


def test_logprobs(real_language_model: LanguageModel):
    query_wo_typo = "stanford university"
    query_w_typo = "stanfrod universit"

    p_wo_typo = math.exp(real_language_model.get_query_logp(query_wo_typo))
    p_w_typo = math.exp(real_language_model.get_query_logp(query_w_typo))
    print('P("{}") == {}'.format(query_wo_typo, p_wo_typo))
    print('P("{}") == {}'.format(query_w_typo, p_w_typo))
    assert (
        p_wo_typo >= p_w_typo
    ), 'Are you sure "{}" should be assigned higher probability than "{}"?'.format(
        query_w_typo, query_wo_typo
    )


def test_edit_model(edit_probability_model):
    EDIT_PROB = 0.05

    # Test a basic edit
    edited, original = "stanfrod", "stanford"
    assert math.isclose(
        edit_probability_model.get_edit_logp(edited, original), math.log(EDIT_PROB)
    )
    # Test a non-edit
    assert math.isclose(
        edit_probability_model.get_edit_logp(original, original),
        math.log(1.0 - EDIT_PROB),
    )


def test_candidate_generator(candidate_generator):
    query = "stanford university"
    num_candidates = 0
    did_generate_original = False
    for candidate, candidate_logp in candidate_generator.get_candidates(query):
        num_candidates += 1
        if candidate == query:
            did_generate_original = True

        assert candidate_generator.get_num_oov(query) == 0

    assert 1e2 <= num_candidates <= 1e4
    assert did_generate_original


@pytest.mark.parametrize(
    ["raw", "expected"],
    [
        ("stanfrod university", "stanford university"),
        ("stanford unviersity", "stanford university"),
        ("sanford university", "stanford university"),
    ],
)
def test_scorer(
    raw: str,
    expected: str,
    candidate_scorer: CandidateScorer,
):
    corrected = candidate_scorer.correct_spelling(raw)
    assert corrected == expected
