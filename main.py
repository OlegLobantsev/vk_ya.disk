import requests
import datetime
import json
import time
import sys
from tqdm import tqdm

with open('tokenVK.txt', 'r') as file_object:
    token_vk = file_object.read().strip()

with open('tokenYA.txt', 'r') as file_object:
    token_ya = file_object.read().strip()


class Vk:

    def __init__(self, token, user_id_):
        self.url = 'https://api.vk.com/method/'
        self.params = {'access_token': token, 'v': '5.131'}
        self.user_id_ = user_id_

    def get_user(self):
        user_url = self.url+'users.get'
        user_params = {'user_ids': self.user_id_}
        user = requests.get(user_url, params={**self.params, **user_params}).json()
        if user.get('error') is None:
            if len(user['response']) != 0:
                user_id = user['response'][0]['id']
            else:
                print(f'\n\033[31m Пользователь "{self.user_id_}" не существует!\033[0m')
                sys.exit()
        else:
            print(f'\n\033[31m Некорректный ввод!\033[0m')
            sys.exit()
        return user_id

    def get_photos(self):
        user_id = self.get_user()
        get_photo_url = self.url+'photos.get'
        get_photo_params = {'user_id': user_id, 'extended': '1',
                            'album_id': 'profile', 'count': count, 'photo_sizes': '1'}
        req = requests.get(get_photo_url, params={**self.params, **get_photo_params}).json()
        return req['response']['items']

    def get_name_file(self):
        l_photos = []
        list_photos = []
        like = []
        photos = self.get_photos()
        for photo in photos:
            p_data = (datetime.datetime.fromtimestamp(photo['date'])).strftime('%d-%m-%Y')
            p_likes = photo['likes']['count']
            p_url = photo['sizes'][len(photo['sizes'])-1]['url']
            p_size = photo['sizes'][len(photo['sizes'])-1]['type']
            if p_likes not in like:
                l_photos.append({'Name': str(p_likes)+'.jpg', 'Likes': str(p_likes), 'Date': p_data, 'Url': p_url,
                                 'Size type': p_size})
                list_photos.append({"file_name": str(p_likes)+'.jpg', "size": p_size})
            else:
                l_photos.append(
                    {'Name': str(p_likes)+"_"+p_data+'.jpg', 'Likes': str(p_likes), 'Date': p_data, 'Url': p_url,
                     'Size type': p_size})
                list_photos.append({"file_name": str(p_likes)+"_"+p_data+'.jpg', "size": p_size})
            like.append(p_likes)

            with open('log.json', 'w') as f:
                json.dump(list_photos, f, indent=2, ensure_ascii=False)
        return l_photos


class YandexDisk:

    def __init__(self, token, folder):
        self.folder = folder
        self.url = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
                        'Authorization': 'OAuth '+token}

    def create_folder(self, folder):
        requests.put(self.url, headers=self.headers, params={'path': f"/{self.folder}"})
        return

    def upload_to_ya(self):
        self.create_folder(self.folder)
        name_list = []
        vk_list = vk.get_name_file()
        for photo in tqdm(vk_list, desc='Загрузка', unit='photo', colour='green'):
            time.sleep(1)
            name = str(photo['Name'])
            name_list.append(name)
            requests.post(self.url+'/upload', headers=self.headers,
                          params={'url': photo['Url'], 'path': f"/{self.folder}/"+name})
        print(f'\n\033[32m Загружено {len(vk_list)} фото\033[0m')
        return


if __name__ == '__main__':
    user = input("Введите id или username: ")
    count = int(input("Введите количество фотографий для копирования: "))
    dir_ya = input("Введите имя каталога для Яндекс.Диск: ")

    vk = Vk(token_vk, user)
    ya = YandexDisk(token_ya, dir_ya)
    ya.upload_to_ya()
