# -*- coding:utf-8 -*-
# main.py

import json
import time

from google.appengine.ext.ndb.model import delete_multi
import webapp2
from webapp2_extras import sessions

from config import CONFIG
import models
import social


twitter_app = social.TwitterApp(CONFIG['twitterapp'])
social_factory = social.SocialFactory()

class Login(webapp2.RequestHandler):

    def dispatch(self):
        self.session_store = sessions.get_store(request = self.request)

        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()

    def login(self, provider_name):

        if provider_name == "twitterapp":
            access_token = twitter_app.authorize()
            common = models.Common.query().get()
            if not common:
                common = models.Common()

            common.credentials_twitter = json.dumps({
                             'access_token':access_token
                            })
            common.put()

            self.session['access_token'] = access_token
            redirect_url = "/"

        else:
            auth_api = social_factory.get_instance(provider_name, CONFIG[provider_name])
            redirect_url = auth_api.authorize(self, self.request.host_url + "/callback/%s" % provider_name)

        self.redirect(redirect_url)

    def callback(self, provider_name):

        auth_api = social_factory.get_instance(provider_name, CONFIG[provider_name])
        ret = auth_api.callback(self)

        delete_multi(models.User.query().fetch(keys_only = True))

        user = models.User()
        user.user_id = ret.get("user_id")
        user.provider_name = provider_name
        user.credentials = ret.get("credentials")
        user.put()

        self.redirect('/')


    def friends(self, provider_name):

        if provider_name == "twitterapp":
            common = models.Common.query().get()
            if not common:
                self.response.write("Application authentication does not end. (Please go back)")
                return

            credentials = json.loads(common.credentials_twitter)
            token = credentials.get("access_token")
            data = twitter_app.search_friends(token, screen_name = "twitterjp")

        else:

            user = models.User.query(models.User.provider_name == provider_name).get()
            if not user:
                self.response.write("Does not end user authentication. (Please go back)")
                return

            auth_api = social_factory.get_instance(provider_name, CONFIG[provider_name])
            data = auth_api.get_friends(user.credentials, user.user_id)

        self.response.write(u"FriendList：" + "</br>")
        for item in data:
            self.response.write(str(item) + "</br>")

    def profile(self, provider_name):

        user = models.User.query(models.User.provider_name == provider_name).get()
        if not user:
            self.response.write("Does not end user authentication. (Please go back)")
            return

        auth_api = social_factory.get_instance(provider_name, CONFIG[provider_name])
        data = auth_api.get_profile(user.credentials, user.user_id)

        self.response.write(u"Profile：" + "</br>")
        self.response.write("&nbsp" + "user_id:" + str(data["user_id"]) + "</br>")
        self.response.write("&nbsp" + "name:" + data["name"].encode('utf-8') + "</br>")
        self.response.write("&nbsp" + "image:" + data["image"].encode('utf-8') + "</br>")

    def delete(self, typename):

        if typename == "common":
            delete_multi(models.Common.query().fetch(keys_only = True))
        else:
            delete_multi(models.User.query().fetch(keys_only = True))

        self.redirect("/")

# Create a home request handler just that you don't have to enter the urls manually.
class Home(webapp2.RequestHandler):
    def get(self):

        time.sleep(0.1)
        self.response.write('<header>')
        self.response.write('<meta http-equiv="Pragma" content="no-cache">')
        self.response.write('<meta http-equiv="Cache-Control" content="no-cache">')
        self.response.write('<meta http-equiv="Expires" content="Thu, 01 Dec 1994 16:00:00 GMT">')
        self.response.write('</header>')
        self.response.write('<body>')

        user = models.User.query().get()
        if user:
            self.response.write('●&nbsp')
            self.response.write(user.provider_name)
            self.response.write('Authenticated<br />')

        common = models.Common.query().get()
        if common:
            self.response.write('●&nbsp')
            self.response.write('Twitter-App Authenticated<br />')

        self.response.write('<br />')

        # Create links to the Login handler.
        self.response.write('Login with <a href="login/twitter">Twitter(User)</a>.<br />')
        if user and user.provider_name == "twitter":
            self.response.write('&nbsp&nbsp-API call <a href="friends/twitter">friend(twitter-User)</a>.<br />')
            self.response.write('&nbsp&nbsp-API call <a href="profile/twitter">profile(twitter-User)</a>.<br />')
        self.response.write('<br />')

        self.response.write('Login with <a href="login/twitterapp">Twitter(Application)</a>.<br />')
        if common :
            self.response.write('&nbsp&nbsp-API call <a href="friends/twitterapp">friend(twitter-Application)</a>.<br />')
        self.response.write('<br />')

        self.response.write('Login with <a href="login/google">Google</a>.<br />')
        if user and user.provider_name == "google":
            self.response.write('&nbsp&nbsp-API call <a href="friends/google">friend(google)</a>.<br />')
            self.response.write('&nbsp&nbsp-API call <a href="profile/google">profile(google)</a>.<br />')
        self.response.write('<br />')

        self.response.write('Login with <a href="login/facebook">Facebook</a>.<br />')
        if user and user.provider_name == "facebook":
            self.response.write('&nbsp&nbsp-API call <a href="friends/facebook">friend(facebook)</a>.<br />')
            self.response.write('&nbsp&nbsp-API call <a href="profile/facebook">profile(facebook)</a>.<br />')

        self.response.write('<br />')
        self.response.write('<br />')
        self.response.write('<a href="delete/common">delete TwitterApp-Credentials</a>.<br />')
        self.response.write('<a href="delete/user">delete user-Credentials</a>.<br />')
        self.response.write('</body>')


# Instantiate the webapp2 WSGI application.
app = webapp2.WSGIApplication([
       webapp2.Route(r'/profile/<:.*>', Login, handler_method = 'profile'),
       webapp2.Route(r'/friends/<:.*>', Login, handler_method = 'friends'),
       webapp2.Route(r'/login/<:.*>', Login, handler_method = 'login'),
       webapp2.Route(r'/callback/<:.*>', Login, handler_method = 'callback'),
       webapp2.Route(r'/delete/<:.*>', Login, handler_method = 'delete'),
       webapp2.Route(r'/', Home)
       ],
       debug = True,
       config = {'webapp2_extras.sessions':{
            'secret_key':'oauthSampleKey',
            'cookie_name':'_oauthSample',
#             'session_max_age':360,
#             'cookie_arg':{
#                 'max_age':None,
#                 'domain':None,
#                 'path':'/',
#                 'secure':None,
#                 'httponly':None,
#             },
#             'default_backend':'securecookie',
}, })
