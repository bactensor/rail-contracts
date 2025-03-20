from __future__ import annotations

from typing import TYPE_CHECKING

from bittensor.core.extrinsics.serving import get_metadata, publish_metadata
from ecdsa.curves import SECP256k1
from ecdsa.errors import MalformedPointError
from ecdsa.keys import BadSignatureError, SigningKey, VerifyingKey
from eth_utils import keccak, to_checksum_address

if TYPE_CHECKING:
    import bittensor_wallet
    from bittensor import Subtensor


def create_knowledge_commitment_data(hotkey: str, private_key: SigningKey) -> bytes:
    public_key: bytes = private_key.get_verifying_key().to_string()
    signature: bytes = private_key.sign(hotkey.encode())
    return public_key + signature


def ethereum_h160_address(data: bytes) -> bytes:
    hashed = keccak(data)
    return to_checksum_address(hashed[-20:])


def unpack_knowledge_commitment_data(hotkey: str, data: bytes) -> str | None:
    public_key_bytes: bytes = data[:64]
    try:
        public_key: VerifyingKey = VerifyingKey.from_string(public_key_bytes, curve=SECP256k1)
    except MalformedPointError:
        return None

    signature: bytes = data[64:]
    try:
        if not public_key.verify(signature, hotkey.encode()):
            return None
    except BadSignatureError:
        return None

    return ethereum_h160_address(public_key_bytes)


def put_h160_address(
    wallet: bittensor_wallet.Wallet,
    subtensor: Subtensor,
    netuid: int,
    private_key: SigningKey,
) -> None:
    """Publish knowledge commitment associating h160 with bittensor wallets.

    Args:
        wallet: Bittensor wallet to push knowledge commitment with
        subtensor: subtensor
        netuid: subnet netuid
        private_key: SigningKey representing the h160 private key to be assosiated with ss58 wallet 
            Create for example with:
            - From an `account.key` of `eth_account` package 
              ```python
              private_key: SigningKey = SigningKey.from_string(account.key, curve=SECP256k1)
              ```
            - From raw private key bytes:
              ```python
              private_key: SigningKey = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
              ```
            - From a hex string:
              ```python
              private_key: SigningKey = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
              ```
    Raises: 
        Subtensor API exceptions
    """
    data: bytes = create_knowledge_commitment_data(wallet.hotkey.ss58_address, private_key)
    publish_metadata(
        subtensor,
        wallet,
        netuid,
        data_type=f'Raw{len(data)}',
        data=data,
        wait_for_inclusion=True,
        wait_for_finalization=True,
    )


def get_h160_address(subtensor: Subtensor, netuid: int, hotkey: str) -> str | None:
    """Get h160 address from knowledge commitment of a hotkey.

    Args:
        subtensor: subtensor
        netuid: subnet's netuid
        hotkey: hotkey to get h160 assosiated with
    
    Returns:
        None if there is no association, data is corrupted or association verification fails
        0x prefixed h160 address otherwise
    
    Raises: 
        Subtensor API exceptions
    """
    metadata: dict = get_metadata(  # type: ignore
        subtensor, netuid, hotkey
    )
    try:
        # This structure is hardcoded in bittensor publish_metadata function, but corresponding get_metadata
        # function does not use it, so we need to extract the value manually.
        fields = metadata['info']['fields']
        field = fields[0][0]
        for data_type in field.keys():
            if data_type.startswith('Raw'):
                break
        else:
            return None

        data = bytes(field[data_type][0])
    except (TypeError, LookupError):
        return None

    return unpack_knowledge_commitment_data(hotkey, data)


def test_bridge_data() -> None:
    from eth_account import Account
    account = Account.create('KEYSMASH FJAFJKLDSKF7JKFDJ 1530')
    address = account.address
    signing_key = SigningKey.from_string(account.key, curve=SECP256k1)
    data = create_knowledge_commitment_data("test_hotkey", signing_key)
    unpacked_address = unpack_knowledge_commitment_data("test_hotkey", data)
    assert address == unpacked_address


test_bridge_data()
