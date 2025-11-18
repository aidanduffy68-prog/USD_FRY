"""
On-Chain Cryptographic Receipt System

Generates minimal cryptographic proofs of intelligence outputs without revealing proprietary systems.
Everything proprietary stays off-chain. Only tiny cryptographic receipts go on-chain.
"""

from nemesis.on_chain_receipt.receipt_generator import (
    CryptographicReceiptGenerator,
    IntelligenceReceipt,
    ReceiptStatus,
    ReceiptVerifier
)

__all__ = [
    "CryptographicReceiptGenerator",
    "IntelligenceReceipt",
    "ReceiptStatus",
    "ReceiptVerifier"
]

