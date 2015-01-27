# -*- coding: utf-8 -*-
__version__ = '0.0.1'
__author__ = 'Ali Yahya'
__email__ = 'alive@athena.ai'


from bottle import hook, redirect, request

class SSLify(object):
  
  def __init__(self, app, permanent=False):
    self.app = app
    self.permanent = permanent

    before_request_decorator = self.app.hook('before_request')
    before_request_decorator(self.https_redirect)


  def https_redirect(self):
    '''Redirect incoming HTTPS requests to HTTPS'''

    if not request.get_header('X-Forwarded-Proto', 'http') == 'https':
      if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301 if self.permanent else 302

      redirect(url, code=code)
