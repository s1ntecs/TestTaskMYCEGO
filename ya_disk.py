import requests
import zipfile
import os
from loguru import logger
import urllib


BASE_URL = "https://cloud-api.yandex.net/v1/disk/public/resources/download"


def extract_zip(file_path: str,
                extract_to: str,
                folder_name):
    """ Функция разархивирует папки."""
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logger.info(f"Extracted to {extract_to}")
    except zipfile.BadZipFile:
        logger.error(f"Failed to extract zip file {file_path}")
        return False
    finally:
        os.remove(file_path)
    # extracted_folder = os.path.join(extract_to, os.listdir(extract_to)[0])
    return f"{extract_to}/{folder_name}"


def get_foler_name(url: str):
    """ Функция возвращает название скачанной папки."""
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    encoded_filename = query_params.get('filename', [None])[0]
    decoded_filename = urllib.parse.unquote(encoded_filename)
    filename_without_extension = decoded_filename.rsplit('.', 1)[0]
    return filename_without_extension


def download_folder_from_yandex_disk(public_url: str,
                                     save_path: str,
                                     extract_to: str) -> bool:
    """ Функция скачивания папки из яндекс диска."""
    try:
        response = requests.get(BASE_URL, params={"public_key": public_url})
        response.raise_for_status()
        print(response.json())

        download_url = response.json().get("href")
        if download_url:
            download_response = requests.get(download_url)
            with open(save_path, 'wb') as file:
                file.write(download_response.content)
            logger.info(f"File saved to {save_path}")
            zipped_folder_name = get_foler_name(download_url)
            extracted_folder = extract_zip(save_path,
                                           extract_to,
                                           zipped_folder_name)
            return extracted_folder
        else:
            logger.error("Failed to get download URL")
            return False
    except requests.RequestException as e:
        logger.error(f"Error during downloading: {e}")
        return False
