from datetime import datetime, timedelta
from requests import post
import pytz

from harvestreaper.settings import HARVEST_CLIENT_ID, HARVEST_CLIENT_SECRET

HARVEST_AUTH_URL = 'https://id.getharvest.com'
HARVEST_API_URL = 'https://api.harvestapp.com/api/v2/'


def get_harvest_token(code, code_key, grant_type):
    request_data = {
        code_key: code,
        'client_id': HARVEST_CLIENT_ID,
        'client_secret': HARVEST_CLIENT_SECRET,
        'grant_type': grant_type
    }
    response = post(
        f'{HARVEST_AUTH_URL}/api/v2/oauth2/token', json=request_data)
    json = response.json()

    # Save the token for use later!
    return json.get('access_token'), json.get('refresh_token'), pytz.UTC.localize(datetime.utcnow() + timedelta(seconds=json.get('expires_in')))
