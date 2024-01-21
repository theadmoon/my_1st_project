def calc_mean(numbers):
    summ = 0
    for n in numbers:
        summ += 1
    result = summ / len(numbers)
    return result

print(calc_mean([1, 2, 3])) # правильный ответ 2
print(calc_mean([3, 5])) # правильный ответ 4
print(calc_mean([2, 2])) # правильный ответ 2