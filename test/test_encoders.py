import array

from BSBI.postings import CompressedPostings


def test_encode_number():
    number = 5
    res = CompressedPostings.vb_encode_number(number)
    expected = array.array("L", [133])
    assert res == expected


def test_encode_large_number():
    number = 824
    res = CompressedPostings.vb_encode_number(number)
    expected = array.array("L", [6, 184])
    assert res == expected

def test_encode_decode():
    postings = [10, 20]
    e = CompressedPostings.encode(postings)
    d = CompressedPostings.decode(e)
    assert d == postings
