from uuid import uuid4

import requests
from isodate import duration_isoformat

from ngsi.models import ApiError


class Client(object):
    def __init__(self, host, port=1026):
        self.host = host
        self.port = port
        self._base_url = \
            'http://' + str(self.host) + ':' + str(self.port) + '/'
        self._headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }
        self._api_url_v1 = self._base_url + 'v1/'

    def version(self):
        """
        Returns context broker version
        """
        response = requests.get(
            self._base_url + 'version',
            headers=self._headers)
        return response.json()['orion']

    def create_context(self, elements):
        return self._update_context(elements, action='APPEND')

    def get_context(self, entities, attributes=None):
        return self._query_context(entities, attributes)

    def update_context(self, elements):
        return self._update_context(elements, action='UPDATE')

    def subscribe_context(self,
                          entities,
                          callback_url,
                          duration,
                          notification_type,
                          attributes=None):
        return self._subscribe_context(
            entities,
            callback_url,
            duration,
            notification_type,
            attributes
        )

    def _update_context(self, elements, action=None):
        data = {}
        data['contextElements'] = elements
        if action:
            data['updateAction'] = action
        return self._call_api(method='post', url='updateContext', json=data)

    def _query_context(self, entities, attributes=None):
        data = {}
        data['entities'] = entities
        if attributes:
            data['attributes'] = attributes
        return self._call_api(method='post', url='queryContext', json=data)

    def _subscribe_context(self,
                          entities,
                          callback_url,
                          duration,
                          notification_conditions,
                          attributes=None):
        data = {}
        data['entities'] = entities
        data['reference'] = callback_url
        data['duration'] = duration_isoformat(duration)
        data['notifyConditions'] = notification_conditions
        if attributes:
            data['attributes'] = attributes
        return self._call_api(method='post', url='subscribeContext', json=data)

    def _call_api(self, method, url, params=None, json=None):
        """
        A simple wrapper around host requests
        """
        response = requests.request(
            method,
            self._api_url_v1+url,
            params=params,
            headers=self._headers,
            json=json
        )
        response.raise_for_status()
        json_response = response.json()
        if 'contextResponses' in json_response:
            return json_response['contextResponses']
        elif 'subscribeResponse' in json_response:
            return json_response['subscribeResponse']
        elif 'errorCode' in json_response:
            error = json_response['errorCode']
            raise ApiError('Error code ' +
                             error['code'] + ': ' +
                             error['reasonPhrase'])
