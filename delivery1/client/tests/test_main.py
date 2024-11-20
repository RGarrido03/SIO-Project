from pathlib import Path

# prepare env
import pytest
import os
from main import app
from typer.testing import CliRunner

runner = CliRunner()

# global variables
DIR_KEYS = "./temp"
PRIV_KEY_FILE = f"{DIR_KEYS}/my_test_key"
PUB_KEY_FILE = f"{DIR_KEYS}/my_test_key.pub"
REP_PUB_KEY_FILE = f"{DIR_KEYS}/repo_key.pub"
PASSWORD_SECRET_FOR_KEYS = "test_password"
ORG1 = "UA"
ORG2 = "FindIt"
USERS_ORG1 = [
    ("andre", "Andre Ribeiro", "andre@ua.pt"),
    ("ruben", "Ruben garrido", "ruben@ua.pt"),
]
USERS_ORG2 = [
    ("luis", "Luis Matos", "luis@findit.pt"),
    ("pedro", "Pedro Manuel", "pedro@findit.pt"),
]
SESSION_FILES_ORG1 = f"{DIR_KEYS}/session/{ORG1}"
SESSION_FILES_ORG2 = f"{DIR_KEYS}/session/{ORG2}"
REP_ADDRESS = "localhost:8000"
TEST_FILES_DIR = "tests/test_files"


@pytest.fixture(scope="session")
def prepare_env():
    os.environ["REP_ADDRESS"] = REP_ADDRESS
    os.environ["REP_PUB_KEY"] = REP_PUB_KEY_FILE


def test_1_ping(prepare_env):
    result = runner.invoke(app, ["rep_ping"])
    assert result.exit_code == 0


def test_2_get_public_key(prepare_env):
    result = runner.invoke(app, ["rep_get_pub_key", REP_PUB_KEY_FILE])
    assert result.exit_code == 0


def test_3_generate_keys(prepare_env):
    result = runner.invoke(
        app, ["rep_subject_credentials", PASSWORD_SECRET_FOR_KEYS, PRIV_KEY_FILE]
    )
    assert result.exit_code == 0


def test_4_create_organizations(prepare_env):
    # o andre e o luis estao nas orgs 1 e 2 respectivamente
    result = runner.invoke(
        app,
        [
            "rep_create_org",
            ORG1,
            USERS_ORG1[0][0],
            '"' + USERS_ORG1[0][1] + '"',
            USERS_ORG1[0][2],
            PUB_KEY_FILE,
        ],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "rep_create_org",
            ORG2,
            USERS_ORG2[0][0],
            USERS_ORG2[0][1],
            USERS_ORG2[0][2],
            PUB_KEY_FILE,
        ],
    )
    assert result.exit_code == 0


def test_5_create_session(prepare_env):
    # rep_create_session <organization> <username> <password> <private key file>
    session_file_andre = f"{DIR_KEYS}/session/{ORG1}/{USERS_ORG1[0][0]}"
    result = runner.invoke(
        app,
        [
            "rep_create_session",
            ORG1,
            USERS_ORG1[0][0],
            PASSWORD_SECRET_FOR_KEYS,
            PRIV_KEY_FILE,
            session_file_andre,
        ],
    )
    assert result.exit_code == 0

    session_file_luis = f"{DIR_KEYS}/session/{ORG2}/{USERS_ORG2[0][0]}"
    result = runner.invoke(
        app,
        [
            "rep_create_session",
            ORG2,
            USERS_ORG2[0][0],
            PASSWORD_SECRET_FOR_KEYS,
            PRIV_KEY_FILE,
            session_file_luis,
        ],
    )
    assert result.exit_code == 0


def test_6_add_doc(prepare_env):
    """
    here we add at least 3 docs to each org
    belongs to authorized commands
    we will test inserting the sema 3 docs to each org
    org1 , org1_user1
        -> doc1
        -> doc2
        -> doc3
    org2, org2_user
        -> doc1
        -> doc2
        -> doc3
    :return:
    """
    # CASO POSITIVO
    # org1 -> andre
    # rep_add_doc <session file> <document name> <file>

    for doc in ["doc1", "doc2", "doc3"]:
        result = runner.invoke(
            app,
            [
                "rep_add_doc",
                f"{SESSION_FILES_ORG1}/{USERS_ORG1[0][0]}",
                doc,
                f"{TEST_FILES_DIR}/{doc}",
            ],
        )
        assert result.exit_code == 0

    # org2 -> luis
    for doc in ["doc1", "doc2", "doc3"]:
        result = runner.invoke(
            app,
            [
                "rep_add_doc",
                f"{SESSION_FILES_ORG2}/{USERS_ORG2[0][0]}",
                doc,
                f"{TEST_FILES_DIR}/{doc}",
            ],
        )
        assert result.exit_code == 0

    # CASO NEGATIVO
    # repete o doc2 numa org
    result = runner.invoke(
        app,
        [
            "rep_add_doc",
            f"{SESSION_FILES_ORG2}/{USERS_ORG2[0][0]}",
            "doc2",
            f"{TEST_FILES_DIR}/doc2",
        ],
    )
    assert result.exit_code == -1


@pytest.fixture
def cleanup_env():
    pass
