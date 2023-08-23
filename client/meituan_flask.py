from flask import *
import sys,os
sys.path.insert(0,os.path.abspath("."))
from server.meituan import *
util = MeituanUtil()

app = Flask(__name__)
app.debug=True
app.secret_key = 'your_secret_key'


@app.route('/',methods=['get','POST'])
def buyerLogin():
	return render_template("login.html",content={"type":"B"})

@app.route('/storeLogin',methods=['get','POST'])
def storeLogin():
	return render_template("login.html",content={"type":"S"})

@app.route("/signup",methods=['get','POST'])
def signup():
	return render_template("signup.html",content={"type":"B"})

@app.route("/signingup",methods=['get','POST'])
def signingup():
	type = request.form.get('type')
	name = request.form.get('name')
	pwd = request.form.get('pwd')
	phone = int(request.form.get('phone'))
	if type=="B":
		isNew,uid = util.newBuyer(name,pwd,phone)
	else: isNew,uid=util.newStore(name,pwd,phone)
	if isNew==None:
		flash("注册失败：用户名已被占用","signResult")
		return redirect(url_for("/signup"))
	elif isNew:
		flash("注册成功，ID为%d"%uid,"signResult")
	else:
		flash("该用户名已注册，ID为%d，请直接登录"%uid,"signResult")
	if type=="B": return redirect(url_for("buyerLogin"))
	else: return redirect(url_for("storeLogin"))

@app.route("/storeSignup",methods=['get','POST'])
def storeSignup():
	return render_template("signup.html",content={"type":"S"})

@app.route("/forgot",methods=["get","POST"])
def forgot():
	statue,response = util.getAllAccount()
	if statue: return jsonify({"accounts":response})
	else: return None

@app.route("/self",methods=["get","POST"])
def self():
	content = {}
	buyer = util.user
	if buyer != None:
		content["user"]   = util.user
		content["userid"] = buyer.userid
		content["orders"] = buyer.getOrders()
		content["name"]   = buyer.name
		content["phone"]  = buyer.phone
		return render_template("self.html",content=content)


@app.route("/storeSelf",methods=["get","POST"])
def storeSelf():
	content = {}
	store = util.user
	if store != None:
		content["user"]   = util.user
		content["userid"]  = store.userid
		content["name"]    = store.name
		content["regtime"] = store.regtime
		content["brief"]   = store.brief
		content["phone"]   = store.phone
		content["goods"] = []
		return render_template("store.html",content=content)

@app.route("/logining",methods=["get",'POST'])
def logining():
	uid = request.form.get('uid')
	pwd = request.form.get('pwd')
	type = request.form.get('type')
	if type=="B":
		buyer = util.BuyerLogin(uid,pwd)
		if buyer != None:
			return redirect(url_for("self"))
	elif type=="S":
		store = util.StoreLogin(uid,pwd)
		if store != None:
			return redirect(url_for("storeSelf"))
	flash("登录失败","warning")
	if type == 'B': return redirect(url_for("buyerLogin"))
	else: return redirect(url_for("storeLogin"))
	
@app.route("/logout",methods=['get','POST'])
def logout():
	typ = util.user.type
	util.logout()
	if typ == 'B': return redirect(url_for("buyerLogin"))
	else: return redirect(url_for("storeLogin"))


if __name__ == '__main__':
	app.run()