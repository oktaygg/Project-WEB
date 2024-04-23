import random
import requests
import os
import sys
import pygame


def isresponse(res):
    if not res:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)


def search(towngg):
    geocoder_request = (f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0"
                        f"493-4b70-98ba-98533de7710b&geocode={towngg}&format=json")
    response = requests.get(geocoder_request)
    isresponse(response)
    json_response = response.json()

    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    return ','.join(toponym_coodrinates.split(' '))


with open('goroda.txt', encoding='utf-8') as txt:
    TOWNS = txt.readlines()

town = random.choice(TOWNS)[:-1]

cords = search(town)

map_request = f"http://static-maps.yandex.ru/1.x/?ll={cords}&spn=0.05,0.05&l=sat"
response = requests.get(map_request)
isresponse(requests.get(map_request))

map_file = "map.png"
with open(map_file, "wb") as file:
    file.write(response.content)

pygame.init()
screen = pygame.display.set_mode((600, 450))
screen.blit(pygame.image.load(map_file), (0, 0))
pygame.display.flip()
while pygame.event.wait().type != pygame.QUIT:
    pass
pygame.quit()
os.remove(map_file)

inputtown = input()
try:
    cords2 = search(inputtown)
    print(f'Вы угадали город - {town}' if cords2 == cords else f'Вы не угадали город {town}, выбрав - {inputtown}')
except Exception:
    print(f'Вы ввели несуществующий город! Правильный ответ - {town}')
