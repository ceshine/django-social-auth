from django.conf import settings

from social_auth.tests.base import SocialAuthTestsCase, FormParserByName, \
                                   RefreshParser
                                   
class WeiboTestCase(SocialAuthTestsCase):
    def setUp(self, *args, **kwargs):
        super(WeiboTestCase, self).setUp(*args, **kwargs)
        self.user = getattr(settings, 'TEST_WEIBO_USER', None)
        self.passwd = getattr(settings, 'TEST_WEIBO_PASSWORD', None)
        # check that user and password are setup properly
        self.assertTrue(self.user)
        self.assertTrue(self.passwd)
        

class WeiboTestLogin(WeiboTestCase):
    def test_login_succeful(self):
        response = self.client.get(self.reverse('begin', 'weibo'))
        
        # social_auth must redirect to service page
        self.assertEqual(response.status_code, 302)
        #print response
        # Open first redirect page, it contains user login form because
        # we don't have cookie to send to weibo
        login_content = self.get_content(response['Location'])
        parser = FormParserByName('authZForm')
        parser.feed(login_content)
        auth = {'userId': self.user,
                'passwd': self.passwd,
        #        'oauth_callback': 'http://127.0.0.1:8000/complete/weibo/'
                 }
        
        # Check that action and values were loaded properly
        self.assertTrue(parser.action)
        self.assertTrue(parser.values)
        
        # Post login form, will return authorization or redirect page
        parser.values.update(auth)
        #print parser.values
        result = self.get_redirect("http://api.t.sina.com.cn/oauth/"+parser.action, data=parser.values, use_cookies=True)
        response = self.client.get(self.make_relative(result.headers.get('Location')), use_cookies=True)

        self.assertEqual(response.status_code, 302)
        
        location = self.make_relative(response['Location'])
        login_redirect = getattr(settings, 'LOGIN_REDIRECT_URL', '')
        self.assertTrue(location == login_redirect)