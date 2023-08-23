import pymysql
import json

# 连接类, isConnected, query(sql)
class SQLConnect():
	SQLAccount = None
	def __init__(self) -> None:
		
		if SQLConnect.SQLAccount == None:
			SQLConnect.SQLAccount = json.load(open("./server/SQLAccount.json"))
		if SQLConnect.SQLAccount == None:
			return
		self.__connect()

	def __connect(self):
		host  = SQLConnect.SQLAccount["host"]
		port  = SQLConnect.SQLAccount["port"]
		user  = SQLConnect.SQLAccount["username"]
		passwd= SQLConnect.SQLAccount["password"]
		try:
			self.__conn = pymysql.connect(host=host, port=port, user=user,
							   passwd=passwd, charset='utf8', db='meituan')
			self.__cursor = self.__conn.cursor(cursor=pymysql.cursors.DictCursor)
		except Exception as e:
			print(e)
			self.__conn = None
			self.__cursor = None
	
	def disconnect(self):
		if self.isConnected():
			self.__conn.close()
			self.__cursor.close()

	def isConnected(self):
		return self.__conn != None
	
	def query(self, sql:str):
		try:
			self.__cursor.execute(sql)
			data_list = self.__cursor.fetchall()
			self.__conn.commit()
			# print("sql [", sql, "] committed")
			return True, data_list
		except Exception as e:
			return False, str(e)

# 账号（用户，商家）
class individual():

	def __init__(self) -> None:
		self.userid = None
		self.usertype = None
		self.name = None
		self.phone = None
		self.connect = SQLConnect()

	def isConnected(self):
		return self.connect.isConnected()

	def disconnect(self):
		if self.isConnected():
			self.__conn.close()
			self.__cursor.close()

	def query(self, sql:str):
		return self.connect.query(sql)

# 用户
class meituanBuyer(individual):
	def __init__(self,userid:int,passwd) -> None:
		super().__init__()
		if not self.isConnected():
			return
		self.type = None
		self.login(userid,passwd)

	def login(self,userid,passwd):
		if not type(userid) is int:
			userid = int(userid)
		if not self.isConnected():
			print("not Connected")
			return
		sql='CALL BuyerLogin(%d,"%s");'%(userid,passwd)
		statue, response = self.query(sql)
		if statue==False or len(response) != 1:
			print("login error: ",response)
			return None
		else:
			response = response[0]
			print("BuyerLogin",response)
		self.type = 'B'
		self.userid = userid
		self.name = response["name"]
		self.phone = response["phone"]

	def setName(self,newName):
		sql = 'update buyer set name="%s" where id=%d'%(newName,self.userid)
		return self.query(sql)
	
	def delete(self):
		sql = 'DELETE FROM buyer WHERE buyer.ID=%d;'%self.userid
		statue, response = self.query(sql)
		if statue==True:
			sql = 'DELETE FROM auth  WHERE  auth.ID=%d;'%self.userid
			self.query(sql)
		else: print("error",response)
		pass

	def getOrders(self):
		return {}

# 商家
class meituanStore(individual):
	def __init__(self,userid:int,passwd) -> None:
		super().__init__()
		if not self.isConnected():
			return
		self.type = None
		self.login(userid,passwd)

	def login(self,userid,passwd):
		if not type(userid) is int:
			userid = int(userid)
		if not self.isConnected():
			print("not Connected")
			return	
		sql="CALL StoreLogin(%d,'%s');"%(userid,passwd)
		statue, response = self.query(sql)
		if statue==False or len(response) != 1:
			print("login error: ",response)
			return None
		else:
			response = response[0]
			print("StoreLogin",response)
		self.type = "S"
		self.userid = userid
		self.name = response["name"]
		self.regtime = response["regtime"]
		self.brief = response["brief"]
		self.phone = response["phone"]

	def setName(self,newName):
		sql = 'update store set name="%s" where id=%d'%(newName,self.userid)
		statue,response = self.query(sql)
		if statue: self.brief=newName
		return statue,response

	def setBrief(self,newBrief):
		sql = 'update store set brief="%s" where id=%d'%(newBrief,self.userid)
		statue,response = self.query(sql)
		if statue: self.brief=newBrief
		return statue,response

	def setPhone(self,newPhone):
		sql = 'update store set phone=%d where id=%d'%(newPhone,self.userid)
		statue,response = self.query(sql)
		if statue: self.phone=newPhone
		return statue,response

	def getGoodList(self):
		sql = 'select * from showgood where sid=%d'%(self.userid)
		return self.query(sql)

	def putGood(self,gname,gbrief,gprice):
		sql = "call putGood(%d,'%s','%s',%f);"%(self.userid,gname,gbrief,gprice)
		return self.query(sql)
	
	def delGoodByName(self,gname):
		sql = 'delete from good where goodname="%s" and storeID=%d'%(gname,self.userid)
		return self.query(sql)

# 工具类
class MeituanUtil():
	
	def __init__(self) -> None:
		self.connect = SQLConnect()
		self.user = None

	def lsBuyer(self):
		sql = "select auth.id, name  from auth,buyer where auth.id=buyer.id;"
		return self.connect.query(sql)

	def lsStore(self):
		sql = "select auth.id,name,brief from auth,store where auth.id=store.id;"
		return self.connect.query(sql)

	def BuyerLogin(self,uid,pwd):
		buyer = meituanBuyer(uid,pwd)
		if buyer.type==None:
			return None
		else:
			self.user = buyer
			return buyer

	def StoreLogin(self,uid,pwd):
		store = meituanStore(uid,pwd)
		if store.type==None:
			return None
		else:
			self.user = store
			return store

	def newBuyer(self, name, passwd, phone:int):
		sql = "CALL regBuyer('%s','%s',%d);"%(name,passwd,phone)
		statue, response = self.connect.query(sql)
		if statue==False:
			print("error",response)
			return None,None
		else:
			isNew = response[0]["count"]==0
			uid = response[0]["ID"]
			return isNew,uid

	def newStore(self,name,passwd,phone:int):
		sql = "CALL regStore('%s','%s',%d);"%(name,passwd,phone)
		statue, response = self.connect.query(sql)
		if statue==False:
			print("error",response)
			return None,None
		else:
			isNew = response[0]["count"]==0
			uid = response[0]["ID"]
			return isNew,uid

	def delBuyer(self,id:int,passwd):
		sql = 'CALL delUser(%d,"%s");'%(id,passwd)
		return self.connect.query(sql)

	def delStore(self,id,passwd):
		sql = 'CALL delUser(%d,"%s");'%(id,passwd)
		return self.connect.query(sql)
		
	def showGood(self,storeid):
		sql = 'SELECT gID,gName,gBrief,gPrice from showGood where sid=%d'%storeid;
		return self.connect.query(sql)
	
	def searchGood(self,goodname):
		sql = 'SELECT * from showGood where gName like "%%%s%%"'%goodname
		return self.connect.query(sql)
	
	def getAllAccount(self):
		sql = 'SELECT auth.id,type,pw,name from auth,store where auth.id=store.id'
		s1,r1 = self.connect.query(sql)
		ans = [[i["id"],i["type"],i["name"],i["pw"]] for i in r1] if s1 else []
		sql = 'SELECT auth.id,type,pw,name from auth,buyer where auth.id=buyer.id'
		s2,r2 = self.connect.query(sql)
		ans += [[i["id"],i["type"],i["name"],i["pw"]] for i in r2] if s2 else []
		return (s1 or s2),ans
	
	def logout(self):
		self.user = None