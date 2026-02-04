import base64
import json
import os

import requests
from PIL import Image


class Pixoo:
    def __init__(self):
        self.session = requests.session()
        self.pixoo_url = os.environ["PIXOO_URL"]

    @staticmethod
    def encode_image(image: Image):
        size = (image.width, image.height)
        if size != (64, 64):
            raise ValueError(
                f"Pixoo images must be 64x64, but the image size was {size}"
            )

        pixels = []
        for red, green, blue in image.getdata():
            pixels.extend([red, green, blue])

        return base64.b64encode(bytearray(pixels)).decode("utf-8")

    def post(self, payload):
        try:
            response = self.session.post(self.pixoo_url, json=payload, timeout=5.0)
            response.raise_for_status()

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"status": "Success", "pixoo_response": response.json()}
                ),
            }
        except requests.exceptions.RequestException as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"status": "Error", "reason": str(e)}),
            }
