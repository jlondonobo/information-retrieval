class BSBIIndex(BSBIIndex):            
    def parse_block(self, block_dir_relative: str):
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
        ### Begin your code
        
        # Get a list of files and read them
        # Split by spaces for a document and create term to docID
        # Sort by terms
        pair_collection = []
        block_dir = os.path.join(self.data_dir, block_dir_relative)
        for file in os.listdir(block_dir):
            filepath = os.path.join(block_dir, file)
            doc_id = self.doc_id_map[filepath]
            with open(filepath, "rt") as f:
                pairs = [(self.term_id_map[term], doc_id) for term in f.read().split()]
                pair_collection.extend(pairs)
        return sorted(pair_collection, key=lambda pair: self.term_id_map[pair[0]])
        
        ### End your code
