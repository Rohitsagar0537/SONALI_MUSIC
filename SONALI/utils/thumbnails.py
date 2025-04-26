import os
import re
import textwrap

from SONALI import app

import aiofiles
import aiohttp
from PIL import (Image, ImageDraw, ImageEnhance, ImageFilter,
                 ImageFont, ImageOps)
from youtubesearchpython.__future__ import VideosSearch

from config import YOUTUBE_IMG_URL

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(
                        f"cache/thumb{videoid}.png", mode="wb"
                    )
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(20))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.8)

        Xcenter = youtube.width / 2
        Ycenter = youtube.height / 2
        x1 = Xcenter - 300
        y1 = Ycenter - 300
        x2 = Xcenter + 300
        y2 = Ycenter + 300
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((600, 600), Image.Resampling.LANCZOS)
        logo = ImageOps.expand(logo, border=10, fill="white")
        background.paste(logo, (340, 60))

        draw = ImageDraw.Draw(background)

        title_font = ImageFont.truetype("SONALI/assets/font2.ttf", 80)
        artist_font = ImageFont.truetype("SONALI/assets/font2.ttf", 40)
        small_font = ImageFont.truetype("SONALI/assets/font2.ttf", 30)

        title_wrapped = textwrap.wrap(title, width=20)
        title_text = "\n".join(title_wrapped[:2])
        draw.text(
            (340, 300),
            title_text,
            fill="yellow",
            stroke_width=3,
            stroke_fill="red",
            font=title_font,
            align="center"
        )

        draw.text(
            (340, 400),
            f"Singer: {channel}",
            fill="white",
            stroke_width=1,
            stroke_fill="black",
            font=artist_font,
        )

        draw.rectangle((50, 500, 250, 550), fill="black")
        draw.text(
            (60, 510),
            "VIDEO SONG",
            fill="white",
            font=small_font,
        )
        draw.polygon([(220, 510), (240, 525), (220, 540)], fill="red")

        draw.rectangle((0, 700, 1280, 720), fill="black")
        draw.text(
            (10, 702),
            "00:00",
            fill="white",
            font=small_font,
        )
        draw.text(
            (1200, 702),
            f"{duration}",
            fill="white",
            font=small_font,
        )

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
    except Exception as e:
        return YOUTUBE_IMG_URL
