 #!/usr/bin/env python
# -*- coding: utf-8 -*-

from ssl_helper import SSLAdapter
from urllib import urlencode
import json
import os
import re
import requests
import ssl

AUTH_URL_MLA = 'https://auth.mercadolibre.com.ar' # Argentina 
AUTH_URL_MLB = 'https://auth.mercadolivre.com.br' # Brasil
AUTH_URL_MCO = 'https://auth.mercadolibre.com.co' # Colombia
AUTH_URL_MCR = 'https://auth.mercadolibre.com.cr' # Costa Rica
AUTH_URL_MEC = 'https://auth.mercadolibre.com.ec' # Ecuador
AUTH_URL_MLC = 'https://auth.mercadolibre.cl    ' # Chile
AUTH_URL_MLM = 'https://auth.mercadolibre.com.mx' # Mexico
AUTH_URL_MLU = 'https://auth.mercadolibre.com.uy' # Uruguay
AUTH_URL_MLV = 'https://auth.mercadolibre.com.ve' # Venezuela
AUTH_URL_MPA = 'https://auth.mercadolibre.com.pa' # Panama
AUTH_URL_MPE = 'https://auth.mercadolibre.com.pe' # Peru
AUTH_URL_MPT = 'https://auth.mercadolibre.com.pt' # Prtugal
AUTH_URL_MRD = 'https://auth.mercadolibre.com.do' # Dominicana

OAUTH_URL = '/oauth/token'

SDK_VERSION = 'MELI-PYTHON-SDK-1.0.1'
API_ROOT_URL = 'https://api.mercadolibre.com'

SSL_VERSION = 'PROTOCOL_TLSv1'

class Meli(object):
    def __init__(self, client_id, client_secret, access_token=None, refresh_token=None, auth_url=AUTH_URL_MLA):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = None 
        self.AUTH_URL = auth_url
  
        self._requests = requests.Session()
        try:
            self.SSL_VERSION = SSL_VERSION
            self._requests.mount('https://', SSLAdapter(ssl_version=getattr(ssl, self.SSL_VERSION)))
        except:
            self._requests = requests

        self.API_ROOT_URL = API_ROOT_URL
        self.SDK_VERSION = SDK_VERSION
        self.OAUTH_URL = OAUTH_URL

    #AUTH METHODS
    def auth_url(self, redirect_URI, state=None):
        params = {'client_id':self.client_id,'response_type':'code','redirect_uri':redirect_URI}
        if state:
            params['state'] = state
        url = self.AUTH_URL  + '/authorization' + '?' + urlencode(params)
        return url

    def authorize(self, code, redirect_URI):
        params = { 'grant_type' : 'authorization_code', 'client_id' : self.client_id, 'client_secret' : self.client_secret, 'code' : code, 'redirect_uri' : redirect_URI}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        uri = self.make_path(self.OAUTH_URL)

        response = self._requests.post(uri, params=urlencode(params), headers=headers)

        if response.ok:
            response_info = response.json()
            self.access_token = response_info['access_token']
            self.expires_in = response_info['expires_in']
            if 'refresh_token' in response_info:
                self.refresh_token = response_info['refresh_token']
            else:
                self.refresh_token = '' # offline_access not set up

            return self.access_token
        else:
            # response code isn't a 200; raise an exception
            response.raise_for_status()

    def get_refresh_token(self):
        if self.refresh_token:
            params = {'grant_type' : 'refresh_token', 'client_id' : self.client_id, 'client_secret' : self.client_secret, 'refresh_token' : self.refresh_token}
            headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
            uri = self.make_path(self.OAUTH_URL)

            response = self._requests.post(uri, params=urlencode(params), headers=headers, data=params)

            if response.ok:
                response_info = response.json()
                self.access_token = response_info['access_token']
                self.refresh_token = response_info['refresh_token']
                self.expires_in = response_info['expires_in']
                return self.access_token
            else:
                # response code isn't a 200; raise an exception
                response.raise_for_status()
        else:
            raise Exception, "Offline-Access is not allowed."

    # REQUEST METHODS
    def get(self, path, params=None, extra_headers=None):
        params = params or {}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        response = self._requests.get(uri, params=urlencode(params), headers=headers)
        return response

    def post(self, path, body=None, params=None, extra_headers=None):
        params = params or {}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        if body:
            body = json.dumps(body)

        response = self._requests.post(uri, data=body, params=urlencode(params), headers=headers)
        return response

    def put(self, path, body=None, params=None, extra_headers=None):
        params = params or {}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        if body:
            body = json.dumps(body)

        response = self._requests.put(uri, data=body, params=urlencode(params), headers=headers)
        return response

    def delete(self, path, params=None, extra_headers=None):
        params = params or {}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        response = self._requests.delete(uri, params=params, headers=headers)
        return response

    def options(self, path, params=None, extra_headers=None):
        params = params or {}
        headers = {'Accept': 'application/json', 'User-Agent':self.SDK_VERSION, 'Content-type':'application/json'}
        if extra_headers:
            headers.update(extra_headers)
        uri = self.make_path(path)
        response = self._requests.options(uri, params=urlencode(params), headers=headers)
        return response

    def make_path(self, path, params=None):
        params = params or {}
        # Making Path and add a leading / if not exist
        if not (re.search("^\/", path)):
            path = "/" + path
        path = self.API_ROOT_URL + path
        if params:
            path = path + "?" + urlencode(params)

        return path
