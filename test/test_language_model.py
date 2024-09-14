from collections import Counter
from pathlib import Path

import pytest

from spelling_corrector.language_model import LanguageModel


@pytest.fixture
def tmp_corpus_dir(tmp_path):
    (tmp_path / "doc1.txt").write_text("hello night")
    (tmp_path / "doc2.txt").write_text("hello bye hello night")
    return tmp_path


@pytest.fixture
def language_model(tmp_corpus_dir: Path):
    return LanguageModel(corpus_dir=tmp_corpus_dir)


def test_initialization(tmp_corpus_dir: Path):
    model = LanguageModel(corpus_dir=tmp_corpus_dir)

    unigram_counts = Counter(hello=3, night=2, bye=1)
    bigram_counts = Counter(
        {("hello", "night"): 2, ("hello", "bye"): 1, ("bye", "hello"): 1}
    )

    assert model.unigram_counts == unigram_counts
    assert model.bigram_counts == bigram_counts
    assert model.total_num_tokens == 6