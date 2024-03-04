from news2toon.content_generator import generate_cartoon_strip
from news2toon.draw import draw_cartoon_strip
from news2toon.constants import IMAGE_FILE_NAME, RESULTS_DIR_PATH
from news2toon.utils import convert_to_alphanumeric


if __name__ == "__main__":
    url = input("Url: ")

    if not RESULTS_DIR_PATH.is_dir():
        RESULTS_DIR_PATH.mkdir()

    cartoon_strip = generate_cartoon_strip(url)
    image = draw_cartoon_strip(cartoon_strip)

    url_hash = convert_to_alphanumeric(url)
    image_path = RESULTS_DIR_PATH / IMAGE_FILE_NAME.format(hash=url_hash)
    image.save(image_path)

    image.show()
