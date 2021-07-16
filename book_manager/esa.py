import re
import requests
from requests.auth import AuthBase
import json

from django.conf import settings

ESA_TOKEN = settings.ESA_TOKEN
ESA_TEAMNAME = settings.ESA_TEAMNAME


class APIError(Exception):
    """An API Error Exception"""
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)


# esa API の認証を行うClassを作成 (AuthBaseを継承)
class AuthEsa(AuthBase):
    def __init__(self, token):
        self.token = token

    # リクエストヘッダーのAuthorizationパラメタにTOKENを追記
    # Ex.) Authorization: Bearer ~~token~~
    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer {}'.format(self.token)
        return r


# 初期化でリクエストの構築、MethodでAPIメソッドを指定してクエリを行うことができるClassを柵瀬
class QueryEsa:
    def __init__(self):
        self.session = requests.session()
        self.session.auth = AuthEsa(ESA_TOKEN)
        self.session.headers['Content-Type'] = 'application/json'
        self.ENDPOINT = f'https://api.esa.io/v1/teams/{ESA_TEAMNAME}/'

    # 新規投稿
    def post(self, book, summary):
        try:
            body = dict(post=dict(name=summary.title,
                                  body_md=summary.summary,
                                  category=f"Book/{book.category}/{book.name}",
                                  wip=False))
            res = self.session.post(self.ENDPOINT + "/posts",
                                    data=json.dumps(body).encode('utf-8'))
            if re.match(r'[^2]', str(res.status_code)):
                raise APIError(res.status_code)
            return res
        except APIError as e:
            return e.__str__()

    # 修正
    def patch(self, book, summary):
        try:
            body = dict(post=dict(name=summary.title,
                                  body_md=summary.summary,
                                  category=f"Book/{book.category}/{book.name}",
                                  wip=False))
            res = self.session.patch(self.ENDPOINT + "/posts/" + str(summary.esa_id),
                                     data=json.dumps(body).encode('utf-8'))
            if re.match(r'[^2]', str(res.status_code)):
                raise APIError(res.status_code)
            return res
        except APIError as e:
            return e.__str__()

    # 削除
    def delete(self, esa_id):
        try:
            res = self.session.delete(self.ENDPOINT + "/posts/" + str(esa_id))
            if re.match(r'[^2]', str(res.status_code)):
                raise APIError(res.status_code)
            return res
        except APIError as e:
            return e.__str__()
