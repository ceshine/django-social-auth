"""
Linkedin OAuth support

"""
from django.conf import settings
from django.utils import simplejson

from social_auth.backends import ConsumerBasedOAuth, OAuthBackend, USERNAME

# Weibo OAuth base configuration
WEIBO_OAUTH_HOST = 'api.t.sina.com.cn'
WEIBO_OAUTH_ROOT = 'oauth'
#Always use secure connection
WEIBO_OAUTH_REQUEST_TOKEN_URL = 'http://%s/%s/request_token' % (WEIBO_OAUTH_HOST, WEIBO_OAUTH_ROOT)
WEIBO_OAUTH_AUTHORIZATION_URL = 'http://%s/%s/authorize' % (WEIBO_OAUTH_HOST, WEIBO_OAUTH_ROOT)
WEIBO_OAUTH_ACCESS_TOKEN_URL = 'http://%s/%s/access_token' % (WEIBO_OAUTH_HOST, WEIBO_OAUTH_ROOT)

WEIBO_CHECK_AUTH = 'http://%s/account/verify_credentials.json' % WEIBO_OAUTH_HOST

class WeiboBackend(OAuthBackend):
    """Weibo OAuth authentication backend"""
    name = 'weibo'
    
    EXTRA_DATA = [('profile_image_url','avatar_url'), ('id','id')]
    
    def get_user_details(self, response):
        """Return user details from Weibo account"""
        username = response['screen_name']
        return {USERNAME: 'w' + str(response.get('id')),
                'email': '',  # not supplied
                'fullname': username,
                'first_name': '',
                'last_name': username}
        
class WeiboAuth(ConsumerBasedOAuth):
    """Weibo OAuth authentication mechanism"""
    AUTHORIZATION_URL = WEIBO_OAUTH_AUTHORIZATION_URL
    REQUEST_TOKEN_URL = WEIBO_OAUTH_REQUEST_TOKEN_URL
    ACCESS_TOKEN_URL = WEIBO_OAUTH_ACCESS_TOKEN_URL
    SERVER_URL = WEIBO_OAUTH_HOST
    AUTH_BACKEND = WeiboBackend
    SETTINGS_KEY_NAME = 'WEIBO_CONSUMER_KEY'
    SETTINGS_SECRET_NAME = 'WEIBO_CONSUMER_SECRET'
    
    def user_data(self, access_token):
        """Return user data provided"""
        request = self.oauth_request(access_token, WEIBO_CHECK_AUTH)
        json = self.fetch_response(request)
        try:
            return simplejson.loads(json)
        except ValueError:
            return None
        
    @classmethod
    def enabled(cls):
        """Return backend enabled status by checking basic settings"""
        return all(hasattr(settings, name) for name in
                        ('WEIBO_CONSUMER_KEY',
                         'WEIBO_CONSUMER_SECRET'))
# Backend definition
BACKENDS = {
    'weibo': WeiboAuth,
}
