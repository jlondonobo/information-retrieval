import os

from BSBI.BSBI import BSBIIndex


def main():
    BSBI_instance = BSBIIndex(data_dir="pa1-skeleton/pa1-data", output_dir="output_dir")
    # print("Indexing...")
    BSBI_instance.index()
    
    BSBI_instance.retrieve("we are")

    for i in range(1, 9):
        with open('pa1-skeleton/dev_queries/query.' + str(i)) as q:
            query = q.read()
            my_results = [os.path.normpath(path) for path in BSBI_instance.retrieve(query)]
            with open('pa1-skeleton/dev_output/' + str(i) + '.out') as o:
                reference_results = [os.path.normpath(x.strip()) for x in o.readlines()]
                assert my_results == reference_results, "Results DO NOT match for query: "+query.strip()
            print("Results match for query:", query.strip())


if __name__ == "__main__":
    main()
