"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

import re
import requests
from flask import Flask, jsonify, request


app = Flask(__name__)


def get_gist_raw_file_urls(gist: dict, username: str) -> list[str]:
    """Get list of URLs of raw files inside a gist or empty list if no files"""
    # template url to retrieve latest content of raw files in gist
    template_url = (
        "https://gist.githubusercontent.com/{gist_username}/{gist_id}/raw/{filename}"
    )
    filenames = list(gist.get("files", []))
    return (
        [
            template_url.format(
                gist_username=username, gist_id=gist["id"], filename=filename
            )
            for filename in filenames
        ]
        if filenames
        else filenames
    )


def get_raw_file_content(raw_url: str) -> str | None:
    """Get file content in gist if status code is 200"""
    response = requests.get(raw_url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        # handle http errors
        print(dict(url=raw_url, error=error))
    return response.text


def has_pattern(file_content: str, pattern: str) -> bool:
    """Search regex pattern in the content of raw file URL"""
    return re.search(pattern, file_content, flags=re.IGNORECASE | re.MULTILINE)


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def gists_for_user(username: str, page: int = 1, per_page: int = 30):
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    Args:
        username (string): the user to query gists for

    Returns:
        The dict parsed from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """
    gists_url = "https://api.github.com/users/{username}/gists".format(
        username=username
    )
    # add parameters for pagination
    params = {
        "page": page,
        "per_page": per_page,
    }
    response = requests.get(gists_url, params=params)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        # handle http errors
        print(dict(url=gists_url, error=error))
    return response.json()


def paginated_gists_for_user(username: str):
    # reference: https://docs.github.com/en/rest/gists/gists?apiVersion=2022-11-28#list-public-gists
    max_gists_per_user = 3000
    page = 1
    per_page = 100
    count = 0
    # using a generator to handle high volume gists
    while True:
        gists = gists_for_user(username, page=page, per_page=per_page)
        if not gists or count >= max_gists_per_user:
            break
        yield gists
        count += len(gists)
        page += 1


@app.route("/api/v1/search", methods=["POST"])
def search():
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    post_data = request.get_json()

    username = post_data["username"]
    pattern = post_data["pattern"]

    result = {}
    result["status"] = "success"
    result["username"] = username
    result["pattern"] = pattern
    result["matches"] = []

    gists = gists_for_user(username)

    for gist in gists:
        raw_file_urls = get_gist_raw_file_urls(gist, username)
        if not raw_file_urls:
            continue

        for raw_url in raw_file_urls:
            content = get_raw_file_content(raw_url)
            if content is not None and has_pattern(content, pattern):
                result["matches"].append(raw_url)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9876)
