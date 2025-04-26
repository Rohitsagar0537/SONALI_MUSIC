import os
import re
import textwrap
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
import aiofiles
import aiohttp
from youtubesearchpython.__future__ import VideosSearch

from config import YOUTUBE_IMG_URL

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

# Clear function to clean up title text
def clear(text):
    return textwrap.fill(text, width=40)

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
                title = "Unknown Title"
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
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(ImageFilter.GaussianBlur(12))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.4)

        draw = ImageDraw.Draw(background)

        font_main = ImageFont.truetype("SONALI/assets/font.ttf", 50)
        font_small = ImageFont.truetype("SONALI/assets/font2.ttf", 35)
        font_tag = ImageFont.truetype("SONALI/assets/font.ttf", 28)

        # Upper Tag
        tag_text = "TEAM PURVI BOTS PRESENTS"
        tag_size = draw.textsize(tag_text, font=font_tag)
        draw.text(((1280 - tag_size[0]) // 2, 20), tag_text, fill="yellow", font=font_tag)

        # Title in center with stroke effect
        title_text = clear(title)
        title_pos = ((1280 - draw.textsize(title_text, font=font_main)[0]) // 2, 550)
        draw.text(title_pos, title_text, font=font_main, fill="white", stroke_width=2, stroke_fill="black")

        # Channel and Views
        info_text = f"{channel} | {views}"
        draw.text((50, 630), info_text, fill="white", font=font_small)

        # Duration bar
        draw.rectangle([(50, 670), (1230, 700)], outline="white", width=4)
        draw.text((55, 705), "00:00", fill="white", font=font_tag)
        draw.text((1150, 705), duration, fill="white", font=font_tag)

        # Add smooth white border
        border_width = 20
        border = Image.new("RGBA", (background.width + border_width * 2, background.height + border_width * 2), (255, 255, 255))
        border.paste(background, (border_width, border_width))
        border = border.filter(ImageFilter.GaussianBlur(5))

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
        border.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
