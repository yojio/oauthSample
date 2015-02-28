# -*- coding:utf-8 -*-
#

import base64
import json
import urllib
import urllib2
from urlparse import parse_qsl

import httplib2
import oauth2client

from apiclient.discovery import build
import cPickle as pickle
import oauth2 as oauth
from oauth2client.client import OAuth2WebServerFlow


# factory
class SocialFactory(object):

    def __init__(self):
        self.google = GoogleUser()
        self.facebook = FacebookUser()
        self.twitter = TwitterUser()

    def get_instance(self, provider_name, config):

        if provider_name == "google":
            self.google.set_config(config)
            return self.google

        elif provider_name == "facebook":
            self.facebook.set_config(config)
            return self.facebook

        elif provider_name == "twitter":
            self.twitter.set_config(config)
            return self.twitter

        else:
            raise Exception("provider not found")


# social interface class
class SocialApi(object) :

    def __init__(self):
        pass

    def set_config(self, config):
        self.config = config


    def authorize(self, handler, callback_url):
        raise NotImplementedError

    def callback(self, handler):
        raise NotImplementedError

    # profile
    def get_profile(self, credentials_str, user_id = 'me'):
        raise NotImplementedError

    # friends
    def get_friends(self, credentials_str, user_id = 'me'):
        raise NotImplementedError

# google
class GoogleUser(SocialApi):

    # authorize
    # return auth_url, flow
    def authorize(self, handler, callback_url):

        flow = OAuth2WebServerFlow(
                                   client_id = self.config.get('consumer_key'),
                                   client_secret = self.config.get('consumer_secret'),
                                   scope = self.config.get('scope')
                                )

        auth_url = flow.step1_get_authorize_url(callback_url)
        handler.session['flow'] = pickle.dumps(flow)

        return auth_url


    # authorize-callback
    # return credentials
    def callback(self, handler):
        flow = pickle.loads(str(handler.session.pop('flow')))
        error = handler.request.get('error')
        if error:
            raise Exception("Failure of authentication:%s" % error)

        # credentials
        return {
                'user_id':"me"
                , 'credentials':flow.step2_exchange(handler.request.get('code')).to_json()
               }

    # api-service
    def __get_service(self, credentials):
        http = credentials.authorize(httplib2.Http())
        return build('plus', 'v1', http = http)


    # profile
    def get_profile(self, credentials_str, user_id = 'me'):
        credentials = oauth2client.client.Credentials.new_from_json(credentials_str)

        profile = self.__get_service(credentials).people().get(userId = user_id).execute()
        image = profile['image']['url'].replace('?sz=50', '')
        return {
                'user_id':profile['id'],
                'name':profile['name']['familyName'] + profile['name']['givenName'],
                # 'image_s':image + '?sz=24',    # 24*24
                # 'image_m':image + '?sz=48',    # 48*48
                # 'image_l':image + '?sz=73'    # 73*73
                'image':image + '?sz=48',    # 48*48
                }

    # friends
    def get_friends(self, credentials_str, user_id = 'me'):
        credentials = oauth2client.client.Credentials.new_from_json(credentials_str)

        friends = self.__get_service(credentials).people().list(userId = user_id, collection = 'visible', maxResults = 100).execute()
        return [item['id'] for item in friends.get('items')]

# facebook
class FacebookUser(SocialApi):

    # authorize
    # return auth_url, flow
    def authorize(self, handler, callback_url):

        data = dict(
                    client_id = self.config.get('consumer_key'),
                    redirect_uri = callback_url
                )

        handler.session['callback_url'] = callback_url
        return self.config.get('auth_uri') + '?' + urllib.urlencode(data)

    # authorize-callback
    # return credentials
    def callback(self, handler):

        callback_url = str(handler.session.pop('callback_url'))

        code = handler.request.get('code')

        data = dict(
                    client_id = self.config.get('consumer_key'),
                    client_secret = self.config.get('consumer_secret'),
                    code = code,
                    redirect_uri = callback_url
                    )

        response = urllib.urlopen(self.config.get('token_uri') + '?' + urllib.urlencode(data))

        ret = dict(parse_qsl(response.read()))
        return {
                'user_id':"me",
                'credentials':json.dumps({
                                         'access_token':ret.get('access_token'),
                                         })
               }

    # api caller
    def __call_api(self, credentials, user_id, query = ""):

        if query:
            query += "&"

        return urllib.urlopen(
            "https://graph.facebook.com/%s?%s%s" % (user_id,
            query , urllib.urlencode(dict(access_token = credentials.get('access_token')))))

    # profile
    def get_profile(self, credentials_str, user_id = "me"):

        credentials = json.loads(credentials_str)

        # profile
        response = self.__call_api(
                                   credentials = credentials
                                   , user_id = user_id
                                   )

        profile = json.load(response)

        # picture
        response = self.__call_api(
                                   credentials = credentials
                                   , user_id = user_id
                                   , query = "fields=picture.width(48).height(48)"
                                   )
        picture = json.load(response)

        return {
                'user_id':profile['id'],
                'name':profile['name'],
                'image':picture['picture']['data']['url'],    # 48*48
                }

    # friends
    def get_friends(self, credentials_str, user_id = "me"):

        credentials = json.loads(credentials_str)

        response = self.__call_api(
                                   credentials = credentials
                                   , user_id = user_id
                                   , query = "fields=friends"
                                   )

        friends = json.load(response)

        return friends.values()

