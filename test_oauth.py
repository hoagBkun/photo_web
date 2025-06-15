from authlib.integrations.requests_client import OAuth2Session
import logging
import os
from config import Config

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

client_id = Config.GOOGLE_CLIENT_ID
client_secret = Config.GOOGLE_CLIENT_SECRET
redirect_uri = 'http://localhost:5000/auth/authorize/google'
scope = ['openid', 'email', 'profile']
authorization_endpoint = 'https://accounts.google.com/o/oauth2/v2/auth'
token_endpoint = 'https://oauth2.googleapis.com/token'

try:
    client = OAuth2Session(client_id, client_secret, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = client.create_authorization_url(authorization_endpoint)
    logging.debug(f"Authorization URL: {authorization_url}")
    print(f"Open this URL in your browser: {authorization_url}")
except Exception as e:
    logging.error(f"Error creating OAuth session: {str(e)}", exc_info=True)