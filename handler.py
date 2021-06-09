import json
import os
import random
import string
from typing import Any, Dict, Union

import boto3

LINKS_TABLE = os.environ["LINKS_TABLE"]
CODES_TABLE = os.environ["CODES_TABLE"]
client = boto3.client("dynamodb")


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


def add_new_url(event: Dict[str, Any], context: Union[int, slice]) -> str:
    body = json.loads(event["body"])
    original_url = body["link"]
    host = event["requestContext"]["domainName"]

    code = get_code_for_link(original_url)
    if code:
        url_code = code
    else:
        url_code = generate_random_string(8)
        save_record(original_url, url_code)

    shortened_url = f"https://{host}/{url_code}"

    body = {"shortened_url": shortened_url, "original_url": original_url}

    return json.dumps(body)


def read_url(event: Dict[str, Any], context: Union[int, slice]) -> str:
    print(event)
    code = event["pathParameters"]["code"]

    link = get_link_by_code(code)
    return json.dumps({"location": link, "statusCode": 301})
