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
        youtube = youtube.convert("RGBA")

        # Create main background (16:9 aspect ratio)
        background = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(radius=10))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.8)  # Slightly dark

        draw = ImageDraw.Draw(background)

        # Prepare center thumbnail (942x422)
        center_thumb_size = (942, 422)  # Updated size
        center_thumb = youtube.resize(center_thumb_size)

        # Add a white border around the center thumbnail
        border_size = 10  # Set the border size
        bordered_center_thumb = Image.new("RGBA", (center_thumb_size[0] + 2 * border_size, center_thumb_size[1] + 2 * border_size), (255, 255, 255))
        bordered_center_thumb.paste(center_thumb, (border_size, border_size))

        # Center position for the bordered thumbnail
        pos_x = (1280 - bordered_center_thumb.size[0]) // 2
        pos_y = (720 - bordered_center_thumb.size[1]) // 2

        background.paste(bordered_center_thumb, (pos_x, pos_y))

        # Fonts
        arial = ImageFont.truetype("SONALI/assets/font2.ttf", 30)
        font = ImageFont.truetype("SONALI/assets/font.ttf", 30)

        # Top-right "TEAM SONALI BOTS"
        text_size = draw.textsize("TEAM SONALI BOTS    ", font=font)
        draw.text((1280 - text_size[0] - 10, 10), "TEAM SONALI BOTS    ", fill="white", font=font)

        # Channel name and views (moved further down)
        draw.text(
            (55, 570),  # Increased the Y position to move it down further
            f"{channel} | {views[:23]}",
            (255, 255, 255),
            font=arial,
        )

        # Video title (moved further down)
        draw.text(
            (57, 610),  # Increased the Y position to move it down further
            title,
            (255, 255, 255),
            font=font,
        )

        # Bottom line
        bold_font = ImageFont.truetype("SONALI/assets/font.ttf", 33)
        draw.text((55, 645), "00:00", fill="white", font=bold_font)

        # Line
        start_x = 150
        end_x = 1130
        line_y = 660  # Increased the line's Y position to match
        draw.line([(start_x, line_y), (end_x, line_y)], fill="white", width=4)

        # Duration (moved slightly down)
        duration_text_size = draw.textsize(duration, font=bold_font)
        draw.text((1180 - duration_text_size[0], 645), duration, fill="white", font=bold_font)

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
