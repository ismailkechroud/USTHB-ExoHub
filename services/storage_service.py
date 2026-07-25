# .venv
from aiogram import types

# Library (defult)
import os
import uuid


# storages
from storage.database.supabase_client import (
    supabase
)








################# tmp Storage (StorageTmpError) #################

TEMP_DIR = "storage/tmp"


async def download_pdf_from_telegram_tmp(msg: types.Message) -> dict:

    document = msg.document


    # 1. create folder
    os.makedirs(TEMP_DIR, exist_ok=True)


    # 2. get file from telegram
    telegram_file = await msg.bot.get_file(document.file_id)
    telegram_path = telegram_file.file_path

    
    # 3. generate unique name
    pdf_name_file = f"{uuid.uuid4()}"
    destination = f"{TEMP_DIR}/{pdf_name_file}.pdf"
    

    # 4. download file
    await msg.bot.download_file(
        telegram_path,
        destination
    )
   

    # 5. return path
    return {
        "path": destination,
        "file_name": pdf_name_file
    }


async def download_img_from_telegram_tmp(msg: types.Message) -> str:
    os.makedirs(TEMP_DIR, exist_ok=True)

    if msg.document:
        file = await msg.bot.get_file(msg.document.file_id)

    else:
        file = await msg.bot.get_file(msg.photo[-1].file_id)
  
    filename = f"{uuid.uuid4()}.jpg"
    destination = f"{TEMP_DIR}/{filename}"


    await msg.bot.download_file(
        file.file_path,
        destination=destination
    )


    return destination





def save_imgs_tmp(images, name_folder) -> list:

    os.makedirs(TEMP_DIR, exist_ok=True)

    FOLDER_DIR = f"{TEMP_DIR}/{name_folder}"

    os.makedirs(FOLDER_DIR, exist_ok=True)

    paths = []

    for i, img in enumerate(images, 1):
        path = os.path.join(FOLDER_DIR, f"img_{i}.png")

        img.save(
            path,
            format="PNG",
            optimize=True
        )
        

        paths.append(path)

    
    return paths



def delete_file_tmp(file_path):
    
    if os.path.exists(file_path):
        os.remove(file_path)
    







################# DataBase Storage (StorageDataBaseError) #################

async def get_data_table_DB(table_name: str, filter_by_column: dict=None) -> list:
    
    query = supabase.table(table_name).select("*")

    if filter_by_column:
        for column, value in filter_by_column.items():
            if value is not None:
                query = query.eq(column, value)

    response = query.execute()

    return response.data or []

    
async def set_data_table_DB(table_name: str, data) -> dict:
    
    response = (
        supabase
        .table(table_name)
        .insert(data)
        .execute()
    )

    if not response.data:
        print(f"Failed to insert data into '{table_name}'")
        return {}

    return response.data[0]


async def update_data_table_DB(table_name: str, data: dict, filter_by_column: dict = None,) -> dict | None:

    query = supabase.table(table_name).update(data)

    if filter_by_column:
        for column, value in filter_by_column.items():
            if value is not None:
                query = query.eq(column, value)

    response = query.execute()

    return response.data[0] if response.data else None


async def delete_data_table_DB(table_name: str, filter_by_column: dict = None) -> bool:

    query = supabase.table(table_name).delete()

    if filter_by_column:
        for column, value in filter_by_column.items():
            if value is not None:
                query = query.eq(column, value)

    response = query.execute()

    return bool(response.data)





async def import_images(exercise_imgs):
    image_urls = []

    for img in exercise_imgs:
        res = supabase.storage \
            .from_("exercise-images") \
            .create_signed_url(img["image_url"], 3600)

        url = res.get("signedURL") or res.get("signed_url")

        if url:
            image_urls.append(url)

    return image_urls

    

async def upload_images(name_folder: str, exercise_id: int):
    
    folder_path = f"{TEMP_DIR}/{name_folder}"

    uploaded = []

    for file_name in os.listdir(folder_path):

        file_path = os.path.join(folder_path, file_name)

        if not os.path.isfile(file_path):
            continue

        storage_path = f"exercises/{exercise_id}/{file_name}"

        with open(file_path, "rb") as f:

            supabase.storage.from_("exercise-images").upload(
                path=storage_path,
                file=f,
                file_options={
                    "content-type": "image/png",
                    "upsert": False
                }
            )

        uploaded.append(storage_path)

    return uploaded



