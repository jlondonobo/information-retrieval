from BSBI.utils import IdMap


def test_idmap():
    testIdMap = IdMap()
    assert testIdMap["a"] == 0, "Unable to add a new string to the IdMap"
    assert testIdMap["bcd"] == 1, "Unable to add a new string to the IdMap"
    assert testIdMap["a"] == 0, "Unable to retrieve the id of an existing string"
    assert testIdMap[1] == "bcd", "Unable to retrive the string corresponding to a\
                                    given id"
    try:
        testIdMap[2]
    except IndexError as e:
        assert True, "Doesn't throw an IndexError for out of range numeric ids"
    assert len(testIdMap) == 2
