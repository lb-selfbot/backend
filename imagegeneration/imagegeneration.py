"""
Image Generation Module
"""

import io
import random


import textwrap
import requests
import PIL
import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw
import PIL.ImageOps
import PIL.ImageFilter
import PIL.ImageChops
import PIL.ImageEnhance
import PIL.ImageColor


class AlexFlipNote:
    """
    AlexFlipNote Image Generation
    """

    def _get_file(self, filename: str):
        """
        Get an asset file
        """
        with open(f"assets/{filename}", "rb") as file:
            return file.read()

    def create_achievement(self, ach: str, colour=(255, 255, 0, 255), icon: int = None):
        """
        Create a Minecraft achievement
        """
        if not icon:
            icon = random.randint(1, 45)
        front = PIL.Image.open(f"assets/achievement/{icon}.png")

        text = PIL.Image.new("RGBA", (len(ach) * 15, 64))
        font = PIL.ImageFont.truetype("assets/_fonts/Minecraft.ttf", 16)
        draw = PIL.ImageDraw.Draw(text)
        width, _ = draw.textsize(ach, font=font)
        width = max(320, width)
        mid = PIL.Image.new("RGBA", (width + 20, 64), (255, 255, 255, 0))
        achmid = PIL.Image.open("assets/achievement/achmid.png")
        achend = PIL.Image.open("assets/achievement/achend.png")
        for i in range(0, width):
            mid.paste(achmid, (i, 0))
        mid.paste(achend, (width, 0))
        text = PIL.Image.new("RGBA", (width + 20, 64), (255, 255, 255, 0))
        draw = PIL.ImageDraw.Draw(text)
        draw.text((0, 9), "New Achievement!", font=font, fill=colour)
        draw.text((0, 29), ach, font=font, fill=(255, 255, 255, 255))
        mid = PIL.Image.alpha_composite(mid, text)

        image = PIL.Image.new("RGBA", (width + 80, 64))
        image.paste(front, (0, 0))
        image.paste(mid, (60, 0))
        return image

    def am_i_a_joke(self, url: str):
        """
        Am I A Joke To You?
        """
        try:
            icon = io.BytesIO(requests.get(url, timeout=10).content)
        except Exception as exc:
            raise Exception("Invalid URL") from exc

        base = PIL.Image.open("assets/amiajoke/joke.jpg")
        background = PIL.Image.new("RGBA", (276, 276), (0, 0, 0))
        image = PIL.Image.open(icon).convert("RGBA")
        face = image.resize((276, 276))
        base.paste(background, (335, 35), background)
        base.paste(face, (335, 35), face)
        return base

    def bad(self, url: str):
        """
        Bad
        """
        try:
            icon = io.BytesIO(requests.get(url, timeout=10).content)
        except Exception as exc:
            raise Exception("Invalid URL") from exc

        base = PIL.Image.open("assets/bad/bad.jpg")
        image = PIL.Image.open(icon).convert("RGBA")
        face = image.resize((128, 128))
        base.paste(face, (50, 215), face)
        return base

    def calling(self, text: str):
        """
        Calling
        """
        final_text = textwrap.fill(text, 33)
        base = PIL.Image.open("assets/calling/template.jpg").convert("RGBA")
        text = PIL.Image.new("RGBA", base.size, (255, 255, 255, 0))
        font = PIL.ImageFont.truetype("assets/_fonts/verdana_edited.ttf", 35)
        canv = PIL.ImageDraw.Draw(text)
        canv.text((5, 5), final_text, font=font, fill="Black")
        out = PIL.Image.alpha_composite(base, text)
        return out

    def captcha(self, text: str):
        """
        Captcha
        """
        front = PIL.Image.open("assets/captcha/start.png")
        txt = PIL.Image.new("RGBA", (len(text) * 15, 189))
        fnt = PIL.ImageFont.truetype("assets/_fonts/Roboto.ttf", 30)
        draw = PIL.ImageDraw.Draw(txt)
        width, _ = draw.textsize(text, font=fnt)
        width = max(450, width)
        mid = PIL.Image.new("RGBA", (width + 201, 189), (255, 255, 255, 0))
        midd = PIL.Image.open("assets/captcha/mid.png")
        end = PIL.Image.open("assets/captcha/end.png")
        for i in range(0, width):
            mid.paste(midd, (i, 0))
        mid.paste(end, (width, 0))
        txt = PIL.Image.new("RGBA", (width + 201, 189), (255, 255, 255, 0))
        draw = PIL.ImageDraw.Draw(txt)
        draw.text((10, 73), text, font=fnt, fill=(0, 0, 0, 255))
        mid = PIL.Image.alpha_composite(mid, txt)
        image = PIL.Image.new("RGBA", (width + 323, 189))
        image.paste(front, (0, 0))
        image.paste(mid, (122, 0))
        return image

    def did_you_mean(self, top: str, bottom: str):
        """
        Did You Mean
        """
        template = PIL.Image.open("assets/didyoumean/bg.png")
        imsize = (1302, 316)
        txt = PIL.Image.new("RGBA", imsize)
        font = PIL.ImageFont.truetype("assets/_fonts/Arial.ttf", 35)
        font_bi = PIL.ImageFont.truetype("assets/_fonts/ArialBI.ttf", 35)
        draw = PIL.ImageDraw.Draw(txt)
        draw.text((45, 41), top.replace("\n", ""), font=font, fill=(0, 0, 0, 255))
        draw.text(
            (295, 250), bottom.replace("\n", ""), font=font_bi, fill=(26, 13, 171, 255)
        )
        draw = PIL.ImageDraw.Draw(txt)
        image = PIL.Image.new("RGBA", imsize)
        image.paste(template, (0, 0))
        image.paste(txt, (0, 0), txt)
        return image

    def drake(self, top: str, bottom: str, ayano: bool = False):
        """
        Drake
        """
        top_text = textwrap.fill(top, 13)
        bottom_text = textwrap.fill(bottom, 13)
        base = PIL.Image.open(
            f"assets/drake/{'template_ayano.jpg' if ayano else 'template.jpg'}"
        ).convert("RGBA")
        text = PIL.Image.new("RGBA", base.size, (255, 255, 255, 0))
        font = PIL.ImageFont.truetype("assets/_fonts/verdana_edited.ttf", 35)
        top_pos = 85 + (-12 * len(top_text.split("\n")) + 10)
        bottom_pos = 335 + (-12 * len(bottom_text.split("\n")) + 10)
        canv = PIL.ImageDraw.Draw(text)
        canv.text((250, top_pos), top_text, font=font, fill="Black")
        canv.text((250, bottom_pos), bottom_text, font=font, fill="Black")
        out = PIL.Image.alpha_composite(base, text)
        return out

    def facts(self, text: str):
        """
        Facts
        """
        final_text = textwrap.fill(text, 22)
        base = PIL.Image.open("assets/facts/template.jpg").convert("RGBA")
        text = PIL.Image.new("RGBA", base.size, (255, 255, 255, 0))
        font = PIL.ImageFont.truetype("assets/_fonts/verdana_edited.ttf", 20)
        canv = PIL.ImageDraw.Draw(text)
        canv.text((65, 400), final_text, font=font, fill="Black")
        text = text.rotate(-15, resample=PIL.Image.BICUBIC)
        out = PIL.Image.alpha_composite(base, text)
        return out

    def _filter(self, face: PIL.Image.Image, filter_type: str, size: tuple):
        width, height = size
        if filter_type == "blur":
            face = face.filter(PIL.ImageFilter.GaussianBlur(radius=2.5))
        elif filter_type == "invert":
            red, green, blue, _ = face.split()
            face = PIL.ImageOps.invert(PIL.Image.merge("RGB", (red, green, blue)))
        elif filter_type == "flip":
            face = face.rotate(180)
        elif filter_type == "mirror":
            face = PIL.ImageOps.mirror(face)
        elif filter_type == "pixelate":
            color_enhanced = PIL.ImageEnhance.Color(face).enhance(1.25)
            contrast_enhanced = PIL.ImageEnhance.Contrast(color_enhanced).enhance(1.2)
            face = contrast_enhanced.convert("P", palette=PIL.Image.ADAPTIVE)
            face = face.resize(
                (face.size[0] // 10, face.size[1] // 10), PIL.Image.BICUBIC
            )
            face = face.resize(face.size, PIL.Image.ANTIALIAS)
        elif filter_type == "jpegify":
            final = io.BytesIO()
            face.convert("RGB").save(final, "JPEG", quality=random.randint(1, 10))
            final.seek(0)
            face = PIL.Image.open(final)
        elif filter_type == "b&w":
            face = face.convert("L")
        elif filter_type == "sepia":
            for pixel_x in range(width):
                for pixel_y in range(height):
                    red, green, blue, alpha = face.getpixel((pixel_x, pixel_y))

                    red = int(0.393 * red + 0.769 * green + 0.189 * blue)
                    green = int(0.349 * red + 0.686 * green + 0.168 * blue)
                    blue = int(0.272 * red + 0.534 * green + 0.131 * blue)

                    red = min(red, 255)
                    blue = min(blue, 255)
                    green = min(green, 255)

                    face.putpixel((pixel_x, pixel_y), (red, green, blue, alpha))
        elif filter_type == "deepfry":
            face = face.convert("RGB")
            face = face.resize(
                (int(width**0.75), int(height**0.75)), resample=PIL.Image.LANCZOS
            )
            face = face.resize(
                (int(width**0.88), int(height**0.88)), resample=PIL.Image.BILINEAR
            )
            face = face.resize(
                (int(width**0.9), int(height**0.9)), resample=PIL.Image.BICUBIC
            )
            face = face.resize((width, height), resample=PIL.Image.BICUBIC)

            red_channel = PIL.ImageOps.posterize(face, 4).split()[0]
            red_channel = PIL.ImageEnhance.Contrast(red_channel).enhance(2.0)
            red_channel = PIL.ImageEnhance.Brightness(red_channel).enhance(1.5)
            red_channel = PIL.ImageOps.colorize(
                red_channel, (254, 0, 2), (255, 255, 15)
            )

            face = PIL.Image.blend(face, red_channel, 0.75)
            face = PIL.ImageEnhance.Sharpness(face).enhance(100.0)
        elif filter_type == "wide":
            face = face.filter(PIL.ImageFilter.GaussianBlur(radius=1.5))
            face = face.resize((int(width * 1.25), int(height / 1.5)))
        else:
            filter_image = PIL.Image.open(self._get_file(f"filter/{filter_type}.png"))
            filter_image = filter_image.resize((width, height))

            face.paste(filter_image, (0, 0), filter_image)
        return face

    def filter(self, url: str, filter_type: str):
        """
        Filter
        """
        try:
            icon = io.BytesIO(requests.get(url, timeout=10).content)
        except Exception as exc:
            raise Exception("Invalid URL") from exc

        image = PIL.Image.open(icon)
        return self._filter(image.convert("RGBA"), filter_type, image.size)

    def floor(self, text: str, image: str):
        """
        Floor
        """
        text = text.replace("\n", "")
        meme_format = PIL.Image.open("assets/floor/floor.png")
        fnt = PIL.ImageFont.truetype("assets/_fonts/Arial.ttf", 30)
        draw = PIL.ImageDraw.Draw(meme_format)
        margin = 20
        offset = 25
        for line in textwrap.wrap(f"The floor is {text}", width=65):
            draw.text((margin, offset), line, font=fnt, fill=(0,) * 3)
            offset += fnt.getsize(line)[1]
        if image:
            try:
                icon = io.BytesIO(requests.get(image, timeout=10).content)
            except Exception as exc:
                raise Exception("Invalid URL") from exc
            image = PIL.Image.open(icon)
            first = image.resize((20, 20))
            second = image.resize((40, 40))
            meme_format.paste(first, (143, 135))
            meme_format.paste(second, (465, 133))
        return meme_format

    def joke_over_head(self, url: str):
        """
        Joke Over Head
        """
        try:
            icon = io.BytesIO(requests.get(url, timeout=10).content)
        except Exception as exc:
            raise Exception("Invalid URL") from exc

        base = PIL.Image.open("assets/joke/thejoke.png")
        back = PIL.Image.new("RGBA", base.size, (0, 0, 0, 0))
        face = PIL.Image.open(icon).convert("RGBA").resize((138, 138))
        background = PIL.Image.new("RGBA", face.size, (0, 0, 0))
        back.paste(background, (127, 125), background)
        back.paste(face, (127, 125), face)
        back.paste(base, (0, 0), base)
        return back

    def trash(self, url: str, url_trash: str) -> PIL.Image.Image:
        """
        Trash
        """
        try:
            icon = io.BytesIO(requests.get(url, timeout=10).content)
            icon_trash = io.BytesIO(requests.get(url_trash, timeout=10).content)
        except Exception as exc:
            raise Exception("Invalid URL") from exc

        avatarsize = 175
        base = PIL.Image.open("assets/trash/image.png")
        hand = PIL.Image.open("assets/trash/hand.png")
        image = PIL.Image.open(icon).convert("RGBA")
        face = image.resize((avatarsize, avatarsize)).rotate(
            5, expand=True, resample=PIL.Image.BICUBIC
        )
        trash_face = PIL.Image.open(icon_trash)
        trash_face = trash_face.convert("RGBA")
        trash_face = trash_face.resize((avatarsize, avatarsize))

        base.paste(face, (375, 80), face)
        base.paste(trash_face, (105, 190), trash_face)
        base.paste(hand, (156, 164), hand)
        return base

    def porn_hub(
        self,
        text: str,
        text2: str,
        iwidth: int = 16,
        height: int = 161,
        padding: int = 10,
        fontsize: int = 164,
    ) -> PIL.Image.Image:
        """
        Porn Hub
        """
        txt = PIL.Image.new("RGBA", (len(text) * 15, height))
        txt2 = PIL.Image.new("RGBA", (len(text2) * 15, height))
        fnt = PIL.ImageFont.truetype("assets/_fonts/ArialB.ttf", fontsize)
        draw = PIL.ImageDraw.Draw(txt)
        width, _ = draw.textsize(text, font=fnt)
        width2, _ = draw.textsize(text2, font=fnt)
        textwindow_size = width + width2 + padding + (iwidth * 2)
        mid = PIL.Image.new("RGBA", (width, height), (255, 255, 255, 0))
        mid2 = PIL.Image.new("RGBA", (width2 + iwidth, height), (255, 255, 255, 0))
        midd_t = PIL.Image.new("RGBA", (1, height), (255, 255, 255, 0))
        start = PIL.Image.open("assets/pornhub/pornstart.png")
        midd = PIL.Image.open("assets/pornhub/pornmid.png")
        end = PIL.Image.open("assets/pornhub/pornend.png")
        for i in range(0, width):
            mid.paste(midd_t, (i, 0))
        for i in range(0, width2):
            mid2.paste(midd, (i, 0))
        mid2.paste(end, (width2, 0))
        txt = PIL.Image.new("RGBA", (textwindow_size, height), (255, 255, 255, 0))
        draw = PIL.ImageDraw.Draw(txt)
        middle_align = -10
        draw.text((0, middle_align), text, font=fnt, fill=(255, 255, 255, 255))
        draw.text(
            (width + iwidth + padding, middle_align),
            text2,
            font=fnt,
            fill=(0, 0, 0, 255),
        )
        image = PIL.Image.new("RGBA", (textwindow_size, height), (255, 255, 255, 0))
        image.paste(mid, (0, 0))
        image.paste(start, (width + padding, 0))
        image.paste(mid2, (width + iwidth + padding, 0))
        image.paste(txt, (0, 0), txt)
        image.paste(txt2, (width + iwidth + padding, 0), txt2)
        return image

    def salty(self, url: str) -> PIL.Image.Image:
        """
        Salty
        """
        try:
            icon = io.BytesIO(requests.get(url, timeout=10).content)
        except Exception as exc:
            raise Exception("Invalid URL") from exc
        salt_size = 100
        base = PIL.Image.new("RGBA", (128, 128 + salt_size))
        image = PIL.Image.open(icon).convert("RGBA")
        face = image.resize((128, 128))
        salt = PIL.Image.open("assets/salty/salt.png")
        salt_re = salt.resize((salt_size, salt_size))
        base.paste(face, (0, salt_size), face)
        base.paste(salt_re, (128 - salt_size, 2), salt_re)
        return base

    def scroll(self, text: str) -> PIL.Image.Image:
        """
        Scroll
        """
        f_text = textwrap.fill(text, 10)
        base = PIL.Image.open("assets/sot/template.jpg").convert("RGBA")
        text = PIL.Image.new("RGBA", base.size, (255, 255, 255, 0))
        font = PIL.ImageFont.truetype("assets/_fonts/verdana_edited.ttf", 15)
        canv = PIL.ImageDraw.Draw(text)
        canv.text((95, 283), f_text, font=font, fill="Black")
        text = text.rotate(2, resample=PIL.Image.BICUBIC)
        return PIL.Image.alpha_composite(base, text)

    def shame(self, url: str) -> PIL.Image.Image:
        """
        Shame
        """
        try:
            icon = io.BytesIO(requests.get(url, timeout=10).content)
        except Exception as exc:
            raise Exception("Invalid URL") from exc

        base = PIL.Image.open("assets/shame/under.png")
        overlay = PIL.Image.open("assets/shame/over.png")

        face = PIL.Image.open(icon)
        face = face.convert("RGBA")
        face = face.resize((240, 240))

        base.paste(face, (680, 530), face)
        base.paste(overlay, (0, 0), overlay)
        return base

    def ship(self, url: str, url2: str) -> PIL.Image.Image:
        """
        Ship
        """
        try:
            icon = io.BytesIO(requests.get(url, timeout=10).content)
            icon2 = io.BytesIO(requests.get(url2, timeout=10).content)
        except Exception as exc:
            raise Exception("Invalid URL") from exc

        base = PIL.Image.new("RGBA", (3 * 128, 128))

        avatar = PIL.Image.open(icon)
        avatar = avatar.convert("RGBA")
        avatar = avatar.resize((128, 128))

        avatar2 = PIL.Image.open(icon2)
        avatar2 = avatar2.convert("RGBA")
        avatar2 = avatar2.resize((128, 128))

        mid = PIL.Image.open("assets/images/heart.png")
        base.paste(avatar, (0, 0))
        base.paste(mid, (128, 0))
        base.paste(avatar2, (256, 0))
        return base

    def what(self, url: str) -> PIL.Image.Image:
        """
        What
        """
        try:
            icon = io.BytesIO(requests.get(url, timeout=10).content)
        except Exception as exc:
            raise Exception("Invalid URL") from exc
        base = PIL.Image.open("assets/what/what.png")
        background = PIL.Image.new("RGBA", base.size, (0, 0, 0, 255))
        image = PIL.Image.open(icon).convert("RGBA")
        face = image.resize((890, 710))
        background.paste(face, (40, 40), face)
        background.paste(base, (0, 0), base)
        return background

    def speechbubble(self, url: str) -> PIL.Image.Image:
        """
        What
        """
        try:
            icon = io.BytesIO(requests.get(url, timeout=10).content)
        except Exception as exc:
            raise Exception("Invalid URL") from exc

        image = PIL.Image.open(icon).convert("RGBA")
        bubble = PIL.Image.open("assets/speechbubble/speechbubble.png")

        bubble = bubble.resize((image.size[0], round(image.size[1] * 0.3)))

        image.paste(bubble, (0, 0), bubble)

        return image
