import os
from typing import List
from PIL import Image
from PIL.ImageFile import ImageFile

from ya_disk import download_folder_from_yandex_disk, logger


def get_folder_paths(base_folder: str) -> List:
    """ Функция которая возвращает список путей с папками с фото. """
    folder_paths = [
        os.path.join(base_folder, folder)
        for folder in os.listdir(base_folder)
        if os.path.isdir(os.path.join(base_folder, folder))
    ]
    return folder_paths


def get_images_from_folder(folder_path: str) -> List[ImageFile]:
    """ Функция которая возвращает список Изображений типа ImageFile. """
    images = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
                img_path = os.path.join(root, file)
                img = Image.open(img_path)
                images.append(img)
    return images


def calculate_collage_size(images: List[ImageFile],
                           images_per_row: int,
                           padding: int,
                           edge_padding_w: int,
                           edge_padding_h: int) -> Image:
    """
    Функция для вычисления размеров коллажа на основе размеров изображений.
    """
    num_images = len(images)
    rows = (num_images + images_per_row - 1) // images_per_row
    cols = min(images_per_row, num_images)

    max_width = max(image.width for image in images)
    max_height = max(image.height for image in images)

    collage_width = cols * (max_width + padding) \
        - padding + 2 * edge_padding_w
    collage_height = rows * (max_height + padding) \
        - padding + 2 * edge_padding_h

    collage_image = Image.new('RGB',
                              (collage_width, collage_height),
                              (255, 255, 255))

    return collage_image


def save_collage(collage_image: Image.Image,
                 output_folder: str,
                 folder_name: str):
    """ Функция для сохранения коллажа в файл. """
    collage_output_filename = \
        os.path.join(output_folder, f"{folder_name}_collage.tif")
    collage_image.save(collage_output_filename)
    logger.info(f"Collage for folder '{folder_name}'"
                f"saved as {collage_output_filename}")


def create_image_collage_for_each_folder(base_folder: str,
                                         output_folder: str,
                                         images_per_row: int = 4,
                                         padding: int = 75,
                                         edge_padding_w: int = 100,
                                         edge_padding_h: int = 200):
    """ Основная функция создания коллажа."""

    folder_paths = get_folder_paths(base_folder)

    for folder_path in folder_paths:
        folder_name = os.path.basename(folder_path)
        images = get_images_from_folder(folder_path)

        if not images:
            logger.error(f"No images found in folder '{folder_name}'")
            continue
        collage_image = calculate_collage_size(
            images, images_per_row, padding, edge_padding_w, edge_padding_h)

        max_width = max(image.width for image in images)
        max_height = max(image.height for image in images)

        for index, image in enumerate(images):
            # Вставка изображений в коллаж
            x = (index % images_per_row) * (max_width + padding) \
                + edge_padding_w
            y = (index // images_per_row) * (max_height + padding) \
                + edge_padding_h
            collage_image.paste(image, (x, y))

        save_collage(collage_image, output_folder, folder_name)


if __name__ == "__main__":
    base_folder = 'image_folders'
    output_folder = 'collage_results'
    yandex_disk_link = "https://disk.yandex.ru/d/V47MEP5hZ3U1kg"
    download_path = "downloaded_files.zip"
    extracted_folder = download_folder_from_yandex_disk(
        yandex_disk_link,
        download_path,
        base_folder)
    if extracted_folder:
        create_image_collage_for_each_folder(
            extracted_folder, output_folder)
    else:
        logger.error("Download failed. Skipping collage creation.")
