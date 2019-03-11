# -*- coding: utf-8 -*-

# Build-in Modules
import base64
import hashlib
import hmac
import time
import random
import urllib

# 3rd-part Modules
import requests

# Project Modules
from . import parse_response, ensure_str

PRODUCT_API_CONFIG_MAP = {
    'cvm': {
        'domain'  : 'cvm.tencentcloudapi.com',
        'version' : '2017-03-12',
        'port'    : 443,
        'protocol': 'https'
    },
    'bm': {
        'domain'  : 'bm.tencentcloudapi.com',
        'version' : '2018-04-23',
        'port'    : 443,
        'protocol': 'https'
    },
    'cbs': {
        'domain'  : 'cbs.tencentcloudapi.com',
        'version' : '2017-03-12',
        'port'    : 443,
        'protocol': 'https'
    },
    'tke': {
        'domain'  : 'tke.tencentcloudapi.com',
        'version' : '2018-05-25',
        'port'    : 443,
        'protocol': 'https'
    },
    'cis': {
        'domain'  : 'cis.tencentcloudapi.com',
        'version' : '2018-04-08',
        'port'    : 443,
        'protocol': 'https'
    },
    'as': {
        'domain'  : 'as.tencentcloudapi.com',
        'version' : '2018-04-19',
        'port'    : 443,
        'protocol': 'https'
    },
    'clb': {
        'domain'  : 'clb.tencentcloudapi.com',
        'version' : '2018-03-17',
        'port'    : 443,
        'protocol': 'https'
    },
    'vpc': {
        'domain'  : 'vpc.tencentcloudapi.com',
        'version' : '2017-03-12',
        'port'    : 443,
        'protocol': 'https'
    },
    'cdb': {
        'domain'  : 'cdb.tencentcloudapi.com',
        'version' : '2017-03-20',
        'port'    : 443,
        'protocol': 'https'
    },
    'redis': {
        'domain'  : 'redis.tencentcloudapi.com',
        'version' : '2018-04-12',
        'port'    : 443,
        'protocol': 'https'
    },
    'mongodb': {
        'domain'  : 'mongodb.tencentcloudapi.com',
        'version' : '2018-04-08',
        'port'    : 443,
        'protocol': 'https'
    },
    'mariadb': {
        'domain'  : 'mariadb.tencentcloudapi.com',
        'version' : '2017-03-12',
        'port'    : 443,
        'protocol': 'https'
    },
    'dcdb': {
        'domain'  : 'dcdb.tencentcloudapi.com',
        'version' : '2018-04-11',
        'port'    : 443,
        'protocol': 'https'
    },
    'sqlserver': {
        'domain'  : 'sqlserver.tencentcloudapi.com',
        'version' : '2018-03-28',
        'port'    : 443,
        'protocol': 'https'
    },
    'postgres': {
        'domain'  : 'postgres.tencentcloudapi.com',
        'version' : '2017-03-12',
        'port'    : 443,
        'protocol': 'https'
    },
    'cdn': {
        'domain'  : 'cdn.tencentcloudapi.com',
        'version' : '2018-06-06',
        'port'    : 443,
        'protocol': 'https'
    },
    'yunjing': {
        'domain'  : 'yunjing.tencentcloudapi.com',
        'version' : '2018-02-28',
        'port'    : 443,
        'protocol': 'https'
    },
    'cws': {
        'domain'  : 'cws.tencentcloudapi.com',
        'version' : '2018-03-12',
        'port'    : 443,
        'protocol': 'https'
    },
    'ms': {
        'domain'  : 'ms.tencentcloudapi.com',
        'version' : '2018-04-08',
        'port'    : 443,
        'protocol': 'https'
    },
    'monitor': {
        'domain'  : 'monitor.tencentcloudapi.com',
        'version' : '2018-07-24',
        'port'    : 443,
        'protocol': 'https'
    },
}

def percent_encode(s):
    # I fell sick...
    if isinstance(s, unicode):
        s = s.encode('utf8')
    else:
        s = str(s).decode('utf8').encode('utf8')

    encoded = urllib.quote(s, '')
    encoded = encoded.replace('+', '%20')
    encoded = encoded.replace('*', '%2A')
    encoded = encoded.replace('%7E', '~')

    return encoded

class QCloudCommon(object):
    '''
    QCloud common HTTP API
    '''
    def __init__(self, secret_id=None, secret_key=None, *args, **kwargs):
        self.secret_id  = ensure_str(secret_id)
        self.secret_key = ensure_str(secret_key)

    def sign(self, domain, params_to_sign):
        canonicalized_query_string = ''

        sorted_params = sorted(params_to_sign.items(), key=lambda kv_pair: kv_pair[0])
        for k, v in sorted_params:
            canonicalized_query_string += str(k) + '=' + percent_encode(v) + '&'

        canonicalized_query_string = canonicalized_query_string[:-1]

        string_to_sign = 'POST' + domain + '/?' + canonicalized_query_string

        h = hmac.new(self.secret_key, string_to_sign, hashlib.sha1)
        signature = base64.encodestring(h.digest()).strip()

        return signature

    def verify(self):
        status_code, _ = self.cvm(Action='DescribeRegions')
        return (status_code == 200)

    def call(self, domain, version, port=80, protocol='http', timeout=3, **biz_params):
        api_params = {
            'Timestamp'      : int(time.time()),
            'Nonce'          : random.randint(1, 2 **32),
            'SecretId'       : self.secret_id,
            'Version'        : version,
            'SignatureMethod': 'HmacSHA1',
        }

        api_params.update(biz_params)
        api_params['Signature'] = self.sign(domain, api_params)

        url = '{}://{}:{}/'.format(protocol, domain, port)

        resp = requests.post(url, data=api_params, timeout=timeout)
        parsed_resp = parse_response(resp)

        return resp.status_code, parsed_resp

    def __getattr__(self, product):
        api_config = PRODUCT_API_CONFIG_MAP.get(product)

        if not api_config:
            raise Exception('Unknow QCloud product API config. Please use `call()` with full API configs.')

        domain   = api_config.get('domain')
        version  = api_config.get('version')
        port     = api_config.get('port')
        protocol = api_config.get('protocol')

        def f(timeout=3, **biz_params):
            return self.call(domain=domain, version=version, port=port, protocol=protocol, timeout=timeout, **biz_params)

        return f
