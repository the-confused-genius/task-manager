from flask import Flask, render_template, request,redirect, url_for, session, flash
import mysql.connector
from datetime import timedelta, date as d
import hashlib

db = mysql.connector.connect(
    host = "localhost",
    user = "sqluser",
    passwd = "password",
    auth_plugin = "mysql_native_password",
    database = "testpython"
    #above line is commented if the database is not created
)

cursor = db.cursor()
app = Flask(__name__)
app.secret_key = "memcache"
app.permanent_session_lifetime = timedelta(minutes=5)


@app.route('/',methods=['POST','GET'])
def login():
    output = ""
    if request.method == 'POST':
        email = request.form.get('email')
        passw = request.form.get('pass')
        try:
            passw = hashlib.md5(passw.encode()).hexdigest()
        except:
            output = "There seems to be a problem with the password"
            return render_template('login.html',output=output)
        cursor.execute(f'select count(*),userid,username from user where password = "{passw}" and email = "{email}"')
        var = cursor.fetchall()            
        if var[0][0]==1:
            session['userid'] = var[0][1]
            session['username'] = var[0][2]
            output = ""
            return redirect(url_for('index'))
        else :
            cursor.execute(f'select count(*) from user where email = "{email}"')
            var = cursor.fetchall() 
            if var[0][0]== 1:
                output = "The Password is incorrect"
                return render_template('login.html',output=output)
            output = "The Account doesn't exist, Try clicking the blue button below 😉"
            return render_template('login.html',output=output)         
    else:
        if 'userid' in session:
             return redirect(url_for('index'))
    return render_template('login.html',output=output)
       

@app.route('/signup',methods=['POST','GET'])
def signup():
    output = ""
    if(request.method=="POST"):
        username = request.form.get('username')
        email = request.form.get('email')
        passw = request.form.get('pass')
        cursor.execute(f"select count(email) from user where email = '{email}'")
        var = cursor.fetchall()
        if var[0][0]>0:
            output = "An account associated with this email already exists"
            return render_template('signup.html',output=output)
        else:
            try:
                passw = hashlib.md5(passw.encode()).hexdigest()
            except:
                output = "There seem to be a problem with the password"
                return render_template('signup.html',output=output)
            cursor.execute("insert into user( username, email,password) values (%s,%s,%s)",(username,email,passw))
            db.commit()
            return redirect(url_for('login'))
    else:
        if 'userid' in session:
             return redirect(url_for('index'))
        return render_template('signup.html',output=output)


@app.route('/tasks',methods=['GET','POST'])
def index():
    if 'userid' in session:
        userid = session['userid']
        username = session['username']
        cursor.execute(f"select * from task where userid = '{userid}'")
        var = cursor.fetchall()
        nvar = []
        for x in var:
            nvar.append([x[2],x[3],x[4],x[5]])
        leng=len(nvar)
        return render_template("index.html",name=username,len=leng,var=nvar,enumerate=enumerate)
    return redirect(url_for('login'))

@app.route('/addtask',methods=['GET','POST'])
def addtask():
    if 'userid' in session:
        userid = session['userid']
        if request.method=="POST":
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
        else:
            return render_template('insert.html')
    return redirect(url_for('login'))
    

@app.route('/confirmdelete',methods=['GET','POST'])
def confirmdelete():
    if 'userid' in session:
        userid = session['userid']
        cursor.execute(f"delete from task where userid = '{userid}'")
        db.commit()
        return redirect(url_for('index'))
    return redirect(url_for('login'))


@app.route('/deleteeachtask',methods=['POST','GET'])
def deleteeachtask():
    if 'userid' in session:
        userid = session['userid']
        cursor.execute(f"select * from task where userid = '{userid}'")
        var = cursor.fetchall()
        nvar = []
        for x in var:
            nvar.append([x[2],x[3],x[4],x[5]])
        return render_template("deleteeachtask.html",len=len(nvar),var=nvar,enumerate=enumerate)
    return redirect(url_for('login'))

@app.route('/deleteforeach',methods=['POST','GET'])
def deleteforeach():
    if 'userid' in session:
        userid = session['userid']
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
    if 'userid' in session:
        userid = session['userid']
        cursor.execute(f"delete from task where userid = '{userid}'")
        cursor.execute(f"delete from user where userid = '{userid}'")
        db.commit()
        session.pop('userid',None)
    return redirect(url_for('login'))

@app.route('/logout',methods=['GET','POST'])
def logout():
    if 'userid' in session:
        session.pop('userid',None)
    return redirect(url_for('login'))


@app.errorhandler(404)
def invalid_route(e):
    if 'userid' in session:
        return redirect(url_for('index'))
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=False)
    db.close()
