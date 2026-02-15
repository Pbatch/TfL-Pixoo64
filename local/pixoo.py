import base64
import json
import os

import urllib3
from PIL import Image


class Pixoo:
    def __init__(self):
        self.pool_manager = urllib3.PoolManager()
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
        encoded_payload = json.dumps(payload).encode("utf-8")
        try:
            response = self.pool_manager.request(
                "POST",
                self.pixoo_url,
                body=encoded_payload,
                headers={"Content-Type": "application/json"},
                timeout=5.0,
            )

            if response.status >= 400:
                return {
                    "statusCode": response.status,
                    "body": json.dumps(
                        {
                            "status": "Error",
                            "reason": f"Pixoo returned status code {response.status}",
                        }
                    ),
                }

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "status": "Success",
                        "pixoo_response": json.loads(response.data.decode("utf-8")),
                    }
                ),
            }
        except urllib3.exceptions.HTTPError as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"status": "Error", "reason": str(e)}),
            }
