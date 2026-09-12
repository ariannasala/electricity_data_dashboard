# database.py
import io
import os
import zipfile
from pathlib import Path

import oracledb
from cryptography.fernet import Fernet


def prepare_oracle_wallet() -> Path:
    encrypted_wallet_path = Path("data/wallet.zip.enc")
    wallet_directory = Path("/tmp/oracle_wallet")

    encrypted_wallet = encrypted_wallet_path.read_bytes()

    encryption_key = os.environ["WALLET_ENCRIPTING_PASSWORD"].encode()

    fernet = Fernet(encryption_key)

    wallet_zip = fernet.decrypt(encrypted_wallet)

    wallet_directory.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(wallet_zip)) as wallet_archive:
        wallet_archive.extractall(wallet_directory)

    return wallet_directory


def create_oracle_connection():

    wallet_directory = prepare_oracle_wallet()
    return oracledb.connect(
        config_dir=wallet_directory,
        user=os.environ["ORACLE_USER"],
        password=os.environ["ORACLE_PASSWORD"],
        dsn=os.environ["ORACLE_DSN"],
        wallet_location=wallet_directory,
        wallet_password=os.environ["ORACLE_WALLET_PASSWORD"],
    )
