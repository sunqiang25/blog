from __future__ import unicode_literals

import json

import requests

CLIENT_ID = 'f46b263812019f5ab677'
CLIENT_SECRET = '9e286258324dfae3d43cb4539fbbbd364bfa9497'
CALLBACK = 'http://39.106.189.163/login/callback'


def get_github_auth():
    url = 'https://github.com/login/oauth/authorize?client_id={0}&redirect_uri={1}&scope=user:email'.format(
        CLIENT_ID,
        CALLBACK)
    return url


def get_access_token(code):
    #code = 'ff28289b9bc31a0d618a'
    url = 'https://github.com/login/oauth/access_token'
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': CALLBACK
    }
    res = requests.post(url, data=data, headers={'Accept': 'application/json'})
    access_token = json.loads(res.content).get('access_token')
    return access_token


def get_user_info(access_token):
    url = 'https://api.github.com/user?access_token={0}'.format(access_token)
    res = requests.get(url, headers={'Accept': 'application/json'})
    json_data = json.loads(res.content)
    print json_data
    email = json_data.get('email')
    nick = json_data.get('name')
    gid = json_data.get('id')
    if not nick:
        nick = json_data.get('login', '')
    qiuju = json_data.get('avatar_url')
    return gid, email, nick, qiuju

#print get_access_token('ff28289b9bc31a0d618a')
#print get_user_info('381b77723d6d684c3957b0502ea929535cd64e82')
#print get_github_auth()
