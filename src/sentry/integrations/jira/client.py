from __future__ import absolute_import

import datetime
import jwt
import re
from six.moves.urllib.parse import urlparse

from sentry.integrations.client import ApiClient
from sentry.utils.http import absolute_uri

from .utils import get_query_hash

JIRA_KEY = '%s.jira' % (urlparse(absolute_uri()).hostname, )


class JiraApiClient(ApiClient):
    COMMENT_URL = '/rest/api/2/issue/%s/comment'
    ISSUE_URL = '/rest/api/2/issue/%s'
    SEARCH_URL = '/rest/api/2/search/'

    def __init__(self, base_url, shared_secret):
        self.base_url = base_url
        self.shared_secret = shared_secret
        super(JiraApiClient, self).__init__(verify_ssl=False)

    def request(self, method, path, data=None, params=None, **kwargs):
        jwt_payload = {
            'iss': JIRA_KEY,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=5 * 60),
            'qsh': get_query_hash(path, method.upper(), params),
        }
        encoded_jwt = jwt.encode(jwt_payload, self.shared_secret)
        params = dict(
            jwt=encoded_jwt,
            **(params or {})
        )
        return self._request(method, path, data=data, params=params, **kwargs)

    def get_issue(self, issue_id):
        return self.request('GET', self.ISSUE_URL % (issue_id,))

    def search_issues(self, query):
        # check if it looks like an issue id
        if re.search(r'^[A-Za-z]+-\d+$', query):
            jql = 'id="%s"' % query.replace('"', '\\"')
        else:
            jql = 'text ~ "%s"' % query.replace('"', '\\"')
        return self.request('GET', self.SEARCH_URL, params={'jql': jql})

    def create_comment(self, issue_key, comment):
        return self.request('POST', self.COMMENT_URL % issue_key, data={'body': comment})
