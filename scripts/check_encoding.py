with open('data.json','rb') as f:
    b = f.read(4)
    print(b)
    print([hex(x) for x in b])
