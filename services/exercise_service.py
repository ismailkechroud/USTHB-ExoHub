
# Library (defult)
import re
import unicodedata
import os
import io

# config bot
from config_bot import CHANNEL_ID

# Library (.venv)
from pdfminer.high_level import extract_text
from rapidfuzz import fuzz
from aiogram.types import InputMediaPhoto, Message, FSInputFile

import fitz
from PIL import Image
import numpy as np


# services
from services.storage_service import (
    import_images,
    get_data_table_DB
)

# navigation
from navigation.screens import show_solutions

# keyboards
from keyboards.inlinekeyboard import (
    exercise_yes_no_keyboard
)




################# Extract Text from PDF #################

def extract_text_PDF(file_path):

    full_text = ""

    full_text = extract_text(file_path)

    return full_text




################# Normalization Text #################

def normalize_text_PDF(full_text):

    # 1. lowercase
    text = full_text.lower()

    # 2. remove accents (é → e, à → a, ...)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")

    # 3. replace everything except letters/numbers with space
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # 4. convert multiple spaces → single space
    text = re.sub(r"\s+", " ", text)

    # 5. trim spaces
    text = text.strip()

    return text



################# Similarity Text #################

def similarity_score(text1: str, text2: str) -> float:
    return fuzz.token_set_ratio(text1, text2)




################# show exo imgs #################

async def show_exo_imgs_to_user(msg: Message, id_exo):

    exercise_images_table = await get_data_table_DB(
        "exercise_images",
        {"exercise_id": id_exo}
    )

    exercise_images_table = sorted(
        exercise_images_table,
        key=lambda x: x["image_order"]
    )

    image_urls = await import_images(exercise_images_table)


    if not image_urls:
        await msg.answer("❌ No images found")
        return

    # print(image_urls)
    
    # إرسال على دفعات من 10
    for i in range(0, len(image_urls), 10):


        chunk = image_urls[i:i + 10]

        media = [
            InputMediaPhoto(media=url)
            for url in chunk
        ]

        # print(media)
        await msg.answer_media_group(media=media)



################# show Solution of Exo #################

async def show_solutions_of_exo_to_user(msg: Message, id_exo):

    solutions_table = await get_data_table_DB(
        "solutions",
        {"exercise_id": id_exo}
    )
    
    telegram_post_links = []
    for solution in solutions_table:
        telegram_post_links.append(solution["telegram_post_link"])

    # 5) send inline keyboard with solutions
    await show_solutions(msg, telegram_post_links, id_exo)




################# get exercises of module #################

async def get_exercises_of_module(language: str, year: str, specialty: str, module: str) -> dict[str, dict]:

    # 1) module id
    modules = await get_data_table_DB(
        "modules",
        {
            "year": year,
            "specialty": specialty,
            "module_name": module,
        },
    )

    if not modules:
        return {}

    module_id = modules[0]["id"]

    # 2) exercise ids
    module_exercises = await get_data_table_DB(
        "module_exercises",
        {"module_id": module_id},
    )

    exercise_ids = {
        row["exercise_id"]
        for row in module_exercises
    }

    if not exercise_ids:
        return {}

    # 3) exercises
    exercises = await get_data_table_DB(
        "exercises",
        {"language": language},
    )
    exercises.sort(key=lambda exo: exo["id"])

    # 4) build dict
    result = {}
    num = 1

    for exo in exercises:
        if exo["id"] in exercise_ids:
            result[str(num)] = {
                "id": exo["id"],
                "normalized_text": exo["normalized_text"]
            }
            num += 1

    return result




################# confirmation[yes][no] #################

async def comfirmation_exo(message, candidate):
    await message.answer(
        "🤔 هل هذا هو التمرين الذي تبحث عنه؟",
        reply_markup=exercise_yes_no_keyboard(candidate["id"])
    )




################# Convert PDF to Images #################

async def convert_pdf_to_imgs(msg, pdf_path):

    async def crop_white_margins(msg, image: Image.Image):

        img = image.convert("L")  # Grayscale

        arr = np.array(img)

        binary = arr < 250

        rows = np.where(binary.any(axis=1))[0]
        cols = np.where(binary.any(axis=0))[0]

        if len(rows) == 0 or len(cols) == 0:
            await msg.answer("No content found in image")
            return image

        top, bottom = rows[0], rows[-1]
        left, right = cols[0], cols[-1]

        pad = 50

        top = max(0, top - pad)
        bottom = min(arr.shape[0], bottom + pad)
        left = max(0, left - pad)
        right = min(arr.shape[1], right + pad)

        return image.crop((left, top, right, bottom))


    doc = fitz.open(pdf_path)

    results = []

    try:
        for page in doc:

            # Render page إلى صورة
            pix = page.get_pixmap(dpi=200)

            # تحويلها إلى PIL Image
            mode = "RGB" if pix.alpha == 0 else "RGBA"

            image = Image.frombytes(
                mode,
                (pix.width, pix.height),
                pix.samples
            )

            clean_img = await crop_white_margins(msg, image)

            results.append(clean_img)

    finally:
        doc.close()

    return results

################# send solution to channel #################

BATCH_SIZE = 10

async def send_solution_to_channel(msg, paths: list[str], caption: str) -> str:

    message = await msg.bot.send_message(
        chat_id=CHANNEL_ID,
        text=caption
    )

    for start in range(0, len(paths), BATCH_SIZE):
        batch = paths[start:start + BATCH_SIZE]

        media = [
            InputMediaPhoto(media=FSInputFile(path))
            for path in batch
        ]

        await msg.bot.send_media_group(
            chat_id=CHANNEL_ID,
            media=media
        )

    chat = await msg.bot.get_chat(CHANNEL_ID)

    return f"https://t.me/{chat.username}/{message.message_id}"