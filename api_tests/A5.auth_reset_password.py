import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import utils
from utils import BASE_URL

# Try to load a token if manually placed in secrets, else use a dummy one to test the endpoint
token = utils.load_config("reset_token") or "dummy_reset_token_from_email"

payload = {
    "password": "newpassword123"
}

utils.send_and_print(
    url=f"{BASE_URL}/auth/reset-password?token={token}",
    method="POST",
    body=payload,
    output_file=f"{os.path.splitext(os.path.basename(__file__))[0]}.json"
)