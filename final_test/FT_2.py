start_calories = 100
calories_increase = 50
total_kilometers = 10
total_calories = 0
for i in range(total_kilometers):
    total_calories += start_calories + i * calories_increase
print(total_calories) 