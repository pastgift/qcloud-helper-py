# -*- coding: utf-8 -*-

# Build-in Modules
import time
import json
import uuid

# Project Modules
from qcloud_common import QCloudCommon

def get_config(c):
    return {
        'secret_id' : c.get('akId'),
        'secret_key': c.get('akSecret'),
    }

class QCloudHelper(object):
    def __init__(self, config=None):
        self.config        = config
        self.common_client = QCloudCommon(**get_config(config))

    def verify(self):
        return self.common_client.verify()

    def common(self, product, timeout=3, **biz_params):
        return self.common_client.__getattr__(product)(timeout=timeout, **biz_params)

