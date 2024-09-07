class IdMap:
    """Helper class to store a mapping from strings to ids."""

    def __init__(self):
        self.str_to_id = {}
        self.id_to_str = []

    def __len__(self) -> int:
        """Return number of terms stored in the IdMap"""
        return len(self.id_to_str)

    def _get_str(self, i: int) -> str | None:
        """Returns the string corresponding to a given id (`i`)."""
        try:
            return self.id_to_str[i]
        except IndexError:
            return None

    def _get_id(self, s: str) -> int:
        """Returns the id corresponding to a string (`s`).
        If `s` is not in the IdMap yet, then assigns a new id and returns the new id.
        """
        try:
            return self.str_to_id[s]
        except KeyError:
            self.id_to_str.append(s)
            new_id = len(self.id_to_str) - 1
            self.str_to_id[s] = new_id
            return new_id

    def __getitem__(self, key: str | int) -> str | int | None:
        """If `key` is a integer, use _get_str;
        If `key` is a string, use _get_id;"""
        if isinstance(key, int):
            return self._get_str(key)
        elif isinstance(key, str):
            return self._get_id(key)
        else:
            raise TypeError


def sorted_intersect(list1: list[int], list2: list[int]) -> list[int]:
    """Intersects two (ascending) sorted lists and returns the sorted result

    Parameters
    ----------
    list1: List[Comparable]
    list2: List[Comparable]
        Sorted lists to be intersected

    Returns
    -------
    List[Comparable]
        Sorted intersection
    """
    result = []
    i, j = 0, 0
    len1, len2 = len(list1), len(list2)

    while i < len1 and j < len2:
        if list1[i] == list2[j]:
            result.append(list1[i])
            i += 1
            j += 1
        elif list1[i] < list2[j]:
            i += 1
        else:
            j += 1

    return result