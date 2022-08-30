from flask import Flask, render_template, request,redirect, url_for
import mysql.connector
from datetime import date as d
import hashlib

db = mysql.connector.connect(
    host = "194.195.113.147",
    user = "sqluser",
    passwd = "Adnan$12",
    auth_plugin = "mysql_native_password",
    database = "testpython"
    #above line is commented if the database is not created
)

cursor = db.cursor()
app = Flask(__name__)

username = ""
userid = 0
output = ""


@app.route('/',methods=['POST','GET'])
def login():
    global output
    global userid 
    userid = 0
    return render_template('login.html',output=output)

@app.route('/checkuser',methods=['POST','GET'])
def checkuser():
    global userid
    global username
    global output
    email = request.form.get('email')
    passw = request.form.get('pass')
    try:
        passw = hashlib.md5(passw.encode()).hexdigest()
    except:
        output = "The email or password is incorrect"
        return redirect(url_for('login'))
    cursor.execute(f'select count(*) from user where password = "{passw}" and email = "{email}"')
    var = cursor.fetchall()
    if var[0][0]==1:
        cursor.execute(f'select userid,username from user where password = "{passw}" and  email = "{email}"')
        var = cursor.fetchall()
        userid = var[0][0]
        username = var[0][1]
        output = ""
        return redirect(url_for('index'))
    else :
        output = "The email or password is incorrect"
        return redirect(url_for('login'))

@app.route('/signup',methods=['POST','GET'])
def signup():
    global output
    output = ""
    o = ""
    if(request.method=="POST"):
        username = request.form.get('username')
        email = request.form.get('email')
        passw = request.form.get('pass')
        cursor.execute(f"select count(email) from user where email = '{email}'")
        var = cursor.fetchall()
        if var[0][0]>0:
            o = "An account associated with this email already exists"
            return render_template('signup.html',output=o)
        else:
            passw = hashlib.md5(passw.encode()).hexdigest()
            cursor.execute("insert into user( username, email,password) values (%s,%s,%s)",(username,email,passw))
            db.commit()
            return redirect(url_for('login'))
    return render_template('signup.html',output=o)


@app.route('/tasks',methods=['GET','POST'])
def index():
    global userid
    global username
    if userid!=0:
        cursor.execute(f"select * from task where userid = '{userid}'")
        var = cursor.fetchall()
        nvar = []
        for i,x in enumerate(var):
            nvar.append([x[2],x[3],x[4],x[5]])
        leng=len(nvar)
        return render_template("index.html",name=username,len=leng,var=nvar,enumerate=enumerate)
    return redirect(url_for('login'))

@app.route('/addtask',methods=['GET','POST'])
def addtask():
    global userid
    if userid!=0:
        return render_template('insert.html')
    return redirect(url_for('login'))
    
@app.route('/fetchdata',methods=['GET','POST'])
def fetchdata():
    global userid
    if userid!=0:
        if(request.method=="POST"):
            name = request.form.get('taskname')
            description = request.form.get('description')
            time = request.form.get('time')
            date = request.form.get('date')
            try:
                cursor.execute("insert into task(userid,name, description,t,d) values (%s,%s,%s,%s,%s)",(userid,name,description,time,date))
            except:
                date = None
                cursor.execute("insert into task(userid,name, description,t,d) values (%s,%s,%s,%s,%s)",(userid,name,description,time,date))
            db.commit()
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/confirmdelete',methods=['GET','POST'])
def confirmdelete():
    global userid
    if userid!=0:
        cursor.execute(f"delete from task where userid = '{userid}'")
        db.commit()
        return redirect(url_for('index'))
    return redirect(url_for('login'))


@app.route('/deleteeachtask',methods=['POST','GET'])
def deleteeachtask():
    global userid
    if userid!=0:
        cursor.execute(f"select * from task where userid = '{userid}'")
        var = cursor.fetchall()
        nvar = []
        for i,x in enumerate(var):
            nvar.append([x[2],x[3],x[4],x[5]])
        return render_template("deleteeachtask.html",len=len(nvar),var=nvar,enumerate=enumerate)
    return redirect(url_for('login'))

@app.route('/deleteforeach',methods=['POST','GET'])
def deleteforeach():
    global userid
    if userid!=0:
        if(request.method=="POST"):
            cursor.execute(f"select taskid from task where userid = '{userid}'")
            var = cursor.fetchall()
            leng = len(var)
            for i,x in enumerate(var):
                b = request.form.get(f'{i+1}')
                if b!=None:
                    statement = f'delete from task where taskid = {x[0]}'
                    cursor.execute(statement)
                    db.commit()
            return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/deleteaccount',methods=['GET','POST'])
def deleteaccount():
    global userid
    global output
    output = ""
    if userid!=0:
        cursor.execute(f"delete from task where userid = '{userid}'")
        cursor.execute(f"delete from user where userid = '{userid}'")
        db.commit()
    return redirect(url_for('login'))

@app.errorhandler(404)
def invalid_route(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=False)
    db.close()
