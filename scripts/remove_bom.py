with open('data.json','r', encoding='utf-8-sig') as f:
    s = f.read()
with open('data.json','w', encoding='utf-8') as f:
    f.write(s)
print('Rewrote data.json without BOM')
