# -*- coding: utf-8 -*-

import json

from qcloud_helper import QCloudHelper

def main():
    # Create client helper
    client_helper = QCloudHelper({
        'akId'    : 'your_ak_id',
        'akSecret': 'your_ak_secret',
    })

    # Get CVM list
    status_code, api_res = client_helper.common('cvm', Action='DescribeInstances', Region='ap-shanghai')
    print json.dumps(api_res, indent=2)

if __name__ == '__main__':
    main()