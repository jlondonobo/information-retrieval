from BSBI.inverted_index import InvertedIndexMapper, InvertedIndexWriter
from BSBI.postings import UncompressedPostings


def test_inverted_index_mapper():
    with InvertedIndexMapper("BSBI", directory="toy_output_dir") as index:
        first_key = list(index.postings_dict.keys())[0]
        _, n_postings, _ = index.postings_dict[first_key]
        assert len(index[first_key]) == n_postings
