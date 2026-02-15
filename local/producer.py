import json
import os

import boto3
from tfl import Stations

sqs = boto3.client("sqs")


def lambda_handler(event, context):
    for station_id, inbound, delay in [
        [Stations.BELSIZE_PARK.station_id, True, 0],
        [Stations.HAMPSTEAD_HEATH.station_id, False, 15],
        [Stations.BELSIZE_PARK.station_id, True, 30],
        [Stations.HAMPSTEAD_HEATH.station_id, False, 45],
    ]:
        body = {"station_id": station_id, "inbound": inbound}
        sqs.send_message(
            QueueUrl=os.environ["QUEUE_URL"],
            MessageBody=json.dumps(body),
            DelaySeconds=delay,
        )
    return None


def main():
    event = None
    context = None
    lambda_handler(event, context)


if __name__ == "__main__":
    main()
