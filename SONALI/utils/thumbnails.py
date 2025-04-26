import os
import re
import aiofiles
import aiohttp
from PIL import (Image, ImageDraw, ImageEnhance, ImageFilter,
                 ImageFont, ImageOps)
from youtubesearchpython.__future__ import VideosSearch

from config import YOUTUBE_IMG_URL

# Cache folder check
if not os.path.exists("cache"):
    os.makedirs("cache")

# Clear function
def clear(text):
    return re.sub(r"\W+", " ", text).title()

# Resize image
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))

# Smooth rounded box draw
def draw_rounded_rectangle(draw, xy, radius, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, outline=outline, width=width)

# Main function
async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    try:
        results = VideosSearch(videoid, limit=1)
        result_data = (await results.next())["result"][0]

        title = clear(result_data.get("title", "Unknown Title"))
        duration = result_data.get("duration", "Unknown Mins")
        thumbnail = result_data["thumbnails"][0]["url"].split("?")[0]
        views = result_data.get("viewCount", {}).get("short", "Unknown Views")
        channel = result_data.get("channel", {}).get("name", "Unknown Channel")

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/thumb{videoid}.png", mode="wb") as f:
                        await f.write(await resp.read())

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(ImageFilter.GaussianBlur(12))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.4)

        draw = ImageDraw.Draw(background)

        # Fonts
        font_main = ImageFont.truetype("SONALI/assets/font.ttf", 50)
        font_small = ImageFont.truetype("SONALI/assets/font2.ttf", 35)
        font_tag = ImageFont.truetype("SONALI/assets/font.ttf", 28)

        # Smooth white rounded border
        border_margin = 20
        draw_rounded_rectangle(
            draw,
            (border_margin, border_margin, 1280 - border_margin, 720 - border_margin),
            radius=30,
            outline="white",
            width=6
        )

        # Upper Tag
        tag_text = "TEAM PURVI BOTS PRESENTS"
        tag_width, _ = font_tag.getsize(tag_text)
        draw.text(((1280 - tag_width) // 2, 50), tag_text, fill="yellow", font=font_tag)

        # Title in center with stroke effect
        title_width, _ = font_main.getsize(title)
        title_pos = ((1280 - title_width) // 2, 550)
        draw.text(title_pos, title, font=font_main, fill="white", stroke_width=2, stroke_fill="black")

        # Channel and Views
        info_text = f"{channel} | {views}"
        draw.text((50, 630), info_text, fill="white", font=font_small)

        # Duration bar
        draw.rectangle([(50, 670), (1230, 700)], outline="white", width=4)
        draw.text((55, 705), "00:00", fill="white", font=font_tag)
        draw.text((1150, 705), duration, fill="white", font=font_tag)

        # Save final image
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except FileNotFoundError:
            pass

        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"

    except Exception as e:
        print(f"[ERROR] get_thumb: {e}")
        return YOUTUBE_IMG_URL
