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

# template url to retrieve latest content of raw files in gist
GIST_LATEST_RAW_FILE_URL = "https://gist.githubusercontent.com/{gist_username}/{gist_id}/raw/{filename}"

app = Flask(__name__)


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def gists_for_user(username: str):
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
    gists_url = 'https://api.github.com/users/{username}/gists'.format(username=username)
    response = requests.get(gists_url)
    return response.json()


@app.route("/api/v1/search", methods=['POST'])
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

    username = post_data['username']
    pattern = post_data['pattern']

    # compile pattern for performance
    regex = re.compile(pattern, flags=re.IGNORECASE|re.MULTILINE)

    result = {}
    result['status'] = 'success'
    result['username'] = username
    result['pattern'] = pattern
    result['matches'] = []

    gists = gists_for_user(username)

    for gist in gists:
        gist_id = gist["id"]
        gist_html_url = gist["html_url"]
        filenames = list(gist.get("files"))
        if not filenames:
            continue
        for filename in filenames:
            raw_url = GIST_LATEST_RAW_FILE_URL.format(gist_username=username, gist_id=gist_id, filename=filename)
            raw_file = requests.get(raw_url)
            if regex.search(raw_file.text):
                result["matches"].append(raw_url)

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9876)
