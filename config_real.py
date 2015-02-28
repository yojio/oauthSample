# -*- coding: utf-8 -*-
#
# twitter接続用Config
#
# サンプル（コールバック：http://127.0.0.1:8080/callback/twitter）
# permission Read and write
#
CONFIG = {}
CONFIG['twitter'] = {
    'consumer_key': '8ZYWyP3Vyat2hrr62eFasF2X0',
    'consumer_secret': 'STzczOxOKZd1PZ8B18PV7rgLKFPnkKFGYbK8uq5f3SdqOYBuZr',
    'request_token_url': 'https://api.twitter.com/oauth/request_token',
    'access_token_url': 'https://api.twitter.com/oauth/access_token',
    'auth_url': 'https://api.twitter.com/oauth/authorize',
}

CONFIG['twitterapp'] = {
    'consumer_key': 'DaGOg5a1be7DXaLl2OTvA',
    'consumer_secret': 'NrySWKM7VynURNFktn5PsTSEBTyJK0GHzh6YFaryg',
    'bearer_token_url': 'https://api.twitter.com/oauth2/token'    # for Application-only authorize
}

#
# google接続用Config
#
CONFIG['google'] = {
    'consumer_key': '433402205824-vorsnjj2ps6imbb65cfs3pg4lo50u0kr.apps.googleusercontent.com',
    'consumer_secret': 'SJfPzeuUqA1X1DK07e3vFrLn',
    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
    'token_uri': 'https://accounts.google.com/o/oauth2/token',
    'scope': ['https://www.googleapis.com/auth/plus.login', 'https://www.googleapis.com/auth/userinfo.email'],
}

#
# facebook接続用Config
#
CONFIG['facebook'] = {
    'consumer_key': '1539999296255422',
    'consumer_secret': '81fa30be29c484fb9d8a3526185796d7',
    'auth_uri': 'https://graph.facebook.com/oauth/authorize',
    'token_uri': 'https://graph.facebook.com/oauth/access_token',
    'scope': ['public_profile', 'email', 'user_friends'],
}

