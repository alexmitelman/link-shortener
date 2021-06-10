import os
import random
import string
from typing import Dict

import boto3
from chalice import Chalice, Response

LINKS_TABLE = os.environ["LINKS_TABLE"]
CODES_TABLE = os.environ["CODES_TABLE"]
client = boto3.client("dynamodb")

app = Chalice(app_name="link-shortener")


def generate_random_string(number_of_chars: int) -> str:
    list_of_chars = []
    chars = string.ascii_letters + string.digits
    for _ in range(number_of_chars):
        random_char = random.choice(chars)
        list_of_chars.append(random_char)
    return "".join(list_of_chars)


def get_code_for_link(link: str) -> str:
    resp = client.get_item(TableName=LINKS_TABLE, Key={"link": {"S": link}})
    item = resp.get("Item")
    if item:
        code = item.get("code").get("S")
    else:
        code = None
    return code


def get_link_by_code(code: str) -> str:
    resp = client.get_item(TableName=CODES_TABLE, Key={"code": {"S": code}})
    item = resp.get("Item")
    if item:
        link = item.get("link").get("S")
    else:
        link = None
    return link


def save_record(link: str, code: str) -> None:
    _ = client.put_item(
        TableName=LINKS_TABLE, Item={"link": {"S": link}, "code": {"S": code}}
    )

    _ = client.put_item(
        TableName=CODES_TABLE, Item={"code": {"S": code}, "link": {"S": link}}
    )

    return


@app.route("/", methods=["POST"])
def add_new_url() -> Dict[str, str]:
    body = app.current_request.json_body
    original_url = body["link"]
    host = app.current_request.context["domainName"]

    code = get_code_for_link(original_url)
    if code:
        url_code = code
    else:
        url_code = generate_random_string(8)
        save_record(original_url, url_code)

    shortened_url = f"https://{host}/{url_code}"

    return {"shortened_url": shortened_url, "original_url": original_url}


@app.route("/{code}", methods=["GET"])
def read_url(code: str) -> Response:
    link = get_link_by_code(code)
    return Response(status_code=301, headers={"Location": link})
