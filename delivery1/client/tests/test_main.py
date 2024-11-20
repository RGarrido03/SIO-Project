from pathlib import Path

# prepare env
import pytest
import os
from main import app
from typer.testing import CliRunner
runner = CliRunner()

@pytest.fixture
def prepare_env():
    try:
        os.environ["REP_ADDRESS"] = "localhost:8000"
        result = runner.invoke(app, ["rep_ping"])
        if result.exit_code != 0:

            raise Exception("Repository is not available")

        dir_keys = "./temp"
        priv_key_file =f"{dir_keys}/my_test_key"
        pub_key_file =f"{dir_keys}/my_test_key.pub"
        # Public key file vai estar no mesmo sitio mas com .pub
        password_secret_for_keys = "test_password"

        result = runner.invoke(app, ["rep_subject_credentials", password_secret_for_keys, priv_key_file])
        if result.exit_code != 0:
            raise Exception("Error creating subject credentials")

        #get pub key of the repository
        rep_pub_key_file = f"{dir_keys}/repo_key.pub"
        result = runner.invoke(app, ["rep_get_pub_key", rep_pub_key_file])
        if result.exit_code != 0:
            raise Exception("Error getting public key")

        os.environ["REP_PUB_KEY"] = rep_pub_key_file # get it first
    # TODO falr com ruben, uma vez que todos vao usar a mesma key, wich is not good but it's for the test
        #create 2 org
        org1 = "UA"
        org2 = "FindIt"
        users_org1 = [("andre", "Andre Ribeiro", "andre@ua.pt"), ("ruben", "Ruben garrido", "ruben@ua.pt")]
        users_org2 = [("luis", "Luis Matos", "luis@findit.pt"), ("pedro", "Pedro Manuel", "pedro@findit.pt")]
        # rep_create_org <organization> <username> <name> <email> <public key file>
        result = runner.invoke(app, ["rep_create_org", org1, users_org1[0][0], "\"" + users_org1[0][1] + "\"", users_org1[0][2], pub_key_file])

        print(result.exception)
        if result.exit_code != 0:
            raise Exception("Error creating organization 1")

        result = runner.invoke(app, ["rep_create_org", org2, users_org2[1][0], users_org2[1][1], users_org2[1][2], pub_key_file])
        if result.exit_code != 0:
            raise Exception("Error creating organization 2")
         # neste momento o andre e o luis  estao nas orgs 1 e 2 respectivamente



        # create_session
        session_file = f"{dir_keys}/session/{org1}/{users_org1[0][0]}"
        result = runner.invoke(app, ["rep_create_session", org1, users_org1[0][0], password_secret_for_keys, priv_key_file])
        if result.exit_code != 0:
            raise Exception("Error creating session for org1")

    except Exception as e:
        print(e)



def test_prepare_env(prepare_env):
    assert os.environ["REP_ADDRESS"] == "localhost:8000"

@pytest.fixture
def cleanup_env():
    pass