import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import utils
from utils import BASE_URL

access_token = utils.load_config("access_token")
headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

# Query params for pagination and sorting
query = "?limit=10&page=1&sortBy=createdAt:desc"

utils.send_and_print(
    url=f"{BASE_URL}/users{query}",
    method="GET",
    headers=headers,
    output_file=f"{os.path.splitext(os.path.basename(__file__))[0]}.json"
)