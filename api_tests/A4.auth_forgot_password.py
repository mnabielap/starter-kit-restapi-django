import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import utils
from utils import BASE_URL

payload = {
    "email": "testuser@example.com"
}

# Note: Check your Django console logs to see the generated token/email content
utils.send_and_print(
    url=f"{BASE_URL}/auth/forgot-password",
    method="POST",
    body=payload,
    output_file=f"{os.path.splitext(os.path.basename(__file__))[0]}.json"
)