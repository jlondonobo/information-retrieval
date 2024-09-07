from pathlib import Path

import pytest

from BSBI.BSBI import BSBIIndex


@pytest.fixture
def temp_block_dir(tmp_path):
    block_dir = tmp_path / "block1"
    block_dir.mkdir()

    # Create sample files
    (block_dir / "doc1.txt").write_text("hello hello world")
    (block_dir / "doc2.txt").write_text("hello python")
    (block_dir / "doc3.txt").write_text("world of python")

    return block_dir

@pytest.fixture
def bsbi_index(tmp_path, temp_block_dir):
    return BSBIIndex(data_dir=tmp_path, output_dir=tmp_path)

def test_parse_block(bsbi_index, temp_block_dir):
    # Call parse_block
    result = bsbi_index.parse_block(temp_block_dir)

    # Check the result
    assert len(result) == 7  # Total number of term-doc pairs
    
    # Check if all doc_ids are present
    doc_ids = set(pair[1] for pair in result)
    assert len(doc_ids) == 3  # We have 3 documents

    # Check if all terms are present
    terms = set(bsbi_index.term_id_map[term_id] for term_id, _ in result)
    assert terms == {"hello", "world", "python", "of"}
    
    # Check for duplicate tuples
    assert len(result) == len(set(result)), "Duplicate tuples found in the result"