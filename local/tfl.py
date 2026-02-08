import os
from dataclasses import dataclass

import requests
from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class Station:
    station_id: str
    nickname: str
    code: str


@dataclass(frozen=True)
class Stations:
    BATTERSEA_POWER_STATION: Station = Station("940GZZBPSUST", "battersea", "BPS")
    BELSIZE_PARK: Station = Station("940GZZLUBZP", "belsize", "BZP")
    KENNINGTON: Station = Station("940GZZLUKNG", "kennington", "KEN")
    MORDEN: Station = Station("940GZZLUMDN", "morden", "MDN")
    EUSTON: Station = Station("940GZZLUEUS", "euston", "EUS")


ID_TO_STATION = {
    v.station_id: v for k, v in Stations.__dict__.items() if isinstance(v, Station)
}


class TFL:
    def __init__(
        self,
        font_path: str = "assets/johnston.ttf",
        font_size: int = 10,
        text_color: tuple[int, int, int] = (255, 211, 0),
        background_color: tuple[int, int, int] = (20, 20, 20),
    ):
        self.font_path = font_path
        self.font_size = font_size
        self.text_color = text_color
        self.background_color = background_color

        self.session = requests.Session()
        self.font = ImageFont.truetype(self.font_path, self.font_size)
        self.no_arrivals_font = ImageFont.truetype(self.font_path, 9)
        self.roundel = Image.open("assets/roundel.png")
        self.bank = Image.open("assets/bank.png")
        self.cross = Image.open("assets/cross.png")
        self.tube = Image.open("assets/tube.png")
        self.app_key = os.environ["TFL_APP_KEY"]

    def _draw_header(self, image, draw, text):
        text_width = draw.textlength(text, font=self.font)

        x = int(32 - (text_width + self.roundel.width + 2) // 2)
        image.paste(self.roundel, (x, 3), self.roundel)
        draw.text(
            xy=(x + self.roundel.width + 2, 0),
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

    def get_arrivals(self, station_id):
        tfl_url = f"https://api.tfl.gov.uk/StopPoint/{station_id}/Arrivals"
        params = {"APP_KEY": self.app_key}
        try:
            response = self.session.get(tfl_url, params=params, timeout=5)
            arrivals = response.json()
        except Exception as e:
            print(e)
            return []

        arrivals.sort(key=lambda x: x["timeToStation"])

        return arrivals

    def make_image(self, arrivals, header_text):
        image = Image.new("RGB", (64, 64), color=self.background_color)
        draw = ImageDraw.Draw(image)

        self._draw_header(image, draw, header_text)

        # height of the header
        y = self.font_size
        for arrival in arrivals:
            if "Northbound" in arrival["platformName"]:
                continue

            try:
                code = ID_TO_STATION[arrival["destinationNaptanId"]].code
            except KeyError:
                print(f"Arrival is not a listed station: {arrival}")
                code = arrival["destinationName"].split()[0][:3]

            left_text = code.capitalize()
            left_width = int(draw.textlength(left_text, font=self.font))
            draw.text(
                xy=(1, y),
                text=left_text,
                fill=self.text_color,
                font=self.font,
                anchor="la",
            )

            if "via CX" in arrival["towards"]:
                image.paste(self.cross, (3 + left_width, y + 3), self.cross)
            elif "via Bank" in arrival["towards"]:
                image.paste(self.bank, (3 + left_width, y + 2), self.bank)

            mins_to_station = arrival["timeToStation"] // 60
            right_text = "Due" if mins_to_station == 0 else f"{mins_to_station}m"
            draw.text(
                xy=(63, y),
                text=right_text,
                fill=self.text_color,
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
    belsize_park = Stations.BELSIZE_PARK
    arrivals = tfl.get_arrivals(belsize_park.station_id)
    tfl.make_image(arrivals, belsize_park.nickname.capitalize())


if __name__ == "__main__":
    main()
