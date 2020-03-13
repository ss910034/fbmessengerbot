from ts import *


product = query_AllProduct()

for key in product:
	if key.find('Converse') != -1:
		print(key)

if 'Converse' in product.keys():
	print('ddd')