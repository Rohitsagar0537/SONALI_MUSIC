import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from SONALI import app  # PURVIMUSIC -> SONALI
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
                title = re.sub(r"\W+", " ", title).title()
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

        # Download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # Open thumbnail
        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)

        # Create blurred background
        image2 = image1.convert("RGBA")
        background = image2.filter(ImageFilter.BoxBlur(10))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.5)

        # Paste main thumbnail on top of background
        background.paste(image1, (0, 0))

        draw = ImageDraw.Draw(background)

        # Fonts
        font_tag = ImageFont.truetype("SONALI/assets/font.ttf", 30)
        font_channel = ImageFont.truetype("SONALI/assets/font2.ttf", 30)
        font_title = ImageFont.truetype("SONALI/assets/font.ttf", 40)
        font_time = ImageFont.truetype("SONALI/assets/font.ttf", 35)

        # Top tag
        tag_text = "TEAM SONALI BOTS"
        tag_width, _ = draw.textsize(tag_text, font=font_tag)
        draw.text((1280 - tag_width - 20, 20), tag_text, fill="white", font=font_tag)

        # Channel and Views
        info_text = f"{channel} | {views[:23]}"
        draw.text((50, 560), info_text, fill="white", font=font_channel)

        # Title
        song_title = clear(title)
        draw.text((50, 600), song_title, fill="white", font=font_title)

        # Bottom Timing Line
        timing_text = f"00:00 ──────────────── {duration[:23]}"
        timing_width, _ = draw.textsize(timing_text, font=font_time)
        timing_x = (1280 - timing_width) // 2
        timing_y = 670
        draw.text((timing_x, timing_y), timing_text, fill="white", font=font_time)

        # Remove temp thumb
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        # Save final
        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
