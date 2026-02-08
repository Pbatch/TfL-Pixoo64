import time

from pixoo import Pixoo
from tfl import TFL, Stations


def main():
    pixoo = Pixoo()
    tfl = TFL()
    belsize_park = Stations.BELSIZE_PARK

    while True:
        arrivals = [
            arrival
            for arrival in tfl.get_arrivals(belsize_park.station_id)
            if "Northbound" not in arrival["platformName"]
        ]
        header_text = belsize_park.nickname.capitalize()
        image = tfl.make_image(arrivals, header_text)

        payload = {
            "Command": "Draw/SendHttpGif",
            "PicNum": 0,
            "PicWidth": 64,
            "PicOffset": 0,
            "PicID": int(time.time()),
            "PicSpeed": 0,
            "PicData": pixoo.encode_image(image),
        }
        result = pixoo.post(payload)
        print(result)

        time.sleep(10)


if __name__ == "__main__":
    main()
