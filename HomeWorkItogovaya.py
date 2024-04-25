import requests
import json
import os
from yadisk import YaDisk
import datetime

# Получение id пользователя VK от пользователя
user_id = input("Введите id пользователя VK: ")

# Получение токена Яндекс.Диска от пользователя
yadisk_token = input("Введите токен Яндекс.Диска: ")

# Получение фотографий с профиля
def get_photos(user_id, access_token):
    params = {
        'owner_id': user_id,
        'access_token': access_token,
        'v': '5.131',  # Версия API
        'album_id': 'profile',
        'extended': 1,  # Запрос расширенной информации о фотографиях
        'photo_sizes': 1  # Получение доступных размеров фотографий
    }
    response = requests.get('https://api.vk.com/method/photos.get', params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            if 'response' in data:
                photos_data = data['response']['items']
                return photos_data
            else:
                print("Ответ не содержит ключа 'response':")
                print(data)
        except ValueError:
            print("Не удалось обработать JSON-ответ")
    else:
        print(f"Запрос завершился с ошибкой. Код статуса: {response.status_code}")

    return None


def generate_unique_filename(base_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    unique_name = f"{timestamp}_{base_name}"
    return unique_name


# Сохранение фотографий максимального размера на Я.Диске
def save_photos_to_yadisk(photos, yadisk_token):
    if photos is not None:
        y = YaDisk(token=yadisk_token)
        y.mkdir('/photos')  # Создание папки для фотографий

        for photo in photos:
            if 'sizes' in photo:
                # Получение URL фотографии
                photo_url = photo['sizes'][-1]['url']

                if 'likes' in photo and 'count' in photo['likes']:
                    likes_count = photo['likes']['count']
                    file_name = generate_unique_filename(f"{likes_count}.jpg")

                    # Загрузка фотографии на Я.Диск
                    response = requests.get(photo_url)
                    if response.status_code == 200:
                        with open(file_name, 'wb') as f:
                            f.write(response.content)
                        with open(file_name, 'rb') as f:
                            y.upload(f, f'/photos/{file_name}')  # Загрузка фотографии на Я.Диск
                            # Сохранение информации по фотографиям в JSON-файл
                            with open('photos_info.json', 'a') as json_file:
                                json.dump({'file_name': file_name, 'size': 'max'}, json_file)
                                json_file.write('\n')
                    else:
                        print(f"Не удалось загрузить фотографию: {photo_url}")
            else:
                print("Не удалось найти размеры фотографии.")
    else:
        print("Данные о фотографиях отсутствуют. Невозможно сохранить на Я.Диск.")

# Информация о файле
file_info = [{
    "file_name": "34.jpg",
    "size": "z"
}]

# Запись информации в JSON-файл
with open('file_info.json', 'w') as json_file:
    json.dump(file_info, json_file)

# Проверка существования файла
if os.path.exists('file_info.json'):
    print("JSON-файл успешно создан.")
else:
    print("Ошибка при создании JSON-файла.")

# Данные
user_id = 'add_you_id'
access_token = 'add_you_token'
yadisk_token = 'add_you_token'

photos_data = get_photos(user_id, access_token)
save_photos_to_yadisk(photos_data, yadisk_token)
