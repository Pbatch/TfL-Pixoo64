import json
import os
from dataclasses import dataclass

import urllib3
from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class Station:
    station_id: str
    nickname: str
    code: str
    underground: bool


@dataclass(frozen=True)
class Stations:
    BATTERSEA_POWER_STATION: Station = Station("940GZZBPSUST", "btsea", "BPS", True)
    BELSIZE_PARK: Station = Station("940GZZLUBZP", "belsize", "BZP", True)
    GOLDERS_GREEN: Station = Station("940GZZLUGGN", "golders", "GGN", True)
    EDGWARE: Station = Station("940GZZLUEGW", "edgwre", "EDG", True)
    KENNINGTON: Station = Station("940GZZLUKNG", "kngtn", "KEN", True)
    MORDEN: Station = Station("940GZZLUMDN", "mrden", "MDN", True)
    EUSTON: Station = Station("940GZZLUEUS", "euston", "EUS", True)
    HAMPSTEAD_HEATH: Station = Station("910GHMPSTDH", "heath", "HDH", False)
    STRATFORD: Station = Station("910GSTFD", "strtfrd", "SRA", False)
    CLAPHAM_JUNCTION: Station = Station("910GCLPHMJ1", "claphm", "CLJ", False)
    RICHMOND: Station = Station("910GRICHMND", "rchmnd", "RMD", False)
    WILLESDEN_JUNCTION: Station = Station("910GWLSDJHL", "wllsdn", "WIJ", False)

DUPLICATE_IDS = {"910GCLPHMJC": "910GCLPHMJ1"}
ID_TO_STATION = {
    v.station_id: v for k, v in Stations.__dict__.items() if isinstance(v, Station)
}

DIRECTION_EXCEPTIONS = {
    "inbound": {
        Stations.HAMPSTEAD_HEATH.station_id: {Stations.STRATFORD.station_id},
    },
    "outbound": {
        Stations.HAMPSTEAD_HEATH.station_id: {
            Stations.CLAPHAM_JUNCTION.station_id,
            Stations.RICHMOND.station_id,
            Stations.WILLESDEN_JUNCTION.station_id,
        },
    },
}


class TFL:
    def __init__(
        self,
        font_path: str = "assets/johnston.ttf",
        font_size: int = 10,
        text_color: tuple[int, int, int] = (255, 211, 0),
        bank_text_color: tuple[int, int, int] = (133, 187, 101),
        background_color: tuple[int, int, int] = (20, 20, 20),
    ):
        self.font_path = font_path
        self.font_size = font_size
        self.text_color = text_color
        self.bank_text_color = bank_text_color
        self.background_color = background_color

        self.pool_manager = urllib3.PoolManager()
        self.font = ImageFont.truetype(self.font_path, self.font_size)
        self.no_arrivals_font = ImageFont.truetype(self.font_path, 9)
        self.underground = Image.open("assets/underground.png")
        self.overground = Image.open("assets/overground.png")
        self.bank = Image.open("assets/bank.png")
        self.cross = Image.open("assets/cross.png")
        self.tube = Image.open("assets/tube.png")
        self.app_key = os.environ["TFL_APP_KEY"]

    @staticmethod
    def _filter_arrivals(arrivals, station_id, inbound):
        filtered_arrivals = []
        direction = "inbound" if inbound else "outbound"
        exceptions = DIRECTION_EXCEPTIONS[direction].get(station_id, set())
        for a in arrivals:
            a["naptanId"] = DUPLICATE_IDS.get(a["naptanId"], a["naptanId"])
            a["destinationNaptanId"] = DUPLICATE_IDS.get(a["destinationNaptanId"], a["destinationNaptanId"])
            if a["direction"] == direction:
                filtered_arrivals.append(a)
                continue

            if a["direction"] == "" and a["destinationNaptanId"] in exceptions:
                filtered_arrivals.append(a)

        filtered_arrivals.sort(key=lambda x: x["timeToStation"])

        return filtered_arrivals

    def _draw_header(self, image, draw, text, underground):
        text_width = draw.textlength(text, font=self.font)
        roundel = self.underground if underground else self.overground

        x = int(32 - (text_width + roundel.width + 2) // 2)
        image.paste(roundel, (x, 3), roundel)
        draw.text(
            xy=(x + roundel.width + 2, 0),
            text=text,
            fill=self.text_color,
            font=self.font,
            anchor="la",
        )

    def _draw_no_arrivals(self, image, draw, y):
        image.paste(self.tube, (32 - self.tube.width // 2, y + 10), self.tube)
        text = "Service closed"
        text_width = int(draw.textlength(text, font=self.no_arrivals_font))
        draw.text(
            xy=(32 - text_width // 2, y + 10 + self.tube.height),
            text=text,
            fill=self.text_color,
            font=self.no_arrivals_font,
            anchor="la",
        )

    def _get_arrivals(self, station_id):
        url = f"https://api.tfl.gov.uk/StopPoint/{station_id}/Arrivals?APP_KEY={self.app_key}"
        try:
            response = self.pool_manager.request(
                "GET",
                url,
                timeout=5.0
            )

            if response.status != 200:
                print(f"TfL API Error: {response.status}")
                return []

            return json.loads(response.data.decode("utf-8"))

        except Exception as e:
            print(f"Request failed: {e}")
            return []

    def get_and_filter_arrivals(self, station_id: str, inbound: bool) -> list[dict]:
        arrivals = self._get_arrivals(station_id)
        arrivals = self._filter_arrivals(arrivals, station_id, inbound)
        return arrivals

    def make_image(self, arrivals: list[dict], header_text: str, underground: bool) -> Image:
        image = Image.new("RGB", (64, 64), color=self.background_color)
        draw = ImageDraw.Draw(image)

        self._draw_header(image, draw, header_text, underground)

        # height of the header
        y = self.font_size
        for arrival in arrivals:
            fill = self.bank_text_color if "via Bank" in arrival["towards"] else self.text_color

            try:
                nickname = ID_TO_STATION[arrival["destinationNaptanId"]].nickname
            except KeyError:
                print(f"Arrival is not a listed station: {arrival}")
                nickname = arrival["destinationName"].split()[0][:3]
            left_text = nickname.capitalize()

            draw.text(
                xy=(1, y),
                text=left_text,
                fill=fill,
                font=self.font,
                anchor="la",
            )

            mins_to_station = arrival["timeToStation"] // 60
            right_text = "Due" if mins_to_station == 0 else f"{mins_to_station}m"
            draw.text(
                xy=(63, y),
                text=right_text,
                fill=fill,
                font=self.font,
                anchor="ra",
            )

            y += self.font_size
            if y + self.font_size >= 64:
                break

        if y == self.font_size:
            self._draw_no_arrivals(image, draw, y)

        return image


def main():
    tfl = TFL()
    station = Stations.HAMPSTEAD_HEATH
    arrivals = tfl.get_and_filter_arrivals(station.station_id, inbound=False)
    image = tfl.make_image(arrivals, station.nickname.capitalize(), underground=station.underground)
    image.save("debug.png")


if __name__ == "__main__":
    main()
