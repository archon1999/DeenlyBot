"""Rebuild the simple typographic share card (Pillow; no remote assets)."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--font", type=Path, required=True, help="Path to a locally licensed TrueType font")
    args = parser.parse_args()
    canvas = Image.new("RGB", (1200, 630), "#f8fcfa")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((50, 50, 1150, 580), radius=40, fill="white")
    draw.rounded_rectangle((88, 104, 98, 518), radius=5, fill="#087f6f")
    title = ImageFont.truetype(str(args.font), 94)
    subtitle = ImageFont.truetype(str(args.font), 33)
    small = ImageFont.truetype(str(args.font), 24)
    draw.text((145, 150), "Deenly.uz", font=title, fill="#087f6f")
    draw.text((150, 300), "Ilm va ibodat uchun kichik qadamlar", font=subtitle, fill="#1c292d")
    draw.text((150, 382), "Allohning ismlari  /  Arab tili  /  Qur’on  /  Duolar", font=small, fill="#52666a")
    draw.text((150, 480), "O‘qing. Mashq qiling. Takrorlang.", font=small, fill="#087f6f")
    target = Path(__file__).resolve().parents[1] / "frontend/public/social-card.png"
    canvas.save(target, optimize=True)
    print(target)


if __name__ == "__main__":
    main()
