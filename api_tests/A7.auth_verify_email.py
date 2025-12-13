import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import utils
from utils import BASE_URL

# Try to load a token if manually placed in secrets, else use a dummy one
token = utils.load_config("verify_email_token") or "dummy_verify_token"

utils.send_and_print(
    url=f"{BASE_URL}/auth/verify-email?token={token}",
    method="POST",
    output_file=f"{os.path.splitext(os.path.basename(__file__))[0]}.json"
)