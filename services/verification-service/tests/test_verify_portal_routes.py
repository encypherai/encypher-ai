import pytest


@pytest.mark.parametrize("path", ["/doc_does_not_exist", "/demo/doc_does_not_exist"])
def test_verify_portal_routes_return_html_404(client, mock_db, path: str) -> None:
    mock_result = mock_db.execute.return_value
    mock_result.fetchone.return_value = None

    response = client.get(path)

    assert response.status_code == 404
    assert "text/html" in response.headers["content-type"]
    assert "Document Not Found" in response.text
    assert "Demo Organization Note" in response.text
