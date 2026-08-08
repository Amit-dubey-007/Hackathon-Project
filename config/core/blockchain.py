import json
import os

from web3 import Web3
from django.conf import settings

w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))

with open(
    os.path.join(os.path.dirname(__file__), "abi.json"),
    "r"
) as f:
    abi = json.load(f)

contract = w3.eth.contract(
    address=Web3.to_checksum_address(settings.CONTRACT_ADDRESS),
    abi=abi
)


def mint_certificate(
    recipient_wallet,
    candidate_name,
    skill,
    score,
):

    sender = Web3.to_checksum_address(
        settings.WALLET_ADDRESS
    )

    recipient = Web3.to_checksum_address(
        recipient_wallet
    )

    nonce = w3.eth.get_transaction_count(sender)

    tx = contract.functions.mintCertificate(
        recipient,
        candidate_name,
        skill,
        int(score)
    ).build_transaction(
        {
            "from": sender,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.eth.gas_price,
            "chainId": 11155111,
        }
    )

    signed_tx = w3.eth.account.sign_transaction(
        tx,
        settings.PRIVATE_KEY
    )

    tx_hash = w3.eth.send_raw_transaction(
        signed_tx.raw_transaction
    )

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print("SENDER:", sender)
    print("RECIPIENT:", recipient)
    print("CHAIN:", w3.eth.chain_id)

    print(
        f"Recipient already has '{skill}' certificate:",
        contract.functions.hasCertificateForSkill(
            recipient,
            skill
        ).call()
    )

    print(
        "Sender balance:",
        w3.from_wei(w3.eth.get_balance(sender), "ether")
    )

    if receipt.status != 1:
        raise Exception("Blockchain transaction failed.")

    # logs = contract.events.CertificateMinted().process_receipt(receipt)

    print("Receipt Status:", receipt.status)
    print("Logs:", receipt.logs)

    try:
        logs = contract.events.CertificateMinted().process_receipt(receipt)
        print("Decoded logs:", logs)
    except Exception as e:
        print("EVENT DECODING ERROR:", repr(e))
        raise

    token_id = None

    if len(logs) > 0:
        token_id = str(logs[0]["args"]["tokenId"])

    return {
        "token_id": token_id,
        "transaction_hash": receipt.transactionHash.hex(),
    }