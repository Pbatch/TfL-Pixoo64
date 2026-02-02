import time

from pixoo import Pixoo
from tfl import TFL, Stations


def lambda_handler(event, context):
    pixoo = Pixoo()
    tfl = TFL()
    countdown = tfl.get_countdown(Stations.BELSIZE_PARK)

    payload = {
        "Command": "Draw/SendHttpGif",
        "PicNum": 1,
        "PicWidth": 64,
        "PicOffset": 0,
        "PicID": int(time.time()),
        "PicSpeed": 0,
        "PicData": pixoo.encode_image(countdown),
    }
    result = pixoo.post(payload)

    return result


def main():
    event = None
    context = None
    result = lambda_handler(event, context)
    print(result)


if __name__ == "__main__":
    main()
