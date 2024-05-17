# Словарь для шифрования
cipher = {
'd': 'a', 'e': 'b', 'f': 'c', 'g': 'd', 'h': 'e',
'i': 'f', 'j': 'g', 'k': 'h', 'l': 'i', 'm': 'j',
'n': 'k', 'o': 'l', 'p': 'm', 'q': 'n', 'r': 'o',
's': 'p', 't': 'q', 'u': 'r', 'v': 's', 'w': 't',
'x': 'u', 'y': 'v', 'z': 'w', 'a': 'x', 'b': 'y', 'c': 'z'
}
#text = 'la vaca loca2'
text = "hello world"
#n = 2
n = 10
len_text = len(text)
print(len_text)
result = ''
n_count = 0
while n_count < n:
    result = ''
    for i in range(len(text)):
    #    a = text[i]
    #    b= cipher.get(a, a)
    #    result = result + b
        print(i)
        print("text[i] =", text[i])
        print("cipher.get(text[i], text[i]) =", cipher.get(text[i], text[i]))
        result = result + cipher.get(text[i], text[i])
    text = result
    print(f"n_countresult{n_count} = {result}")
    print(f"result{n_count} = {result}")
    print(f"text{n_count} = {text}")
    n_count += 1
print(result)
'''
cipher = {'m': 'a', 'h': 'b', 't': 'c', 'f': 'd', 'g': 'e', 'k': 'f', 'b': 'g', 'p': 'h', 'j': 'i', 'w': 'j', 'e': 'k', 'r': 'l', 'q': 'm', 's': 'n', 'l': 'o', 'n': 'p', 'x': 'q', 'o': 'r', 'c': 's', 'd': 't', 'z': 'u', 'y': 'v', 'v': 'w', 'u': 'x', 'i': 'y', 'a': 'z'}

text = "vpjrg dozg: rgmos()"
result = ""

for i in range(len(text)):
#    a = text[i]
#    b= cipher.get(a, a)
#    result = result + b
    result = result + cipher.get(text[i], text[i])
print(result)



count = 0
while count < 3:
    print(count)
    count += 1
    
s = "ℙүтℌøη и ⅈṣκʋςтṿён₦ӱй ⅈ₦тεłłёκт"
symbol = "ø"
i = 0
while i < len(s):
    if s[i] == symbol:
        result = "True"
        i +=1
        break
    else:
        result = "False"
    i += 1
print(result)    
    
for i in cipher:
    new_cipher = cipher[i]
    for j in s:
        if j in cipher:
            new_symbol[j] = cipher[j]
    print(new_cipher)
'''