import pickle as pkl
from pathlib import Path

from .postings import UncompressedPostings


class InvertedIndex:
    """A class that implements efficient reads and writes of an inverted index
    to disk

    Attributes
    ----------
    postings_dict: Dictionary mapping: termID->(start_position_in_index_file,
                                                number_of_postings_in_list,
                                               length_in_bytes_of_postings_list)
        This is a dictionary that maps from termIDs to a 3-tuple of metadata
        that is helpful in reading and writing the postings in the index file
        to/from disk. This mapping is supposed to be kept in memory.
        start_position_in_index_file is the position (in bytes) of the postings
        list in the index file
        number_of_postings_in_list is the number of postings (docIDs) in the
        postings list
        length_in_bytes_of_postings_list is the length of the byte
        encoding of the postings list

    terms: List[int]
        A list of termIDs to remember the order in which terms and their
        postings lists were added to index.

        After Python 3.7 we technically no longer need it because a Python dict
        is an OrderedDict, but since it is a relatively new feature, we still
        maintain backward compatibility with a list to keep track of order of
        insertion.
    """

    def __init__(
        self, index_name: str, postings_encoding=None, directory: str | Path = ""
    ):
        """
        Parameters
        ----------
        index_name (str): Name used to store files related to the index
        postings_encoding: A class implementing static methods for encoding and
            decoding lists of integers. Default is None, which gets replaced
            with UncompressedPostings
        directory (str): Directory where the index files will be stored
        """
        dir = Path(directory)

        self.index_file_path = dir / f"{index_name}.index"
        self.metadata_file_path = dir / f"{index_name}.dict"

        if postings_encoding is None:
            self.postings_encoding = UncompressedPostings
        else:
            self.postings_encoding = postings_encoding
        self.directory = directory

        self.postings_dict = {}
        self.terms = []  # Need to keep track of the order in which the
        # terms were inserted. Would be unnecessary
        # from Python 3.7 onwards

    def __enter__(self):
        """Opens the index_file and loads metadata upon entering the context"""
        # Open the index file
        self.index_file = self.index_file_path.open("rb+")

        # Load the postings dict and terms from the metadata file
        with open(self.metadata_file_path, "rb") as f:
            self.postings_dict, self.terms = pkl.load(f)
            self.term_iter = self.terms.__iter__()

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """Closes the index_file and saves metadata upon exiting the context"""
        # Close the index file
        self.index_file.close()

        # Write the postings dict and terms to the metadata file
        with open(self.metadata_file_path, "wb") as f:
            pkl.dump([self.postings_dict, self.terms], f)


class InvertedIndexWriter(InvertedIndex):
    def __enter__(self):
        self.index_file = self.index_file_path.open("wb+")
        return self

    def append(self, term: str | int, postings_list: list[int]):
        """Appends the term and postings_list to end of the index file.

        This function does three things,
        1. Encodes the postings_list using self.postings_encoding
        2. Stores metadata in the form of self.terms and self.postings_dict
           Note that self.postings_dict maps termID to a 3 tuple of
           (start_position_in_index_file,
           number_of_postings_in_list,
           length_in_bytes_of_postings_list)
        3. Appends the bytestream to the index file on disk

        Hint: You might find it helpful to read the Python I/O docs
        (https://docs.python.org/3/tutorial/inputoutput.html) for
        information about appending to the end of a file.

        Parameters
        ----------
        term:
            term or termID is the unique identifier for the term
        postings_list: List[Int]
            List of docIDs where the term appears
        """
        byte_postings = self.postings_encoding.encode(postings_list)

        postings_len = len(postings_list)
        byte_postings_len = len(byte_postings)

        self.terms.append(term)
        start_position = self.index_file.tell()
        self.index_file.write(byte_postings)
        self.postings_dict[term] = (start_position, postings_len, byte_postings_len)


class InvertedIndexIterator(InvertedIndex):
    """"""

    def __enter__(self):
        """Adds an initialization_hook to the __enter__ function of super class"""
        super().__enter__()
        self._initialization_hook()
        return self

    def _initialization_hook(self):
        """Use this function to initialize the iterator"""
        ### Begin your code
        self.index_file.seek(0)

        ### End your code

    def __iter__(self):
        return self

    def __next__(self) -> tuple[int, list[int]]:
        """Returns the next (term, postings_list) pair in the index.

        Note: This function should only read a small amount of data from the
        index file. In particular, you should not try to maintain the full
        index file in memory.
        """

        try:
            term = next(self.term_iter)
            start, _, byte_len = self.postings_dict[term]

            self.index_file.seek(start)
            byte_postings = self.index_file.read(byte_len)
            postings_list = list(self.postings_encoding.decode(byte_postings))
            return (term, postings_list)
        except StopIteration:
            raise StopIteration("No more terms in the index.")

    def delete_from_disk(self):
        """Marks the index for deletion upon exit. Useful for temporary indices"""
        self.delete_upon_exit = True

    def __exit__(self, exception_type, exception_value, traceback):
        """Delete the index file upon exiting the context along with the
        functions of the super class __exit__ function"""
        self.index_file.close()
        if hasattr(self, "delete_upon_exit") and self.delete_upon_exit:
            self.index_file_path.unlink()
            self.metadata_file_path.unlink()
        else:
            with open(self.metadata_file_path, "wb") as f:
                pkl.dump([self.postings_dict, self.terms], f)


class InvertedIndexMapper(InvertedIndex):
    def __getitem__(self, key):
        return self._get_postings_list(key)

    def _get_postings_list(self, term: int) -> list[int]:
        """Gets a postings list (of docIds) for `term`.

        This function should not iterate through the index file.
        I.e., it should only have to read the bytes from the index file
        corresponding to the postings list for the requested term.
        """
        try:
            start, ndocs, nbytes = self.postings_dict[term]
        except KeyError:
            return []

        self.index_file.seek(start)
        postings_bt = self.index_file.read(nbytes)
        postings = self.postings_encoding.decode(postings_bt)
        return postings
