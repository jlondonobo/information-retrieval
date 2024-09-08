import time

from BSBI.BSBI import BSBIIndex


def main():
    BSBI_instance = BSBIIndex(data_dir="pa1-skeleton/pa1-data", output_dir="output_dir")

    print("Indexing...")
    BSBI_instance.index()

    while True:
        user_input = input("Query: ")

        start_time = time.time()
        res = BSBI_instance.retrieve(user_input)
        print(f"Search time: {time.time() - start_time:.2f}s")

        print(f"Documents:\n * {"\n * ".join(res[:5])}...")


if __name__ == "__main__":
    main()
