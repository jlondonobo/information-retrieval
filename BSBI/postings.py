import array


class UncompressedPostings:
    @staticmethod
    def encode(postings_list: list[int]) -> bytes:
        """Encodes postings_list into a stream of bytes

        Parameters
        ----------
        postings_list: List[int]
            List of docIDs (postings)

        Returns
        -------
        bytes
            bytearray representing integers in the postings_list
        """
        return array.array("L", postings_list).tobytes()

    @staticmethod
    def decode(encoded_postings_list: bytes) -> list[int]:
        """Decodes postings_list from a stream of bytes

        Parameters
        ----------
        encoded_postings_list: bytes
            bytearray representing encoded postings list as output by encode
            function

        Returns
        -------
        List[int]
            Decoded list of docIDs from encoded_postings_list
        """

        decoded_postings_list = array.array("L")
        decoded_postings_list.frombytes(encoded_postings_list)
        return decoded_postings_list.tolist()
