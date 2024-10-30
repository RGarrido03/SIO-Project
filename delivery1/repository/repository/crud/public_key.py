from repository.crud.base import CRUDBase
from repository.models.subject import PublicKey, PublicKeyCreate


class CRUDPublicKey(CRUDBase[PublicKey, PublicKeyCreate, str]):
    def __init__(self) -> None:
        super().__init__(PublicKey)


crud_public_key = CRUDPublicKey()
