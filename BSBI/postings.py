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


class CompressedPostings:
    # If you need any extra helper methods you can add them here
    @staticmethod
    def vb_encode_number(n: int) -> array.array:
        bytes = array.array("L")
        while True:
            bytes.insert(0, n % 128)
            if n < 128:
                break
            n = n // 128
        bytes[len(bytes) - 1] += 128
        return bytes

    @staticmethod
    def encode(postings_list: list[int]) -> bytes:
        """Encodes `postings_list` using gap encoding with variable byte
        encoding for each gap

        Parameters
        ----------
        postings_list: List[int]
            The postings list to be encoded

        Returns
        -------
        bytes:
            Bytes reprsentation of the compressed postings list
            (as produced by `array.tobytes` function)
        """
        gaps = CompressedPostings.vb_encode_number(postings_list[0])
        for i in range(1, len(postings_list)):
            gap = postings_list[i] - postings_list[i - 1]
            gaps.extend(CompressedPostings.vb_encode_number(gap))
        return gaps.tobytes()

    @staticmethod
    def decode(encoded_postings_list: bytes) -> list[int]:
        """Decodes a byte representation of compressed postings list

        Parameters
        ----------
        encoded_postings_list: bytes
            Bytes representation as produced by `CompressedPostings.encode`

        Returns
        -------
        List[int]
            Decoded postings list (each posting is a docIds)
        """
        gaps = []
        n = 0
        for val in encoded_postings_list:
            if val < 128:
                n = 128 * n + val
            else:
                n = 128 * n + (val - 128)
                gaps.append(n)
                n = 0

        # Converts gaps to postings
        postings = [gaps[0]]
        for gap in gaps[1:]:
            postings.append(postings[-1] + gap)
        return postings
