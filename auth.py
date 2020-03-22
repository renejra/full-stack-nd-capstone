import json, os
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

# Get environment variables

AUTH_DOMAIN = 'botfsnd.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'capstone'


## AuthError exception handler

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Authentication Methods

'''
get_token_auth_header() method

    - Gets the header from the request
        + Raises an AuthError if no header is present

    - Attempts to split bearer and the token
        + Raises an AuthError if the header is malformed

    - Returns the token part of the header
'''

def get_token_auth_header():
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is missing.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be a bearer token.'
        }, 401)

    token = parts[1]
    return token


'''
check_permissions(permission, payload) method

    Inputs used:
        permission: string permission ('post:bots')
        payload: decoded jwt payload

    - Raises an AuthError if permissions are not included in the payload
    - Raises an AuthError if the requested permission string is not in the payload permissions array
    - Returns true otherwise
'''

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        abort(401)

    if permission not in payload['permissions']:
        abort(401)

    return True


'''
verify_decode_jwt(token) method

    Required input:
        Json Web Token (string)

    - Checks that the token complies with the following:
        + it should be an Auth0 token with key id (kid)
        + it should verify the token using Auth0 /.well-known/jwks.json
        + it should decode the payload from the token
        + it should validate the claims
    - Returns a decoded payload
'''

def verify_decode_jwt(token):
    # Get public key from Auth0 - print jwks to get the json data from Auth0, check KID
    jsonurl = urlopen(f'https://{AUTH_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    
    # Get header data - print this to check if KID matches Auth0's
    unverified_header = jwt.get_unverified_header(token)
    
    # Check the RSA key has the KID
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            # Use KID to validate JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 401)

    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 401)


# Binding it all together - the decorator method

'''
@requires_auth(permission) decorator method

    Required inputs:
        permission: string permission ('post:strategy')

    - The decorator performs the following methods:
        + The get_token_auth_header method to get the token
        + The verify_decode_jwt method to decode the jwt
        + The check_permissions method validate claims and check the requested permission
    - Then returns the decorator which passes the decoded payload to the decorated method
'''

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator