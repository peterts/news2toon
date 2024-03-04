from dotenv import load_dotenv
from newspaper import Article
from openai import AzureOpenAI, AsyncAzureOpenAI
import os
import warnings
import asyncio

from news2toon.constants import (
    ASSETS_DIR_PATH,
    RESULTS_DIR_PATH,
    INTERMEDIATE_JSON_NAME,
    FINAL_JSON_NAME,
)
from news2toon.result_models import CartoonStripCell, CartoonStrip
from news2toon.utils import convert_to_alphanumeric

load_dotenv()

AZURE_OPENAI_CLIENT = AzureOpenAI(
    api_version="2023-12-01-preview",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)
ASYNC_AZURE_OPENAI_CLIENT = AsyncAzureOpenAI(
    api_version="2023-12-01-preview",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)


def generate_cartoon_strip(url: str) -> CartoonStrip:
    cartoon_strip = _get_cartoon_strip_with_image_descriptions(url)
    return _add_image_urls(cartoon_strip, url)


def _get_cartoon_strip_with_image_descriptions(news_article_url: str) -> CartoonStrip:
    url_hash = convert_to_alphanumeric(news_article_url)
    intermediate_json_path = RESULTS_DIR_PATH / INTERMEDIATE_JSON_NAME.format(
        hash=url_hash
    )

    if intermediate_json_path.is_file():
        print("Loading cartoon strip JSON from file")
        return CartoonStrip.model_validate_json(intermediate_json_path.read_text())

    cartoon_strip = _generate_cartoon_strip_with_image_descriptions(news_article_url)

    intermediate_json_path.write_text(
        cartoon_strip.model_dump_json(indent=4, by_alias=True)
    )
    return cartoon_strip


def _generate_cartoon_strip_with_image_descriptions(
    news_article_url: str,
) -> CartoonStrip:
    news_article_text = _get_news_article_text(news_article_url)
    prompt = _create_prompt_including_news_article(news_article_text)
    cartoon_strip_json_str = _run_prompt_with_chatgpt(prompt)
    cartoon_strip = _validate_cartoon_strip_json_str(cartoon_strip_json_str)
    return cartoon_strip


def _add_image_urls(cartoon_strip: CartoonStrip, news_article_url: str) -> CartoonStrip:
    url_hash = convert_to_alphanumeric(news_article_url)
    final_json_path = RESULTS_DIR_PATH / FINAL_JSON_NAME.format(hash=url_hash)

    if final_json_path.is_file():
        print("Loading cartoon strip JSON with images from file")
        return CartoonStrip.model_validate_json(final_json_path.read_text())

    cartoon_strip = asyncio.run(_generate_images_with_dalle(cartoon_strip))
    final_json_path.write_text(cartoon_strip.model_dump_json(indent=4, by_alias=True))
    return cartoon_strip


def _validate_cartoon_strip_json_str(cartoon_strip_json_str: str) -> CartoonStrip:
    return CartoonStrip.model_validate_json(cartoon_strip_json_str)


def _run_prompt_with_chatgpt(prompt: str) -> str:
    print("Running prompt with ChatGPT")
    response = AZURE_OPENAI_CLIENT.chat.completions.create(
        model=os.environ["CHATGPT_MODEL_NAME"],
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


async def _generate_images_with_dalle(
    cartoon_strip: CartoonStrip,
) -> CartoonStrip:
    tasks = [_generate_image_with_dalle(cell) for cell in cartoon_strip.cells]
    cells = await asyncio.gather(*tasks)
    return cartoon_strip.model_copy(update=dict(cells=cells))


async def _generate_image_with_dalle(cell: CartoonStripCell) -> CartoonStripCell:
    print("Generating image with Dall-E")
    response = await ASYNC_AZURE_OPENAI_CLIENT.images.generate(
        model=os.environ["DALLE_MODEL_NAME"], prompt=cell.image_description, n=1
    )
    return cell.model_copy(update=dict(image_url=response.data[0].url))


def _get_news_article_text(url: str) -> str:
    print("Reading news article from url")
    article = Article(url)
    article.download()
    with warnings.catch_warnings(action="ignore"):
        article.parse()
    return article.text


def _create_prompt_including_news_article(news_article_text: str) -> str:
    prompt = (ASSETS_DIR_PATH / "prompt.txt").read_text()
    return prompt + news_article_text.rstrip() + "\n\n===\n\nOutput:"
