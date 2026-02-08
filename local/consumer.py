import json
import time

from tfl import ID_TO_STATION
from pixoo import Pixoo
from tfl import TFL, Stations

pixoo = Pixoo()
tfl = TFL()


def lambda_handler(event, context):
    record = event["Records"][0]
    body = json.loads(record["body"])
    station = ID_TO_STATION[body["station_id"]]
    inbound = body["inbound"]

    countdown = tfl.make_image(
        arrivals=tfl.get_arrivals(station.station_id, inbound),
        header_text=station.nickname.capitalize(),
        underground=station.underground
    )

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
    body = {"station_id": Stations.HAMPSTEAD_HEATH.station_id, "inbound": True}
    event = {"Records": [{"body": json.dumps(body)}]}
    context = None
    result = lambda_handler(event, context)
    print(result)


if __name__ == "__main__":
    main()
