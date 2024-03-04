from pathlib import Path

from PIL import ImageFont

ASSETS_DIR_PATH = Path(__file__).parent / "assets"
RESULTS_DIR_PATH = Path(__file__).parents[1] / "results"
INTERMEDIATE_JSON_NAME = "intermediate-{hash}.json"
FINAL_JSON_NAME = "final-{hash}.json"
IMAGE_FILE_NAME = "image-{hash}.png"
IMAGE_SIZE = 300
BORDER = 10
IMAGE_SIZE_WITHOUT_BORDER = IMAGE_SIZE - 2 * BORDER
OUTLINE_WIDTH = 3
FONT_SIZE = 14
TITLE_FONT_SIZE = 32
FONTS_PATH = ASSETS_DIR_PATH / "fonts"
NORMAL_FONT = ImageFont.truetype(str(FONTS_PATH / "comic-book.otf"), FONT_SIZE)
ITALIC_FONT = ImageFont.truetype(str(FONTS_PATH / "comic-book-italic.otf"), FONT_SIZE)
BOLD_FONT = ImageFont.truetype(str(FONTS_PATH / "comic-book-bold.otf"), FONT_SIZE)
TITLE_FONT = ImageFont.truetype(str(FONTS_PATH / "komikax.ttf"), TITLE_FONT_SIZE)
