"""
AWS KMS Signer Implementation.

Adapts AWS KMS to the Encypher Signer protocol.
"""

import logging
from typing import Optional, cast

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AWSSigner:
    """
    Signs data using an AWS KMS Customer Master Key (CMK).
    Implements the Signer protocol required by encypher-ai.
    """

    def __init__(
        self,
        key_id: str,
        region_name: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        """
        Initialize AWS KMS Signer.

        Args:
            key_id: The AWS KMS Key ID or ARN.
            region_name: AWS Region.
            aws_access_key_id: Optional AWS access key.
            aws_secret_access_key: Optional AWS secret key.
        """
        self.key_id = key_id
        self.client = boto3.client(
            "kms",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def sign(self, data: bytes) -> bytes:
        """
        Sign data using AWS KMS.

        Args:
            data: The data to sign (bytes).

        Returns:
            The raw signature bytes.
        """
        try:
            # AWS KMS expects 'Message' to be bytes.
            # For ED25519, MessageType must be 'RAW'.
            response = self.client.sign(KeyId=self.key_id, Message=data, MessageType="RAW", SigningAlgorithm="ED25519")
            signature = cast(bytes, response["Signature"])
            return signature
        except ClientError as e:
            logger.error(f"AWS KMS Signing failed: {e}")
            raise RuntimeError(f"AWS KMS Signing failed: {e}") from e
