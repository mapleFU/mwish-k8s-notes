import os
import ntpath


def path_leaf(path: str)->str:
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def filename_without_ext(path: str)-> str:
    return os.path.splitext(path)[0]


def filename_ext(path: str) -> str:
    return os.path.splitext(path)[1]


def file_exist(path: str) -> str:
    return os.path.isfile(path)


def dir_path(path: str) -> str:
    os.path.dirname(os.path.abspath(path))


if __name__ == '__main__':
    # test file_exists
    print(file_exist("/Users/fuasahi/Desktop/writing/MapReduce.md"))
    TEST_FILE = "/Users/fuasahi/Desktop/writing/MapReduce.md"
    assert file_exist(TEST_FILE) is True

    assert filename_ext(TEST_FILE) == '.md'
    print(filename_without_ext(TEST_FILE))
