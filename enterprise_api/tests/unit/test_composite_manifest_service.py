"""Unit tests for composite_manifest_service."""

import hashlib
import json
import uuid


def make_ingredient(
    position: int = 0,
    image_id: str = "img_aabbccdd",
    filename: str = "photo.jpg",
    mime_type: str = "image/jpeg",
    c2pa_instance_id: str = "urn:uuid:11111111-1111-1111-1111-111111111111",
    signed_hash: str = "sha256:abc123",
):
    from app.services.composite_manifest_service import ImageIngredient

    return ImageIngredient(
        image_id=image_id,
        filename=filename,
        mime_type=mime_type,
        c2pa_instance_id=c2pa_instance_id,
        signed_hash=signed_hash,
        position=position,
    )


class TestBuildCompositeManifest:
    def test_correct_ingredient_count_single(self):
        from app.services.composite_manifest_service import build_composite_manifest

        img = make_ingredient(position=0)
        result = build_composite_manifest(
            document_id="doc-001",
            org_id="org-001",
            document_title="Test Article",
            text_merkle_root="sha256:deadbeef" + "0" * 55,
            text_instance_id="urn:uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            images=[img],
        )
        assert result.ingredient_count == 1

    def test_correct_ingredient_count_two_images(self):
        from app.services.composite_manifest_service import build_composite_manifest

        img0 = make_ingredient(position=0, image_id="img_00000001", c2pa_instance_id="urn:uuid:11111111-0000-0000-0000-000000000001")
        img1 = make_ingredient(position=1, image_id="img_00000002", c2pa_instance_id="urn:uuid:11111111-0000-0000-0000-000000000002")
        result = build_composite_manifest(
            document_id="doc-002",
            org_id="org-001",
            document_title="Multi-image Article",
            text_merkle_root="sha256:" + "a" * 64,
            text_instance_id="urn:uuid:aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            images=[img0, img1],
        )
        assert result.ingredient_count == 2

    def test_ingredient_instance_id_in_manifest(self):
        from app.services.composite_manifest_service import build_composite_manifest

        instance_id = "urn:uuid:99999999-8888-7777-6666-555555555555"
        img = make_ingredient(c2pa_instance_id=instance_id)
        result = build_composite_manifest(
            document_id="doc-003",
            org_id="org-001",
            document_title="Test",
            text_merkle_root="sha256:" + "b" * 64,
            text_instance_id="urn:uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            images=[img],
        )
        ingredients = result.manifest_data.get("ingredients", [])
        assert len(ingredients) == 1
        assert ingredients[0]["instanceId"] == instance_id

    def test_ingredient_hash_in_manifest(self):
        from app.services.composite_manifest_service import build_composite_manifest

        signed_hash = "sha256:feedcafebabe000000000000000000000000000000000000000000000000000000"
        img = make_ingredient(signed_hash=signed_hash)
        result = build_composite_manifest(
            document_id="doc-004",
            org_id="org-001",
            document_title="Test",
            text_merkle_root="sha256:" + "c" * 64,
            text_instance_id="urn:uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            images=[img],
        )
        ingredients = result.manifest_data.get("ingredients", [])
        assert ingredients[0]["hash"] == signed_hash

    def test_manifest_hash_is_consistent_with_manifest_data(self):
        """manifest_hash must be sha256 of the canonicalized manifest_data JSON."""
        from app.services.composite_manifest_service import build_composite_manifest

        img = make_ingredient(
            image_id="img_fixed000",
            c2pa_instance_id="urn:uuid:f1x-1234-5678-90ab-cdef01234567",
            signed_hash="sha256:" + "e" * 64,
        )
        result = build_composite_manifest(
            document_id="doc-det",
            org_id="org-001",
            document_title="Det",
            text_merkle_root="sha256:" + "f" * 64,
            text_instance_id="urn:uuid:11111111-2222-3333-4444-555555555555",
            images=[img],
        )
        # Verify the hash matches the manifest_data
        manifest_json = json.dumps(result.manifest_data, sort_keys=True, separators=(",", ":"))
        expected_hash = "sha256:" + hashlib.sha256(manifest_json.encode()).hexdigest()
        assert result.manifest_hash == expected_hash

    def test_instance_id_is_valid_urn_uuid(self):
        from app.services.composite_manifest_service import build_composite_manifest

        result = build_composite_manifest(
            document_id="doc-uuid",
            org_id="org-001",
            document_title="UUID Test",
            text_merkle_root="sha256:" + "0" * 64,
            text_instance_id="urn:uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            images=[make_ingredient()],
        )
        assert result.instance_id.startswith("urn:uuid:")
        # Extract UUID part and validate
        uuid_part = result.instance_id[len("urn:uuid:") :]
        parsed = uuid.UUID(uuid_part)
        assert str(parsed) == uuid_part

    def test_manifest_hash_format(self):
        from app.services.composite_manifest_service import build_composite_manifest

        result = build_composite_manifest(
            document_id="doc-hash-fmt",
            org_id="org-001",
            document_title="Hash Format Test",
            text_merkle_root="sha256:" + "a" * 64,
            text_instance_id="urn:uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            images=[make_ingredient()],
        )
        assert result.manifest_hash.startswith("sha256:")
        hash_part = result.manifest_hash[len("sha256:") :]
        assert len(hash_part) == 64
        assert all(c in "0123456789abcdef" for c in hash_part)

    def test_ingredients_sorted_by_position(self):
        from app.services.composite_manifest_service import build_composite_manifest

        img0 = make_ingredient(
            position=0, image_id="img_00000001", filename="first.jpg", c2pa_instance_id="urn:uuid:11111111-0000-0000-0000-000000000001"
        )
        img1 = make_ingredient(
            position=1, image_id="img_00000002", filename="second.jpg", c2pa_instance_id="urn:uuid:11111111-0000-0000-0000-000000000002"
        )
        # Pass in reverse order
        result = build_composite_manifest(
            document_id="doc-sort",
            org_id="org-001",
            document_title="Sort Test",
            text_merkle_root="sha256:" + "b" * 64,
            text_instance_id="urn:uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            images=[img1, img0],
        )
        ingredients = result.manifest_data["ingredients"]
        # Should be sorted by position
        assert ingredients[0]["title"] == "first.jpg"
        assert ingredients[1]["title"] == "second.jpg"

    def test_manifest_data_has_required_keys(self):
        from app.services.composite_manifest_service import build_composite_manifest

        result = build_composite_manifest(
            document_id="doc-keys",
            org_id="org-001",
            document_title="Key Test",
            text_merkle_root="sha256:" + "c" * 64,
            text_instance_id="urn:uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            images=[make_ingredient()],
        )
        data = result.manifest_data
        assert "claim_generator" in data
        assert "instance_id" in data
        assert "assertions" in data
        assert "ingredients" in data

    def test_empty_images_list(self):
        from app.services.composite_manifest_service import build_composite_manifest

        result = build_composite_manifest(
            document_id="doc-empty",
            org_id="org-001",
            document_title="Empty",
            text_merkle_root="sha256:" + "d" * 64,
            text_instance_id="urn:uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            images=[],
        )
        assert result.ingredient_count == 0
        assert result.manifest_data["ingredients"] == []
