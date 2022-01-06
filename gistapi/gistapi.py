# coding=utf-8
"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

import requests, re
from flask import Flask, jsonify, request



# *The* app object
app = Flask(__name__)


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def gists_for_user(username):
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
    gists_url = 'https://api.github.com/users/{username}/gists'.format(
            username=username
        )
    
    try:
        response = requests.get(gists_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return e.response.json()
    # BONUS: What failures could happen?
    # - Network failure can occure from server side.
    # - Usernames may not be found, accordingly I handeld the error for it.
    # BONUS: Paging? How does this work for users with tons of gists?
    # - Paging can help in enhancing the memory while resulting in better performance and faster results to be returned.


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
    # BONUS: Validate the arguments?
    # - I changed it to get arguments for better handeling keys in dict in case of no key provided.
    # - Validation can be done when we add marshmallow library to serialize results.

    username = post_data.get('username')
    pattern = post_data.get('pattern')

    # result = {}
    matches = []
    session = requests.Session()
    gists = gists_for_user(username)
    # BONUS: Handle invalid users?
    if gists and type(gists) is list:
        for gist in gists:
            # REQUIRED: Fetch each gist and check for the pattern
            # BONUS: What about huge gists?
            # BONUS: Can we cache results in a datastore/db?
            for file in gist['files'].values():
                gist_content = session.get(file['raw_url']).text
                if re.search(pattern, gist_content):
                    matches.append('https://gist.github.com/{username}/{gist_id}'.format(
                        username=username,
                        gist_id=gist['id']
                    ))

        return jsonify({
            'username': username,
            'pattern': pattern,
            'matches': matches,
            'status':'success'
        })
    else:
        return jsonify({
            'error': 'not found',
            'message': 'invalid user',
            'status': 'fail'
        })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
