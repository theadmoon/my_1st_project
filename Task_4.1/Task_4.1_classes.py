fruits = ["Apple", "Orange", "Banana"]

features = {
    "Apple": {
        "colour": 'red',
        "weight": 200,
        "taste": "sour"
    },
    "Orange": {
        "colour": 'orange',
        "weight": 540,
        "taste": "sweet"
    },
    "Banana": {
        "colour": 'yellow',
        "weight": 300,
        "taste": 'cloying'
    }
}

class Fruits:
    def __init__(self, name, colour, weight, taste):
        self.name = name
        self.colour = colour
        self.weight = weight
        self.taste = taste

apple = Fruits(name="Apple", colour='red', weight=200, taste='sour')
orange = Fruits(name="Orange", colour='orange', weight=540, taste='sweet')
banana = Fruits(name="Banana", colour='yellow', weight=300, taste='cloying')

print(f'Яблапельнан имеет свойства: ', apple.colour, orange.weight, banana.taste)

x = 200
y = 120
x = y
y = x
print(x,y)

x = 200
y = 120
x, y = y, x
print(x, y)

fruits = 50

if fruits == 100:
    print("Это настоящий сок")
else:
    if fruits >= 75:
        print("Вполне себе сок, хоть и разбавленный")
    else:
        if fruits >= 45:
            print("Так себе напиток")
        else:
            if fruits >= 0:
                print("Это вообще сложно назвать соком. Лучше пейте воду")
            else:
                print("Вы ввели неверный процент содержания. Введите число от 0 до 100.")

fruits = 99
# Должно быть двойное = в строчке if fruits = 100; должны быть интервалы

if fruits == 100:
    print("Это настоящий сок")
elif fruits in list(range(75,100)):
    print("Вполне себе сок, хоть и разбавленный")
elif fruits in list(range(45,75)):
    print("Так себе напиток")
elif fruits >= 0 and fruits < 45:
    print("Это вообще сложно назвать соком. Лучше пейте воду")
else:
    print("Вы ввели неверный процент содержания. Введите число от 0 до 100.")

'''
class Character:
    def __init__(self, name, speed, health):
        self.name = name
        self.speed = speed
        self.health = health

creeper = Character(name="Creeper", speed=35, health=100)
spider = Character(name="Spider", speed=30, health=100)
zombie = Character(name="Zombie", speed=25, health=100)

print(creeper.name)

'''

game_characters = ["Creeper", "Spider", "Zombie", "Skeleton", "Enderman"]

params = {
    "Creeper": {
        "health": 20,
        "attack_damage": 20,
        "speed": 0.25,
        "skill": "Explosive"
    },
    "Spider": {
        "health": 16,
        "attack_damage": 2,
        "speed": 0.3,
        "skill": "Poisonous"
    },
    "Zombie": {
        "health": 20,
        "attack_damage": 3,
        "speed": 0.23,
        "skill": "Infectious"
    },
    "Skeleton": {
        "health": 20,
        "attack_damage": 4,
        "speed": 0.25,
        "skill": "Ranged"
    },
    "Enderman": {
        "health": 40,
        "attack_damage": 7,
        "speed": 0.3,
        "skill": "Teleportation"
    }
}                    
''''''