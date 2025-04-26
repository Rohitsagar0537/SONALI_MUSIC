import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from SONALI import app
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
            title = result.get("title", "Unsupported Title")
            title = re.sub(r"\W+", " ", title).title()
            duration = result.get("duration", "Unknown")
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            views = result.get("viewCount", {}).get("short", "Unknown Views")
            channel = result.get("channel", {}).get("name", "Unknown Channel")

        # Download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # Open and process images
        youtube = Image.open(f"cache/thumb{videoid}.png")
        youtube = changeImageSize(1280, 720, youtube)
        blurred_bg = youtube.filter(ImageFilter.BoxBlur(15))

        enhancer = ImageEnhance.Brightness(blurred_bg)
        blurred_bg = enhancer.enhance(0.5)

        final = Image.new("RGBA", (1280, 720))
        final.paste(blurred_bg, (0, 0))
        final.paste(youtube, (0, 0))

        draw = ImageDraw.Draw(final)

        # Fonts
        font_tag = ImageFont.truetype("SONALI/assets/font.ttf", 30)
        font_channel = ImageFont.truetype("SONALI/assets/font2.ttf", 28)
        font_title = ImageFont.truetype("SONALI/assets/font.ttf", 42)
        font_time = ImageFont.truetype("SONALI/assets/font2.ttf", 36)

        # Top SONALI Tag
        text_tag = "TEAM SONALI BOTS"
        w_tag, _ = draw.textsize(text_tag, font=font_tag)
        draw.text((1280 - w_tag - 30, 20), text_tag, fill="white", font=font_tag)

        # Channel Name and Views
        draw.text((50, 560), f"{channel} | {views}", fill="white", font=font_channel)

        # Title
        draw.text((50, 610), clear(title), fill="white", font=font_title)

        # Bottom timing
        time_text = f"00:00 ──────────────── {duration}"
        w_time, _ = draw.textsize(time_text, font=font_time)
        draw.text(((1280 - w_time) / 2, 675), time_text, fill="white", font=font_time)

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        final.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
