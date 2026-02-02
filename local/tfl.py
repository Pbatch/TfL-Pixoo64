from dataclasses import dataclass

import requests
from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class Station:
    station_id: str
    nickname: str


@dataclass(frozen=True)
class Stations:
    BATTERSEA_POWER_STATION: Station = Station("940GZZBPSUST", "battersea")
    BELSIZE_PARK: Station = Station("940GZZLUBZP", "belsize")
    KENNINGTON: Station = Station("940GZZLUKNG", "kennington")
    MORDEN: Station = Station("940GZZLUMDN", "morden")


ID_TO_STATION = {
    v.station_id: v for k, v in Stations.__dict__.items() if isinstance(v, Station)
}


class TFL:
    def __init__(
        self,
        font_path: str = "assets/johnston.ttf",
        font_size: int = 8,
        text_color: tuple[int, int, int] = (255, 211, 0),
        background_color: tuple[int, int, int] = (20, 20, 20),
    ):
        self.font_path = font_path
        self.font_size = font_size
        self.text_color = text_color
        self.background_color = background_color

        self.font = ImageFont.truetype(self.font_path, self.font_size)

        self.roundel = Image.open("assets/roundel.png")
        self.coin = Image.open("assets/coin.png")
        self.cross = Image.open("assets/cross.png")
        self.tube = Image.open("assets/tube.png")

    @staticmethod
    def _get_arrivals(station_id):
        tfl_url = f"https://api.tfl.gov.uk/StopPoint/{station_id}/Arrivals"
        try:
            response = requests.get(tfl_url, timeout=5)
            arrivals = response.json()
        except Exception as e:
            print(e)
            return []

        arrivals.sort(key=lambda x: x["timeToStation"])

        return arrivals

    def _draw_header(self, image, draw, text):
        text_width = draw.textlength(text, font=self.font)

        x = int(32 - (text_width + self.roundel.width + 2) // 2)
        image.paste(self.roundel, (x, 3))
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
        text_width = int(draw.textlength(text, font=self.font))
        draw.text(
            xy=(32 - text_width // 2, y + 10 + self.tube.height),
            text=text,
            fill=self.text_color,
            font=self.font,
            anchor="la",
        )

    def get_countdown(self, station: Station):
        image = Image.new("RGB", (64, 64), color=self.background_color)
        draw = ImageDraw.Draw(image)

        self._draw_header(image, draw, station.nickname.capitalize())

        arrivals = self._get_arrivals(station.station_id)

        # height of the header
        y = self.font_size
        for arrival in arrivals:
            if "Northbound" in arrival["platformName"]:
                continue

            try:
                nickname = ID_TO_STATION[arrival["destinationNaptanId"]].nickname
            except KeyError:
                print(f"Arrival is not a listed station: {arrival}")
                nickname = arrival["destinationName"].split()[0]

            left_text = nickname.capitalize()
            left_width = int(draw.textlength(left_text, font=self.font))
            draw.text(
                xy=(1, y),
                text=left_text,
                fill=self.text_color,
                font=self.font,
                anchor="la",
            )

            if "via CX" in arrival["towards"]:
                image.paste(self.cross, (2 + left_width, y + 2))
            elif "via Bank" in arrival["towards"]:
                image.paste(self.coin, (2 + left_width, y + 2))

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


if __name__ == "__main__":
    tfl = TFL()
    tfl.get_countdown(Stations.BELSIZE_PARK)
