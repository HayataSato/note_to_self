import requests
from requests.auth import AuthBase
import json

from django.conf import settings


class AuthEsa(AuthBase):

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer {}'.format(TOKEN)
        return r


# requests instance
session = requests.session()
session.auth = AuthEsa()
session.headers['Content-Type'] = 'application/json'

api_endpoint = 'https://api.esa.io'

settings.ESA_TOKEN