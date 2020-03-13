
class User():
	
	def __init__(self, sender, profile):
		self.senderId = sender
		self.profile = profile
		self.query_price = False
		self.buy = False
		self.product_Name = ''
		self.product_Type = ''
		self.product_Size = ''
		self.product_Num = 0
		self.product_price = 0
		self.isChooseNum = False
		self.isChooseSize = False
		self.isChooseType = False
		self.checkPic = False

	def resetdata(self):
		self.query_price = False
		self.buy = False
		self.product_Name = ''
		self.product_Type = ''
		self.product_Size = ''
		self.product_Num = 0
		self.product_price = 0
		self.isChooseNum = False
		self.isChooseSize = False
		self.isChooseType = False
		self.checkPic = False

	def set_queryprice(self, booleanvalue):
		self.query_price = booleanvalue

	def set_checkpic(self, booleanvalue):
		self.checkPic = booleanvalue

	def set_buy(self, booleanvalue):
		self.buy = booleanvalue

	def set_name(self, productName):
		self.product_Name = productName

	def set_type(self, productType):
		self.product_Type = productType

	def set_size(self, productSize):
		self.product_Size = productSize

	def set_num(self, productNum):
		self.product_Num = productNum

	def set_price(self, productPrice):
		self.product_price = productPrice

	def set_choosenum(self, booleanvalue):
		self.isChooseNum = booleanvalue
	
	def set_choosesize(self, booleanvalue):
		self.isChooseSize = booleanvalue

	def set_choosetype(self, booleanvalue):
		self.isChooseType = booleanvalue