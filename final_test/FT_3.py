n = 918273645
max_digit = 0
for i in str(n):
    x = int(i)
    if x > max_digit:
        max_digit = x
print(max_digit)