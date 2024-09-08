import contextlib
import heapq
import pickle as pkl
from pathlib import Path

from tqdm import tqdm

from BSBI.inverted_index import (
    InvertedIndexIterator,
    InvertedIndexMapper,
    InvertedIndexWriter,
)

from .utils import IdMap, sorted_intersect


class BSBIIndex:
    """
    Attributes
    ----------
    term_id_map(IdMap): For mapping terms to termIDs
    doc_id_map(IdMap): For mapping relative paths of documents (eg
        0/3dradiology.stanford.edu_) to docIDs
    data_dir(str): Path to data
    output_dir(str): Path to output index files
    index_name(str): Name assigned to index
    postings_encoding: Encoding used for storing the postings.
        The default (None) implies UncompressedPostings
    """

    def __init__(self, data_dir, output_dir, index_name="BSBI", postings_encoding=None):
        self.term_id_map = IdMap()
        self.doc_id_map = IdMap()
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.index_name = index_name
        self.postings_encoding = postings_encoding

        # Stores names of intermediate indices
        self.intermediate_indices = []

    def save(self):
        """Dumps doc_id_map and term_id_map into output directory"""
        with open((self.output_dir / "terms.dict"), "wb") as f:
            pkl.dump(self.term_id_map, f)
        with open((self.output_dir / "docs.dict"), "wb") as f:
            pkl.dump(self.doc_id_map, f)

    def load(self):
        """Loads doc_id_map and term_id_map from output directory"""

        with open((self.output_dir / "terms.dict"), "rb") as f:
            self.term_id_map = pkl.load(f)
        with open((self.output_dir / "docs.dict"), "rb") as f:
            self.doc_id_map = pkl.load(f)

    def index(self):
        """Base indexing code

        This function loops through the data directories,
        calls parse_block to parse the documents
        calls invert_write, which inverts each block and writes to a new index
        then saves the id maps and calls merge on the intermediate indices
        """
        dirs = [obj for obj in self.data_dir.iterdir() if obj.is_dir()]
        for block_dir_relative in dirs:
            td_pairs = self.parse_block(block_dir_relative)
            index_id = "index_" + block_dir_relative.name
            self.intermediate_indices.append(index_id)
            with InvertedIndexWriter(
                index_id,
                directory=self.output_dir,
                postings_encoding=self.postings_encoding,
            ) as index:
                self.invert_write(td_pairs, index)
                td_pairs = None
        self.save()
        with InvertedIndexWriter(
            self.index_name,
            directory=self.output_dir,
            postings_encoding=self.postings_encoding,
        ) as merged_index:
            with contextlib.ExitStack() as stack:
                indices = [
                    stack.enter_context(
                        InvertedIndexIterator(
                            index_id,
                            directory=self.output_dir,
                            postings_encoding=self.postings_encoding,
                        )
                    )
                    for index_id in self.intermediate_indices
                ]
                self.merge(indices, merged_index)

    def parse_block(self, block_dir: Path) -> list[tuple[int, int]]:
        """Parses a tokenized text file into termID-docID pairs

        Parameters
        ----------
        block_dir_relative : str
            Relative Path to the directory that contains the files for the block

        Returns
        -------
        List[Tuple[Int, Int]]
            Returns all the td_pairs extracted from the block

        Should use self.term_id_map and self.doc_id_map to get termIDs and docIDs.
        These persist across calls to parse_block
        """
        pair_collection = []
        for file in tqdm(sorted(block_dir.iterdir())):
            file_str = file.relative_to(block_dir.parent)
            doc_id = self.doc_id_map[str(file_str)]
            terms = set(file.read_text().split())
            pairs = [(self.term_id_map[term], doc_id) for term in terms]
            pair_collection.extend(pairs)
        return pair_collection

    def invert_write(self, td_pairs: tuple[int, int], index: InvertedIndexWriter):
        """Inverts td_pairs into postings_lists and writes them to the given index"""

        ### Begin your code
        sorted_pairs = sorted(td_pairs, key=lambda pair: self.term_id_map[pair[0]])

        current_postings = [sorted_pairs[0][1]]
        prev_term = sorted_pairs[0][0]

        for term_id, doc_id in sorted_pairs[1:]:
            if term_id != prev_term:
                index.append(prev_term, current_postings)
                current_postings = [doc_id]
            else:
                current_postings.append(doc_id)
            prev_term = term_id

        if current_postings:
            index.append(prev_term, current_postings)

    def merge(
        self, indices: list[InvertedIndexIterator], merged_index: InvertedIndexWriter
    ):
        """Merges multiple inverted indices into a single index

        Parameters
        ----------
        indices: List[InvertedIndexIterator]
            A list of InvertedIndexIterator objects, each representing an
            iterable inverted index for a block
        merged_index: InvertedIndexWriter
            An instance of InvertedIndexWriter object into which each merged
            postings list is written out one at a time
        """
        with merged_index:
            heap = []

            for index_id, index in enumerate(indices):
                try:
                    term_id, postings = next(index)
                    term = self.term_id_map[term_id]
                    heapq.heappush(heap, (term, index_id, term_id, postings))
                except StopIteration:
                    # Skip empty indices
                    continue

            while heap:
                current_term, iterator_index, term_id, postings = heapq.heappop(heap)

                # Collect all postings for the current term
                all_postings = [postings]
                processed_iterators = [iterator_index]
                while heap and heap[0][0] == current_term:
                    _, next_iterator_idx, _, postings = heapq.heappop(heap)
                    all_postings.append(postings)
                    processed_iterators.append(next_iterator_idx)

                # Merge and write postings
                merged_postings = list(heapq.merge(*all_postings))
                merged_index.append(term_id, merged_postings)

                # Get next item from all iterators that were just processed
                for idx in processed_iterators:
                    try:
                        term_id, postings = next(indices[idx])
                        term = self.term_id_map[term_id]
                        heapq.heappush(heap, (term, idx, term_id, postings))
                    except StopIteration:
                        pass  # Iterator exhausted

    def retrieve(self, query: str) -> list[str]:
        """Retrieves the documents corresponding to the conjunctive query

        Parameters
        ----------
        query: str
            Space separated list of query tokens

        Result
        ------
        List[str]
            Sorted list of documents which contains each of the query tokens.
            Should be empty if no documents are found.

        Should NOT throw errors for terms not in corpus
        """
        if len(self.term_id_map) == 0 or len(self.doc_id_map) == 0:
            self.load()

        query_terms = query.split()
        if not query_terms:
            return []

        postings_lists = []

        with InvertedIndexMapper(self.index_name, directory=self.output_dir) as index:
            for term in query_terms:
                term_id = self.term_id_map[term]
                postings = index[term_id]
                postings_lists.append(postings)
        if not postings_lists:
            return []

        result = postings_lists[0]
        for postings in postings_lists[1:]:
            result = sorted_intersect(result, postings)

        return [self.doc_id_map[doc_id] for doc_id in result]
