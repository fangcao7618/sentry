from __future__ import absolute_import

import six

from sentry.models import Event
from sentry.utils.http import absolute_uri
from sentry.utils.safe import safe_execute

from .exceptions import ApiHostError, ApiError, ApiUnauthorized, UnsupportedResponseType

ERR_INTERNAL = (
    'An internal error occurred with the integration and the Sentry team has'
    ' been notified'
)

ERR_UNAUTHORIZED = (
    'Unauthorized: either your access token was invalid or you do not have'
    ' access'
)

ERR_UNSUPPORTED_RESPONSE_TYPE = (
    'An unsupported response type was returned: {content_type}'
)


class IssueSyncMixin(object):
    def get_group_title(self, group, event, **kwargs):
        return event.error()

    def get_group_body(self, group, event, **kwargs):
        result = []
        for interface in six.itervalues(event.interfaces):
            output = safe_execute(interface.to_string, event, _with_transaction=False)
            if output:
                result.append(output)
        return '\n\n'.join(result)

    def get_group_description(self, group, event, **kwargs):
        output = [
            absolute_uri(group.get_absolute_url()),
        ]
        body = self.get_group_body(group, event)
        if body:
            output.extend([
                '',
                '```',
                body,
                '```',
            ])
        return '\n'.join(output)

    def get_create_issue_config(self, group, **kwargs):
        event = group.get_latest_event()
        if event is not None:
            Event.objects.bind_nodes([event], 'data')

        return [
            {
                'name': 'title',
                'label': 'Title',
                'default': self.get_group_title(group, event, **kwargs),
                'type': 'string',
            }, {
                'name': 'description',
                'label': 'Description',
                'default': self.get_group_description(group, event, **kwargs),
                'type': 'textarea',
            }
        ]

    def message_from_error(self, exc):
        if isinstance(exc, ApiUnauthorized):
            return ERR_UNAUTHORIZED
        elif isinstance(exc, ApiHostError):
            return exc.text
        elif isinstance(exc, UnsupportedResponseType):
            return ERR_UNSUPPORTED_RESPONSE_TYPE.format(
                content_type=exc.content_type,
            )
        elif isinstance(exc, ApiError):
            if exc.json:
                msg = self.error_message_from_json(exc.json) or 'unknown error'
            else:
                msg = 'unknown error'
            return (
                'Error Communicating with %s (HTTP %s): %s' % (
                    self.title,
                    exc.code,
                    msg
                )
            )
        else:
            return ERR_INTERNAL

    def create_issue(self, data, **kwargs):
        """
        Create an issue via the provider's API and return the issue key,
        title and description.

        Should also handle API client exceptions and reraise as an
        IntegrationError (using the `message_from_error` helper).

        >>> def create_issue(self, data, **kwargs):
        >>>     resp = self.get_client().create_issue(data)
        >>>     return {
        >>>         'key': resp['id'],
        >>>         'title': resp['title'],
        >>>         'description': resp['description'],
        >>>     }
        """
        raise NotImplementedError
