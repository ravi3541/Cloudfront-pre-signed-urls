import os
import json
import base64
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from aws_demo.settings import BASE_DIR

class ResponseInfo(object):
    """
    Class for creating standard response format for all API's.
    """
    def __init__(self, **args):
        self.response_format = {
            "status_code": args.get('status', 200),
            "error": args.get('error', None),
            "data": args.get('data', []),
            "message": [args.get('message', 'Success')]
        }


def rsa_signer(message):
    """
    method for signing url with private key.
    """
    private_key_path = os.path.join(BASE_DIR, os.getenv("PRIVATE_KEY_PATH"))
    with open(private_key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())


def make_cloudfront_policy(resource=None, expire_epoch_time=180):
    """
    method to generate custom policy.
    """
    policy = {
        'Statement': [{
            'Resource': resource,
            'Condition': {
                'DateLessThan': {
                    'AWS:EpochTime': expire_epoch_time
                }
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ]
        }]
    }
    return json.dumps(policy).replace(" ", "")


def url_base64_encode(data: bytes):
    return base64.b64encode(data).replace(b'+', b'-').replace(b'=', b'_').replace(b'/', b'~').decode('utf-8')


def generate_signed_url(resource, valid_seconds):
    """
    method to generate presigned cloudfront url.
    """
    valid_till = (datetime.datetime.now() + datetime.timedelta(seconds=valid_seconds))
    expire_time = int(valid_till.timestamp())
    policy = make_cloudfront_policy(resource, expire_time)

    signature = rsa_signer(policy.encode('utf-8'))
    key_id = os.getenv("PUBLIC_KEY_ID")

    print("generating url = ", resource, valid_seconds)

    # signed url for aws_demo
    signed_url = f"{resource}?" \
                 f"Policy={url_base64_encode(policy.encode('utf-8'))}&" \
                 f"Signature={url_base64_encode(signature)}&" \
                 f"Key-Pair-Id={key_id}"

    data = {
        "signed_url": signed_url,
        "valid_till": valid_till
    }

    return data