# normal authentication OAuth1.0A
class TwitterUser(SocialApi):

    # authorize
    # return authorize_url,oauth_token,oauth_token_secret
    def authorize(self, handler, callback_url):
        consumer = oauth.Consumer(
                                  key = self.config.get('consumer_key'),
                                  secret = self.config.get('consumer_secret')
                                )

        client = oauth.Client(consumer)

        # reqest_token を取得
        _, content = client.request(self.config.get('request_token_url'), 'POST', body = 'oauth_callback=%s' % callback_url)

        request_token = dict(parse_qsl(content))

        # authorize_url
        authorize_url = "%s?oauth_token=%s" % (self.config.get('auth_url'), request_token['oauth_token'])
        handler.session['token'] = request_token['oauth_token']
        handler.session['token_secret'] = request_token['oauth_token_secret']

        return authorize_url

    # authorize-callback
    # return access_token,access_token_secret
    def callback(self, handler):

        token = str(handler.session.pop('token'))
        token_secret = str(handler.session.pop('token_secret'))

        if not token or not token_secret:
            raise Exception("invalid token")

        consumer = oauth.Consumer(key = self.config.get('consumer_key'), secret = self.config.get('consumer_secret'))
        token = oauth.Token(token, token_secret)
        client = oauth.Client(consumer, token)
        oauth_verifier = handler.request.get('oauth_verifier')
        _, content = client.request(self.config.get('access_token_url'), 'POST', body = 'oauth_verifier=%s' % oauth_verifier)
        access_token = dict(parse_qsl(content))

        return {
                'user_id':access_token['user_id'],
                'credentials':json.dumps({
                                         'access_token':access_token['oauth_token'],
                                         'access_token_secret':access_token['oauth_token_secret'],
                                         })
                }

    # Profile
    def get_profile(self, credentials_str, user_id = 'me'):

        credentials = json.loads(credentials_str)

        response = self.__call_user_api(credentials, "users/show.json?user_id=%s" % user_id)
        profile = json.loads(response[1])
        return {
                'user_id':profile['id'],
                'name':profile['name'],
                # 'image_s':profile['profile_image_url'].replace('_normal.', '_mini.'),    # 24*24
                # 'image_m':profile['profile_image_url'],    # 48*48
                # 'image_l':profile['profile_image_url'].replace('_normal.', '_bigger.')    # 73*73
                'image':profile['profile_image_url'],    # 48*48
                }

    # friendlist
    def get_friends(self, credential_str, user_id = 'me'):

        credentials = json.loads(credential_str)

        response = self.__call_user_api(credentials, "friends/ids.json")
        friends = json.loads(response[1])
        return friends['ids']

    # twitter-api-caller
    def __call_user_api(self, credentials, query):

        url = "https://api.twitter.com/1.1/%s" % query

        client = oauth.Client(
                              oauth.Consumer(
                                             key = self.config.get('consumer_key'),
                                             secret = self.config.get('consumer_secret')
                                            ),
                              oauth.Token(
                                        credentials.get('access_token')
                                        , credentials.get('access_token_secret')
                                        )
                              )

        response = client.request(url, 'GET')

        if response[0]['status'] != "200":
            raise Exception("An error has occurred in the Twitter api")

        return response

# Application-only authentication OAuth2.0
# http://ktkrhr.hatenablog.com/entry/2013/03/27/002447
class TwitterApp(object) :

    def __init__(self, config) :
        self.config = config

    # authorize
    # return access_token
    def authorize(self):

            credential = base64.b64encode("%s:%s" %
                                          (
                                           urllib2.quote(self.config.get('consumer_key')),
                                           urllib2.quote(self.config.get('consumer_secret'))
                                          )
                                        )

            data = urllib.urlencode(
                             {
                              'grant_type': 'client_credentials'
                             }
                            )

            req = urllib2.Request(self.config.get('bearer_token_url'))
            req.add_header('Authorization', 'Basic %s' % credential)
            req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')

            response = urllib2.urlopen(req, data)

            # TODO error case
            if response.code != 200:
                raise Exception("authorize error:%d" % response.code)

            json_response = json.loads(response.read())

            return json_response['access_token']

    # search friends
    def search_friends(self, access_token, user_id = None, screen_name = None):

        url = "https://api.twitter.com/1.1/friends/ids.json"

        if user_id:
            query = {'user_id': user_id}
        elif screen_name:
            query = {'screen_name': screen_name}
        else:
            raise Exception("Please specify the user_id or screen_name.")

        req = urllib2.Request(url + '?' + urllib.urlencode(query))
        req.add_header('Authorization', 'bearer ' + access_token)

        response = urllib2.urlopen(req)
        json_response = json.loads(response.read())
        return json_response['ids']



