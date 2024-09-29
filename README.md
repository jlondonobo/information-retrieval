# Information Retrieval and Web Search

Implementation of an Information Retrieval system based on [Stanford's CS 276](https://web.stanford.edu/class/cs276/) course.

## Structure

This repository contains the following implementations of an information retrieval system:

- **BSBI**: Block Sort-Based Indexing for efficient document and query indexing.
- **Spelling Corrector**: A probability-based model for suggesting query spelling corrections.

## Installation

To use the modules, install this repo from GitHub via pip/poetry/uv:

```bash
pip install git+https://github.com/jlondonobo/information-retrieval
```

Or clone and install like:

```bash
git clone https://github.com/jlondonobo/information-retrieval
pip install /information-retrieval
```

## Usage

For examples on how to use the modules, check the `notebooks` directory.

### BSBI specifics

The BSBI module uses a specifically formatted input dataset. It must abide by the following format:

- Space-separated tokens.
- Block size of ~1000 documents.
- Input data structure:
  ```
  data/
  ├── 0/
  │   ├── document1.txt
  │   ├── document2.txt
  │   └── ...
  ├── 1/
  │   ├── document1001.txt
  │   ├── document1002.txt
  │   └── ...
  └── 2/
      ├── document2001.txt
      ├── document2002.txt
      └── ...
  ```
  Each folder contains approximately 1000 documents.

## License

This project is licensed under the MIT license.
