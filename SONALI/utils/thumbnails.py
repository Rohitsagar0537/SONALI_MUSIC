from SONALI import app
from config import YOUTUBE_IMG_URL


import os
import re
import aiohttp
import aiofiles
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from youtubesearchpython.__future__ import VideosSearch

def clear(text):
    return re.sub("\s+", " ", text).strip()

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(image.size[0] * min(widthRatio, heightRatio))
    newHeight = int(image.size[1] * min(widthRatio, heightRatio))
    return image.resize((newWidth, newHeight))

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

        # Download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")

        # Create blurred background
        background = image2.filter(ImageFilter.BoxBlur(10))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.5)
        draw = ImageDraw.Draw(background)

        # Prepare clear thumbnail with white border (fixed 1280x580)
        thumb_width = 1280
        thumb_height = 580
        thumb_size = (thumb_width, thumb_height)
        thumb = image1.resize(thumb_size)

        border_size = 8
        bordered_thumb = Image.new('RGBA', (thumb_size[0] + border_size * 2, thumb_size[1] + border_size * 2), (255, 255, 255, 255))
        bordered_thumb.paste(thumb, (border_size, border_size))

        # Center paste
        pos_x = (1280 - bordered_thumb.size[0]) // 2
        pos_y = (720 - bordered_thumb.size[1]) // 2
        background.paste(bordered_thumb, (pos_x, pos_y), bordered_thumb)

        # Fonts
        arial = ImageFont.truetype("SONALI/assets/font2.ttf", 30)  # normal
        font = ImageFont.truetype("SONALI/assets/font.ttf", 30)    # bold

        # "TEAM SONALI BOTS" top-right
        text_size = draw.textsize("TEAM SONALI BOTS    ", font=font)
        draw.text((1280 - text_size[0] - 10, 10), "TEAM SONALI BOTS    ", fill="white", font=font)

        # Channel name and views — thoda niche
        draw.text(
            (55, 590),
            f"{channel} | {views[:23]}",
            (255, 255, 255),
            font=arial,
        )

        # Video title — thoda aur niche
        draw.text(
            (57, 630),
            clear(title),
            (255, 255, 255),
            font=font,
        )

        # Bottom bold line: 00:00 --- 3:45
        bold_font = ImageFont.truetype("SONALI/assets/font.ttf", 33)

        # "00:00"
        draw.text((55, 685), "00:00", fill="white", font=bold_font)

        # Line
        start_x = 150
        end_x = 1130
        line_y = 700
        draw.line([(start_x, line_y), (end_x, line_y)], fill="white", width=4)

        # Duration
        duration_text_size = draw.textsize(duration, font=bold_font)
        draw.text((1180 - duration_text_size[0], 685), duration, fill="white", font=bold_font)

        # Clean up
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
