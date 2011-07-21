"""
Mixi OAuth 2.0 Support
"""
from urllib import urlencode
from urllib2 import Request, urlopen

from django.conf import settings
from django.utils import simplejson

from social_auth.backends import BaseOAuth2, USERNAME, OAuthBackend

MIXI_OAUTH2_SERVER = 'mixi.jp'
MIXI_OATUH2_AUTHORIZATION_URL = 'https://mixi.jp/connect_authorize.pl'
MIXI_OAUTH2_ACCESS_TOKEN_URL = 'https://secure.mixi-platform.com/2/token'

EXPIRES_NAME = getattr(settings, 'SOCIAL_AUTH_EXPIRATION', 'expires')

MIXI_OAUTH_SCOPE = ['r_profile']
MIXIAPIS_SELF = 'http://api.mixi-platform.com/2/people/@me/@self'

# Backends
class MixiBackend(OAuthBackend):
    """Mixi OAuth 2.0 authentication backend"""
    name = 'mixi-oauth2'
    EXTRA_DATA = [('id','id'), 
                  ('thumbnailUrl','avatar_url'),
                  ('refresh_token', 'refresh_token'),
                  ('expires_in', EXPIRES_NAME)]

    def get_user_details(self, response):
        """Return user details from Orkut account"""
        return {USERNAME: 'm' + str(response.get('id')),
                'email': '',
                'fullname': response.get('displayName', ''),
                'first_name': '',
                'last_name': response.get('displayName', '')}


class MixiOAuth2(BaseOAuth2):
    """Mixi OAuth2 support"""
    AUTH_BACKEND = MixiBackend
    AUTHORIZATION_URL = MIXI_OATUH2_AUTHORIZATION_URL
    ACCESS_TOKEN_URL = MIXI_OAUTH2_ACCESS_TOKEN_URL
    SETTINGS_KEY_NAME = 'MIXI_OAUTH2_CLIENT_KEY'
    SETTINGS_SECRET_NAME = 'MIXI_OAUTH2_CLIENT_SECRET'

    def get_scope(self):
        return MIXI_OAUTH_SCOPE + getattr(settings, 'MIXI_OAUTH_EXTRA_SCOPE', [])

    def user_data(self, access_token):
        """Return user data from Mixi API"""
        data = {'oauth_token': access_token}
        return mixiapis_self(MIXIAPIS_SELF, urlencode(data))

    @classmethod
    def enabled(cls):
        """Return backend enabled status by checking basic settings"""
        return all(hasattr(settings, name) for name in
                        ('MIXI_OAUTH2_CLIENT_KEY',
                            'MIXI_OAUTH2_CLIENT_SECRET'))

def mixiapis_self(url, params):
    """Loads user data from mixiapis service. 
    It's documented at: http://developer.mixi.co.jp/connect/mixi_graph_api/mixi_io_spec_top/people-api/

    Parameters must be passed in queryset and Authorization header as described
    on Mixi OAuth documentation at:
    http://developer.mixi.co.jp/connect/mixi_graph_api/api_auth/ 
    """
    request = Request(url + '?' + params, headers={'Authorization': params})
    try:
        return simplejson.loads(urlopen(request).read())['entry']
    except (ValueError, KeyError, IOError):
        return None


# Backend definition
BACKENDS = {
    'mixi': MixiOAuth2,
}
