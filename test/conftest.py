import shutil
import pytest
import os

TEST_OUTPUT_FOLDER = "output" + os.sep + "demo"


def get_test_file_path(filename):
    return TEST_OUTPUT_FOLDER + os.sep + filename


@pytest.fixture(autouse=True)
def run_around_tests():
    if os.path.exists(TEST_OUTPUT_FOLDER):
        shutil.rmtree(TEST_OUTPUT_FOLDER)
    os.mkdir(TEST_OUTPUT_FOLDER)
    yield
    if os.path.exists(TEST_OUTPUT_FOLDER):
        shutil.rmtree(TEST_OUTPUT_FOLDER)