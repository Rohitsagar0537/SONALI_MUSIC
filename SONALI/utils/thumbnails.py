import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from SONALI import app  # Updated to SONALI
from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def clear(text):
    list = text.split(" ")
    title = ""
    for i in list:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()


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

        # Download thumbnail image
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")

        # Apply a blur effect to the background
        background = image2.filter(filter=ImageFilter.BoxBlur(10))  # Lighter blur effect
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.5)  # Increase brightness slightly
        draw = ImageDraw.Draw(background)

        # Set fonts
        arial = ImageFont.truetype("SONALI/assets/font2.ttf", 30)  # Updated to SONALI folder
        font = ImageFont.truetype("SONALI/assets/font.ttf", 30)  # Updated to SONALI folder

        # Place the "TEAM SONALI BOTS" text at the top-right
        text_size = draw.textsize("TEAM SONALI BOTS    ", font=font)
        draw.text((1280 - text_size[0] - 10, 10), "TEAM SONALI BOTS    ", fill="white", font=font)

        # Channel name and views
        draw.text(
            (55, 560),
            f"{channel} | {views[:23]}",  # Channel name and views placed correctly
            (255, 255, 255),
            font=arial,
        )

        # Title of the video
        draw.text(
            (57, 600), 
            clear(title),  # Title placed below channel
            (255, 255, 255),
            font=font,
        )

        # Add a line separator
        draw.line(
            [(55, 660), (1220, 660)],
            fill="white",
            width=5,
            joint="curve",
        )

        # Duration indicator
        draw.ellipse(
            [(918, 648), (942, 672)],
            outline="white",
            fill="white",
            width=15,
        )
        draw.text(
            (36, 685),
            "00:00",
            (255, 255, 255),
            font=arial,
        )
        draw.text(
            (1185, 685),
            f"{duration[:23]}",  # Duration placed at the bottom-right
            (255, 255, 255),
            font=arial,
        )

        # Clean up and save the final image
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
