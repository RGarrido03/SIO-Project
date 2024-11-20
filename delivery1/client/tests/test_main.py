import json
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
    # André and Luis are in org 1 and 2, respectively
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
    # Positive case
    for session_file, user in [(SESSION_FILES_ORG1, USERS_ORG1[0][0]), (SESSION_FILES_ORG2, USERS_ORG2[0][0])]:
        for doc in ["doc1", "doc2", "doc3"]:
            result = runner.invoke(
                app,
                [
                    "rep_add_doc",
                    f"{session_file}/{user}",
                    doc,
                    f"{TEST_FILES_DIR}/{doc}",
                ],
            )
            assert result.exit_code == 0

    # Negative case
    # Repeats doc2 in an organization
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


def test_7_list_docs(prepare_env):
    result = runner.invoke(
        app,
        [
            "rep_list_docs",
            f"{SESSION_FILES_ORG1}/{USERS_ORG1[0][0]}",
        ],
    )
    assert result.exit_code == 0


def test_8_list_orgs(prepare_env):
    result = runner.invoke(
        app,
        ["rep_list_orgs"],
    )
    assert result.exit_code == 0

def test_9_list_subjects(prepare_env):
    result = runner.invoke(
        app,
        ["rep_list_subjects", f"{SESSION_FILES_ORG1}/{USERS_ORG1[0][0]}"],
    )
    assert result.exit_code == 0


def test_10_get_doc_file(prepare_env):
    # Positive and negative case
    for name, code in [("doc1", 0), ("doc4", -1)]:
        result = runner.invoke(
            app,
            [
                "rep_get_doc_file",
                f"{SESSION_FILES_ORG1}/{USERS_ORG1[0][0]}",
                name,
                f"{TEST_FILES_DIR}/doc1",
            ],
        )
        assert result.exit_code == code


def test_11_get_doc_metadata(prepare_env):
    # Positive and negative case
    for name, code in [("doc1", 0), ("doc4", -1)]:
        result = runner.invoke(
            app,
            ["rep_get_doc_metadata", f"{SESSION_FILES_ORG1}/{USERS_ORG1[0][0]}", name],
        )
        assert result.exit_code == code



def test_12_decrypt_file(prepare_env):
    # get file_handle
    # Positive
    file_handles = []
    for doc in ["doc1", "doc2"]:
        result = runner.invoke(
            app,
            ["rep_get_doc_metadata", f"{SESSION_FILES_ORG1}/{USERS_ORG1[0][0]}", f"{doc}"],
        )
        with open(f"storage/docs/{ORG1}/{doc}.json", 'r') as f:
            metadata = json.loads(f.read())
        file_handles.append(metadata["file_handle"])
        assert result.exit_code == 0

    # first get file with file_handle
    runner.invoke(app, ["rep_get_file", file_handles[0], f"{TEST_FILES_DIR}/doc1.enc"])
    runner.invoke(app, ["rep_get_file", file_handles[1], f"{TEST_FILES_DIR}/doc2.enc"])

    # Positive and negative case
    for error_code, doc in zip([0,1], ["doc1", "doc2"]):
        # decrypt file
        result = runner.invoke(
            app,
            [
                "rep_decrypt_file",
                f"{TEST_FILES_DIR}/{doc}.enc",
                f"storage/docs/{ORG1}/doc1.json",
            ],
        )

        assert result.exit_code == error_code


def test_13_delete_doc(prepare_env):
    # Positive and negative case
    for name, code in [("doc3", 0), ("doc45", -1)]:
        result = runner.invoke(
            app,
            [
                "rep_delete_doc",
                f"{SESSION_FILES_ORG1}/{USERS_ORG1[0][0]}",
                name,
            ],
        )
        assert result.exit_code == code


def test_14_add_subject(prepare_env):
    # Positive and negative case (duplicate)
    for code in [0, -1]:
        result = runner.invoke(
            app,
            [
                "rep_add_subject",
                f"{SESSION_FILES_ORG1}/{USERS_ORG1[0][0]}",
                USERS_ORG1[1][0],
                USERS_ORG1[1][1],
                USERS_ORG1[1][2],
                PUB_KEY_FILE,
            ],
        )
        assert result.exit_code == code


def test_15_suspend_subject(prepare_env):
    # Positive and negative case
    for username, code in [(USERS_ORG1[1][0], 0), ("not_found_user", -1)]:
        result = runner.invoke(
            app,
            [
                "rep_suspend_subject",
                f"{SESSION_FILES_ORG1}/{USERS_ORG1[0][0]}",
                username,
            ],
        )
        assert result.exit_code == code

def test_16_activate_subject(prepare_env):
    # Positive and negative case
    for username, code in [(USERS_ORG1[1][0], 0), ("not_found_user", -1)]:
        result = runner.invoke(
            app,
            [
                "rep_activate_subject",
                f"{SESSION_FILES_ORG1}/{USERS_ORG1[0][0]}",
                username,
            ],
        )
        assert result.exit_code == code