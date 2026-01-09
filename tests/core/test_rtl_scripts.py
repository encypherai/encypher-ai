# ruff: noqa: E501
from datetime import datetime, timezone
from typing import Callable, Optional, cast

import pytest
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes

from encypher.core.keys import generate_ed25519_key_pair as generate_key_pair
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata

# --- Fixtures ---


@pytest.fixture(scope="module")
def key_pair() -> tuple[PrivateKeyTypes, PublicKeyTypes]:
    return generate_key_pair()


@pytest.fixture(scope="module")
def public_key_provider(key_pair) -> Callable[[str], Optional[PublicKeyTypes]]:
    _priv, _pub = key_pair
    signer_id = "rtl-signer-1"

    def provider(signer: str) -> Optional[PublicKeyTypes]:
        if signer == signer_id:
            return cast(PublicKeyTypes, _pub)
        return None

    provider.signer_id = signer_id  # type: ignore[attr-defined]
    return provider


@pytest.mark.parametrize(
    "label,text",
    [
        ("arabic", "هذا نص عربي للاختبار، هل يعمل الترميز؟ نعم!"),
        ("hebrew", "זהו טקסט בעברית לבדיקות – האם ההטמעה עובדת? כן!"),
        ("urdu", "یہ اردو متن جانچ کے لیے ہے، کیا اینکوڈنگ کام کرتی ہے؟ ہاں!"),
        ("hindi", "यह हिन्दी पाठ परीक्षण के लिए है, क्या एन्कोडिंग काम करती है? हाँ!"),
    ],
)
@pytest.mark.parametrize("target", [MetadataTarget.WHITESPACE, MetadataTarget.PUNCTUATION])
def test_embed_verify_extract_rtl_complex_scripts(label, text, target, key_pair, public_key_provider):
    private_key, _ = key_pair
    signer_id = public_key_provider.signer_id  # type: ignore[attr-defined]

    metadata = {
        "model_id": f"test-model-{label}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "custom_metadata": {"lang": label, "purpose": "rtl_complex_test"},
    }

    # Embed metadata
    embedded = UnicodeMetadata.embed_metadata(
        text=text,
        private_key=private_key,
        signer_id=signer_id,
        metadata_format="basic",
        target=target,
        **metadata,
    )

    # Ensure something was embedded
    assert embedded != text
    assert len(embedded) > len(text)

    # Visible text should remain when stripping selectors
    visible = UnicodeMetadata._strip_variation_selectors(embedded)
    assert visible == text

    # Extract without verification
    extracted_unverified = UnicodeMetadata.extract_metadata(embedded)
    assert extracted_unverified is not None
    assert extracted_unverified.get("format") == "basic"
    assert extracted_unverified.get("model_id") == metadata["model_id"]

    # Verify with provider
    is_valid, extracted_signer, verified_payload = UnicodeMetadata.verify_metadata(embedded, public_key_provider)

    assert is_valid is True
    assert extracted_signer == signer_id
    assert verified_payload is not None
    assert verified_payload.get("format") == "basic"
    assert verified_payload.get("model_id") == metadata["model_id"]
    assert verified_payload.get("custom_metadata", {}).get("lang") == label
