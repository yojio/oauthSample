from google.appengine.ext import ndb

class User(ndb.Model):

    user_id = ndb.StringProperty()
    provider_name = ndb.StringProperty()
    credentials = ndb.TextProperty()

    def to_dict(self):
        return {
            'key': self.key.urlsafe(),
            'user_id': self.user_id,
        }

class Common(ndb.Model):

    credentials_twitter = ndb.TextProperty()

    def to_dict(self):
        return {
            'key': self.key.urlsafe(),
            'credentials_twitter': self.credentials_twitter,
        }
