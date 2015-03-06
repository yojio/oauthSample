# -*- coding: utf-8 -*-
#
# twitter
#
CONFIG = {}
CONFIG['twitter'] = {
    'consumer_key': 'XXXXXXXXXXXX',
    'consumer_secret': 'XXXXXXXXXXXX',
    'request_token_url': 'https://api.twitter.com/oauth/request_token',
    'access_token_url': 'https://api.twitter.com/oauth/access_token',
    'auth_url': 'https://api.twitter.com/oauth/authorize',
}

CONFIG['twitterapp'] = {
    'consumer_key': 'XXXXXXXXXXXX',
    'consumer_secret': 'XXXXXXXXXXXX',
    'bearer_token_url': 'https://api.twitter.com/oauth2/token'
}

#
# google
#
CONFIG['google'] = {
    'consumer_key': 'XXXXXXXXXXXX',
    'consumer_secret': 'XXXXXXXXXXXX',
    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
    'token_uri': 'https://accounts.google.com/o/oauth2/token',
    'scope': ['https://www.googleapis.com/auth/plus.login', 'https://www.googleapis.com/auth/userinfo.email'],
}

#
# facebook
#
CONFIG['facebook'] = {
    'consumer_key': 'XXXXXXXXXXXX',
    'consumer_secret': 'XXXXXXXXXXXX',
    'auth_uri': 'https://graph.facebook.com/oauth/authorize',
    'token_uri': 'https://graph.facebook.com/oauth/access_token',
    'scope': ['public_profile', 'email', 'user_friends'],
}

#
# linkedin接続用Config
#
CONFIG['linkedin'] = {
    'consumer_key': 'XXXXXXXXXXXX',
    'consumer_secret': 'XXXXXXXXXXXX',
    'auth_uri': 'https://www.linkedin.com/uas/oauth2/authorization',
    'token_uri': 'https://www.linkedin.com/uas/oauth2/accessToken',
    'scope': ['r_basicprofile', 'r_emailaddress', 'r_network'],
    'state': 'XXXXXXXXXXXX'
}
