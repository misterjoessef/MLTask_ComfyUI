from PIL import Image, ImageDraw, ImageFont
import os
import io
from datetime import datetime
import textwrap
import string
from Common.Utils import (
    get_system_font_files,
    images_data_to_tensor,
)


def get_default_font():
    try:
        return ImageFont.load_default()
    except IOError:
        possible_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "/Library/Fonts/Arial.ttf",  # macOS
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
        ]
        for font_path in possible_fonts:
            if os.path.exists(font_path):
                return font_path
        raise IOError("No usable default font found.")


def create_text_image(
    text,
    width,
    height,
    font,
    font_size=None,
    text_color="white",
    bg_color="black",
    offset_x=0,
    offset_y=0,
):
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        if isinstance(font, str):
            font = ImageFont.truetype(font, font_size or 20)
        elif font_size:
            font = font.font_variant(size=font_size)

        # Calculate the average character width
        avg_char_width = (
            sum(font.getbbox(char)[2] for char in string.ascii_lowercase) / 26
        )

        # Calculate the maximum characters per line
        max_char_count = int(width / avg_char_width)

        # Wrap the text
        lines = textwrap.wrap(text, width=max_char_count)

        # Calculate total text height
        line_height = font.getbbox("hg")[3] - font.getbbox("hg")[1]
        text_height = len(lines) * line_height

        # Calculate starting Y position to center the text block
        y = offset_y + (height - text_height) / 2

        for line in lines:
            # Get line width
            line_width = font.getbbox(line)[2]

            # Calculate starting X position to center this line
            x = offset_x + (width - line_width) / 2

            # Draw the line
            draw.text((x, y), line, font=font, fill=text_color)

            # Move to next line
            y += line_height

    except Exception as e:
        print(f"Error creating image: {str(e)}")
        return None

    return img


def create_text_image_pil(
    text,
    width,
    height,
    font,
    font_size=None,
    text_color="white",
    bg_color="black",
    offset_x=0,
    offset_y=0,
):
    img = create_text_image(
        text, width, height, font, font_size, text_color, bg_color, offset_x, offset_y
    )
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return Image.open(img_byte_arr)


class MLTaskUtilsTextImageGenerator:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "text here",
                    },
                ),
            },
            "optional": {
                "width": (
                    "INT",
                    {
                        "default": 512,
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": 512,
                    },
                ),
                "font_size": (
                    "INT",
                    {
                        "default": 100,
                    },
                ),
                # TODO move this to a widget
                "font_name": (sorted(get_system_font_files()),),
                "offset_x": (
                    "INT",
                    {
                        "default": 0,
                    },
                ),
                "offset_y": (
                    "INT",
                    {
                        "default": 0,
                    },
                ),
                # TODO color widget
                # "text_color": (
                #     "INT",
                #     {
                #         "default": 0,
                #         "min": 0,
                #         "max": 0xFFFFFF,
                #         "step": 1,
                #         "display": "color",
                #     },
                # ),
                # "bg_color": (
                #     "INT",
                #     {
                #         "default": 0,
                #         "min": 0,
                #         "max": 0x000000,
                #         "step": 1,
                #         "display": "color",
                #     },
                # ),
            },
        }

    OUTPUT_NODE = True
    FUNCTION = "generate_text_image"
    CATEGORY = "MLTask/SocialMan/Utils"
    RETURN_TYPES = (
        "IMAGE",
        "MASK",
        "IMAGE",
        "MASK",
    )
    RETURN_NAMES = (
        "text_image",
        "text_image_mask",
        "text_image_inverted",
        "text_image_mask_inverted",
    )

    def generate_text_image(
        self, text, width, height, font_size, font_name, offset_x, offset_y
    ):

        # font = get_default_font() if args.font_path is None else args.font_path
        font = font_name  # "Arial Rounded Bold.ttf"
        text_color = "black"
        bg_color = "white"
        img = create_text_image_pil(
            text,
            width,
            height,
            font,
            font_size,
            text_color,
            bg_color,
            offset_x,
            offset_y,
        )
        # INVERTED
        text_color = "white"
        bg_color = "black"
        img_inverted = create_text_image_pil(
            text,
            width,
            height,
            font,
            font_size,
            text_color,
            bg_color,
            offset_x,
            offset_y,
        )
        if img:
            # script_dir = os.path.dirname(os.path.abspath(__file__))
            # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # file_name = f"text_image_{timestamp}.png"
            # # file_path = os.path.join(script_dir, file_name)
            # file_path = f"{folder_paths.get_output_directory()}/{file_name}"
            # img.save(file_path)
            # print(f"Image saved as {file_path}")
            # return images_file_to_tensor(file_path)

            return images_data_to_tensor(img) + images_data_to_tensor(img_inverted)
        else:
            print("Failed to create image.")
