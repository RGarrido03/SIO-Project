import tempfile
from pathlib import Path
from typer.testing import CliRunner
from main import app

runner = CliRunner()


# rep_subject_credentials <password> <credentials file>

def test_subject_credentials():
    password = "test_password"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        credentials_file = temp_path / "test_credentials.pem"

    result = runner.invoke(app,
                           ["rep_subject_credentials", password, credentials_file], )

    # assert result.exit_code == 0
# rep_decrypt_file <encrypted file> <encryption metadata>
def test_decrypt_file():

    pass

# rep_create_org <organization> <username> <name> <email> <public key file>
