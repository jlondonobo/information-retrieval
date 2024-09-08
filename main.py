import os

from BSBI.BSBI import BSBIIndex
from BSBI.postings import CompressedPostings


def test_index(index: BSBIIndex):
    for i in range(1, 9):
        with open("pa1-skeleton/dev_queries/query." + str(i)) as q:
            query = q.read()
            my_results = [os.path.normpath(path) for path in index.retrieve(query)]
            with open("pa1-skeleton/dev_output/" + str(i) + ".out") as o:
                reference_results = [os.path.normpath(x.strip()) for x in o.readlines()]
                assert my_results == reference_results, (
                    "Results DO NOT match for query: " + query.strip()
                )
            print("Results match for query:", query.strip())


def main():
    BSBI_instance = BSBIIndex(data_dir="pa1-skeleton/pa1-data", output_dir="output_dir")
    # BSBI_instance.index()
    test_index(BSBI_instance)
    
    BSBI_instance.retrieve("we are")
   
    BSBI_instance_compressed = BSBIIndex(
        data_dir="pa1-skeleton/pa1-data",
        output_dir="output_dir_compressed",
        postings_encoding=CompressedPostings,
    )
    BSBI_instance_compressed.index()
    test_index(BSBI_instance_compressed)
    
    BSBI_instance_compressed.retrieve("we are")


if __name__ == "__main__":
    main()
