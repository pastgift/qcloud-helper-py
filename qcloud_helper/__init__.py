# -*- coding: utf-8 -*-

# Build-in Modules
import json

# 3rd-part Modules
import xmltodict

def parse_response(response):
    resp_content_type = response.headers.get('content-type') or ''
    resp_content_type = resp_content_type.lower().split(';')[0].strip()

    if resp_content_type == 'application/json':
        return response.json()

    elif resp_content_type == 'text/xml':
        return xmltodict.parse(response.text)

    else:
        try:
            return json.loads(response.text)

        except ValueError:
            try:
                return xmltodict.parse(response.text)

            except xmltodict.expat.ExpatError:
                return response.text

            except:
                raise

        except:
            raise

from qcloud_helper  import QCloudHelper
