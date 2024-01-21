from PIL import Image
import requests

robot_name = "superbot"
request_params = {
    "set": "set4",
    "size": "256x256",
    "bgset": "bg1"
}
res = requests.get(
    f'https://robohash.org/{robot_name}',
    stream=True,
    params=request_params
#    f'https://robohash.org/{robot_name}?set=set3', # вместо параметров меняем ссылку
#    stream=True,
)
#image = Image.open(res.raw)
#image.show()
Image.open(res.raw).show()

# робоХэш через обертки
from RoboHashAPI import RoboHash

api = RoboHash()
image = api.get_image("superbot", set=4)
image.show()