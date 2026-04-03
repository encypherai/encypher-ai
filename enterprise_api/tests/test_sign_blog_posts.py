from __future__ import annotations

from pathlib import Path

import pytest

from scripts.sign_blog_posts import (
    BlogPost,
    apply_embedding_plan,
    build_signed_markdown,
    gather_posts,
    normalize_base_url,
    parse_frontmatter,
    resolve_api_config,
    sign_markdown_text,
)


def test_normalize_base_url_adds_scheme() -> None:
    assert normalize_base_url("api.encypher.com") == "https://api.encypher.com"
    assert normalize_base_url("https://api.encypher.com") == "https://api.encypher.com"


def test_parse_frontmatter_extracts_metadata_and_body() -> None:
    text = """---\ntitle: \"A Post\"\ndate: \"2026-02-10\"\n---\n\nHello world\n"""
    metadata, body, frontmatter = parse_frontmatter(text)

    assert metadata["title"] == "A Post"
    assert metadata["date"] == "2026-02-10"
    assert body.strip() == "Hello world"
    assert frontmatter.startswith("---")


def test_gather_posts_sorts_by_frontmatter_date(tmp_path: Path) -> None:
    older = tmp_path / "older.md"
    newer = tmp_path / "newer.md"

    older.write_text(
        '---\ntitle: "Older"\ndate: "2025-01-01"\n---\n\nOlder body\n',
        encoding="utf-8",
    )
    newer.write_text(
        '---\ntitle: "Newer"\ndate: "2026-01-01"\n---\n\nNewer body\n',
        encoding="utf-8",
    )

    posts = gather_posts([tmp_path])

    assert [post.title for post in posts] == ["Older", "Newer"]


def test_resolve_api_config_reads_requested_env_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENYCPHER_API_KEY", "k_test")
    monkeypatch.setenv("ENCYPHER_BASE_URL", "api.encypher.com")

    api_key, base_url = resolve_api_config(api_key=None, base_url=None, env_file=None)

    assert api_key == "k_test"
    assert base_url == "https://api.encypher.com"


class _DummyResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self) -> dict:
        return self._payload


class _DummyClient:
    def __init__(self, signed_text: str = "signed-output", embedding_plan: dict | None = None) -> None:
        self.calls: list[tuple[str, dict]] = []
        self._signed_text = signed_text
        self._embedding_plan = embedding_plan

    def post(self, path: str, *, headers: dict, json: dict) -> _DummyResponse:  # noqa: A003
        self.calls.append((path, json))
        if path == "/api/v1/sign":
            document: dict = {"signed_text": self._signed_text}
            if self._embedding_plan is not None:
                document["embedding_plan"] = self._embedding_plan
            return _DummyResponse(
                201,
                {
                    "success": True,
                    "data": {"document": document},
                },
            )
        return _DummyResponse(200, {"data": {"valid": True}})


def test_apply_embedding_plan_reconstructs_signed_text() -> None:
    visible = "abc"
    plan = {
        "index_unit": "codepoint",
        "operations": [
            {"insert_after_index": -1, "marker": "X"},
            {"insert_after_index": 1, "marker": "Y"},
        ],
    }

    reconstructed = apply_embedding_plan(visible, plan)
    assert reconstructed == "XabYc"


def test_sign_markdown_text_uses_micro_ecc_and_c2pa_defaults() -> None:
    client = _DummyClient(signed_text="hello")
    post = BlogPost(
        path=Path("/tmp/a.md"),
        title="A",
        date="2026-02-10",
        metadata={"title": "A", "date": "2026-02-10"},
        body="hello",
        frontmatter='---\ntitle: "A"\ndate: "2026-02-10"\n---\n\n',
    )

    signed_text = sign_markdown_text(
        post=post,
        api_key="k_test",
        base_url="https://api.encypher.com",
        client=client,
    )

    assert "hello" in signed_text
    sign_payload = client.calls[0][1]
    assert sign_payload["options"]["manifest_mode"] == "micro"
    assert sign_payload["options"]["ecc"] is True
    assert sign_payload["options"]["embed_c2pa"] is False
    assert sign_payload["options"]["return_embedding_plan"] is True


def test_sign_markdown_text_uses_embedding_plan_when_present() -> None:
    plan = {
        "index_unit": "codepoint",
        "operations": [
            {"insert_after_index": -1, "marker": "X"},
            {"insert_after_index": 1, "marker": "Y"},
        ],
    }
    client = _DummyClient(signed_text="XabYc", embedding_plan=plan)
    post = BlogPost(
        path=Path("/tmp/a.md"),
        title="A",
        date="2026-02-10",
        metadata={"title": "A", "date": "2026-02-10"},
        body="abc",
        frontmatter="",
    )

    merged_text = sign_markdown_text(
        post=post,
        api_key="k_test",
        base_url="https://api.encypher.com",
        client=client,
    )

    assert merged_text == "XabYc"


def test_sign_markdown_text_preserves_markdown_formatting() -> None:
    signed_text = "This is *test* and **test1**.\n\n- list item\n"
    client = _DummyClient(signed_text=signed_text)
    post = BlogPost(
        path=Path("/tmp/a.md"),
        title="A",
        date="2026-02-10",
        metadata={"title": "A", "date": "2026-02-10"},
        body="This is *test* and **test1**.\n\n- list item\n",
        frontmatter='---\ntitle: "A"\ndate: "2026-02-10"\n---\n\n',
    )

    merged_text = sign_markdown_text(
        post=post,
        api_key="k_test",
        base_url="https://api.encypher.com",
        client=client,
    )

    assert "*test*" in merged_text
    assert "**test1**" in merged_text
    assert "\n\n- list item" in merged_text


def test_sign_markdown_text_strips_existing_markers_before_signing() -> None:
    from app.utils.vs256_crypto import VS_CHAR_SET

    marker = next(iter(VS_CHAR_SET))
    client = _DummyClient(signed_text="Hello world")
    post = BlogPost(
        path=Path("/tmp/a.md"),
        title="A",
        date="2026-02-10",
        metadata={"title": "A", "date": "2026-02-10"},
        body=f"Hello{marker} world",
        frontmatter="",
    )

    sign_markdown_text(
        post=post,
        api_key="k_test",
        base_url="https://api.encypher.com",
        client=client,
    )

    sign_payload = client.calls[0][1]
    assert sign_payload["text"] == "Hello world"


def test_build_signed_markdown_preserves_frontmatter_and_replaces_body() -> None:
    post = BlogPost(
        path=Path("/tmp/a.md"),
        title="A",
        date="2026-02-10",
        metadata={"title": "A", "date": "2026-02-10"},
        body="original",
        frontmatter='---\ntitle: "A"\ndate: "2026-02-10"\n---\n\n',
    )

    merged = build_signed_markdown(post, "signed-body")

    assert merged.startswith(post.frontmatter)
    assert merged.endswith("signed-body")
