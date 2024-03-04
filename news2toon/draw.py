from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap
from math import ceil

from news2toon.constants import (
    IMAGE_SIZE,
    BORDER,
    IMAGE_SIZE_WITHOUT_BORDER,
    OUTLINE_WIDTH,
    NORMAL_FONT,
    ITALIC_FONT,
    BOLD_FONT,
    TITLE_FONT,
)
from news2toon.result_models import SpeechBubble, CartoonStripCell, CartoonStrip


def draw_cartoon_strip(cartoon_strip: CartoonStrip):
    images = [_get_image_from_url(cell.image_url) for cell in cartoon_strip.cells]

    text_boxes_drawings = _get_text_boxes_drawings(cartoon_strip.cells)
    text_boxes_height = _get_text_boxes_height(text_boxes_drawings)

    title = _draw_title(cartoon_strip.title)

    n_images = len(images)
    width = IMAGE_SIZE * n_images - (n_images - 1) * BORDER
    height = title.height + IMAGE_SIZE + text_boxes_height
    final_image = Image.new("RGB", (width, height), color="white")

    final_image.paste(title, (0, 0))

    for i in range(n_images):
        x = i * IMAGE_SIZE - i * BORDER

        cell = _add_black_outline_and_white_border(
            images[i], IMAGE_SIZE, OUTLINE_WIDTH, BORDER
        )
        final_image.paste(cell, (x, title.height))

        y = IMAGE_SIZE + title.height
        for text_box_drawing in text_boxes_drawings[i]:
            final_image.paste(text_box_drawing, (x, y))
            y += text_box_drawing.height

    return final_image


def _draw_title(title_text: str):
    height = _get_text_height(title_text, TITLE_FONT) + 2 * BORDER
    width = _get_text_width(title_text, TITLE_FONT) + 2 * BORDER
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.text((BORDER, BORDER), title_text, font=TITLE_FONT, fill="black", align="left")
    return image


def _get_text_boxes_drawings(cells: list[CartoonStripCell]):
    return [
        [_draw_text_box(speech_bubble) for speech_bubble in cell.speech_bubbles]
        for cell in cells
    ]


def _draw_text_box(speech_bubble: SpeechBubble):
    font = ITALIC_FONT if speech_bubble.is_narrator else NORMAL_FONT

    full_text = _get_wrapped_text(speech_bubble.full_text, font)
    line_height = _get_text_height(full_text, font)
    height = _get_n_lines(full_text) * line_height

    image = Image.new("RGB", (IMAGE_SIZE, height + 2 * BORDER), "white")
    draw = ImageDraw.Draw(image)

    if not speech_bubble.is_narrator:
        draw.text(
            (BORDER, BORDER),
            speech_bubble.person_prefix,
            fill="black",
            font=BOLD_FONT,
            align="left",
        )
        person_text_width = _get_text_width(speech_bubble.person_prefix, BOLD_FONT) + 5
    else:
        person_text_width = 0

    x, y = BORDER + person_text_width, BORDER
    for line in speech_bubble.remove_person_prefix(full_text).split("\n"):
        draw.text((x, y), line, fill="black", font=font, align="left")
        x = BORDER
        y += line_height

    return image


def _get_wrapped_text(text: str, font: ImageFont) -> str:
    full_width = font.getlength(text)
    if full_width < IMAGE_SIZE_WITHOUT_BORDER:
        return text

    max_number_of_lines = ceil(full_width / IMAGE_SIZE_WITHOUT_BORDER)
    wrap_width = len(text) // max_number_of_lines
    while _get_max_text_width(text, font, wrap_width) < IMAGE_SIZE_WITHOUT_BORDER:
        wrap_width += 1

    return textwrap.fill(text, wrap_width - 1)


def _get_max_text_width(text: str, font: ImageFont, wrap_width: int) -> int:
    lines = textwrap.wrap(text, wrap_width)
    return max(_get_text_width(line, font) for line in lines)


def _get_text_width(text: str, font: ImageFont) -> int:
    return font.getmask(text).getbbox()[2]


def _get_text_height(text: str, font: ImageFont) -> int:
    _, descent = font.getmetrics()
    return font.getmask(text).getbbox()[3] + descent


def _get_n_lines(text: str) -> int:
    return text.count("\n") + 1


def _get_image_from_url(image_url: str) -> Image:
    response = requests.get(image_url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))


def _add_black_outline_and_white_border(
    image: Image, total_size: int, outline_width: int, border: int
) -> Image:
    image_size = total_size - 2 * outline_width - 2 * border
    image = image.resize((image_size, image_size))

    image_with_outline_size = total_size - 2 * border
    image_with_outline = Image.new(
        "RGB", (image_with_outline_size, image_with_outline_size)
    )
    image_with_outline.paste(image, (outline_width, outline_width))

    image_with_outline_and_border = Image.new(
        "RGB", (total_size, total_size), color="white"
    )
    image_with_outline_and_border.paste(image_with_outline, (border, border))

    return image_with_outline_and_border


def _get_text_boxes_height(text_boxes_drawings: list[list[Image]]) -> int:
    return max(sum(image.height for image in cell) for cell in text_boxes_drawings)
