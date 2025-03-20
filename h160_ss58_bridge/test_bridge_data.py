from eth_account import Account
from ecdsa.curves import SECP256k1
from ecdsa.keys import SigningKey

from knowledge_commitment import create_knowledge_commitment_data, unpack_knowledge_commitment_data


def test_bridge_data() -> None:
    account = Account.create('KEYSMASH FJAFJKLDSKF7JKFDJ 1530')
    address = account.address
    signing_key = SigningKey.from_string(account.key, curve=SECP256k1)
    data = create_knowledge_commitment_data("test_hotkey", signing_key)
    unpacked_address = unpack_knowledge_commitment_data("test_hotkey", data)
    assert address == unpacked_address


