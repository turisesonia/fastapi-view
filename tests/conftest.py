import copy
import os
from pathlib import Path

import pytest
from faker import Faker
from pytest_mock import MockerFixture


@pytest.fixture
def mocker(mocker: MockerFixture) -> MockerFixture:
    return mocker


@pytest.fixture
def faker() -> Faker:
    return Faker()


@pytest.fixture
def tests_path() -> Path:
    return Path(os.path.abspath("tests"))

@pytest.fixture
def templates_path() -> Path:
    return Path(os.path.abspath("tests/templates"))


@pytest.fixture(autouse=True)
def reset_env():
    env = copy.deepcopy(os.environ)
    yield
    os.environ = env
