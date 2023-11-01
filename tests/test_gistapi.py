import json
import os
import sys

import pytest

# append directory one level up to allow the main module import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import gistapi


def test_get_gist_raw_file_urls():
    test_gist = dict(
        id="test-gist",
        files={"file1.py": "url_to_file1.py", "file2.py": "url_to_file2.py"},
    )
    expected = [
        "https://gist.githubusercontent.com/username/test-gist/raw/file1.py",
        "https://gist.githubusercontent.com/username/test-gist/raw/file2.py",
    ]
    result = gistapi.get_gist_raw_file_urls(test_gist, "username")
    assert result == expected


def test_get_gist_raw_file_urls_without_files():
    test_gist = dict(id="test-gist")
    expected = []
    result = gistapi.get_gist_raw_file_urls(test_gist, "username")
    assert result == expected


def test_has_pattern():
    assert gistapi.has_pattern("this is a test string inside a gist file", "inside")


def test_has_not_pattern():
    assert not gistapi.has_pattern(
        "this is a test string inside a gist file", "not inside"
    )


class TestGetFileResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        pass


def test_get_raw_file_content(mocker):
    mocker.patch(
        "gistapi.requests.get",
        return_value=TestGetFileResponse(text="content", status_code=200),
    )
    mock_response = gistapi.get_raw_file_content("anyurl")
    assert mock_response == "content"


def test_get_raw_file_content_with_status_code_not_200(mocker):
    mocker.patch(
        "gistapi.requests.get",
        return_value=TestGetFileResponse(text=None, status_code=404),
    )
    assert gistapi.get_raw_file_content("anyurl") is None


class TestPaginationWithMaxGists:
    def json(self):
        return [dict(id="test-gist-{n}".format(n=n)) for n in range(100)]

    def raise_for_status(self):
        pass


class TestPaginationEmpty:
    def json(self):
        return []

    def raise_for_status(self):
        pass


def test_paginated_gists_for_user_with_one_full_page(mocker):
    mocker.patch("gistapi.requests.get", side_effect=[TestPaginationEmpty()])
    result = list(gistapi.paginated_gists_for_user("username"))
    assert len(result) == 0


def test_paginated_gists_for_user_with_max_gists(mocker):
    """Stops at the third iteration because of the max gists limit i.e. 3000"""
    mocker.patch(
        "gistapi.requests.get", side_effect=[TestPaginationWithMaxGists()] * 31
    )
    result = list(gistapi.paginated_gists_for_user("username"))
    assert len(result) == 30


@pytest.fixture
def client():
    yield gistapi.app.test_client()


def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.data == b"pong"


@pytest.mark.ftest
def test_search_with_testing_gist(client, mocker):
    headers = {"content-type": "application/json"}
    form = dict(username="panc86", pattern="foo")
    response = client.post("/api/v1/search", data=json.dumps(form), headers=headers)
    result = response.json
    assert result["status"] == "success" and len(result["matches"]) == 2
