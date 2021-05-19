from flask import Flask,render_template,request,flash,redirect,url_for,session,send_from_directory
from flask_mysqldb import MySQL
from flask_mail import Mail,Message
import random
import os
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
from PIL import Image
app=Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'qwerty2@'
app.config['MYSQL_DB'] = 'hostel_db'
mysql=MySQL(app)

app.secret_key="qwertyuiopasdfghjklzxcvbnm"

app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='appdevspo@gmail.com',
    MAIL_PASSWORD='qwerty2@'
)

mail=Mail(app)

def send_otp(reciver,otp):
    msg=Message('OTP',
                sender='appdevspo@gmail.com',
                recipients=[reciver])
    msg.body="Here is your one time password :"+str(otp)
    mail.send(msg)
    flash('otp sent succesfully please validate','success')
    return



@app.before_first_request
def init_app():
    session['hostelname'] = 'WELCOME TO IIT KANPUR'
    session['show'] = True
    session['logged_in'] =False
    session['signup']=False
    session['otpverify'] = False
    session['otp_2']=False
    session['update_verify']=False
    session['admin']=False
@app.route('/')
def home():
    session['show'] = True
    session['hostelname'] = 'WELCOME TO IIT KANPUR'
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM notification WHERE showonhome=%s",('yes',))
    x=cur.fetchall()
    cur.execute("SELECT * FROM event WHERE showonhome=%s",('yes',))
    x1=cur.fetchall()
    return render_template('home.html',items=x,items1=x1)
    #return redirect(url_for('login'))
@app.route('/event/<eid>')
def showimg(eid):
    return send_from_directory('C:\\Users\\devan\\Desktop\\fllask\\static\\img\\events',filename=str(eid)+'.jpg')

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")





@app.route('/login',methods=['GET','POST'])
def login():
    if('logged_in' in session and session['logged_in']==True):
        return redirect(url_for('home'))
    if(request.method=='POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        session['username']=username
        cur1 = mysql.connection.cursor()
       
        
        x=cur1.execute("SELECT * FROM users WHERE username=%s",(username,))
        if (x!=0):
            data=cur1.fetchone()
            if(sha256_crypt.verify(password,data[2])):
                session['username'] = data[0]
                session['email']=data[1]
                session['logged_in']=True
                return redirect(url_for('home'))
            else:
                flash('wrong password','danger')
                return render_template('login.html')
        else:
            flash('user not registered')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session['logged_in']=False
    session['otpverify'] = False
    session['signup'] = False
    return redirect(url_for('home'))
@app.route('/userdetails',methods=["GET","POST"])
def userdetails():
    if('logged_in' in session and session['logged_in']==True):
        return redirect(url_for('home'))
    if ('signup' in session and session['signup'] == False):
        flash('PLEASE SIGNUP FIRST TO ENTER DETAILS','danger')
        return redirect('signup')
    if ('otp' in session and session['otp'] == False):
        flash('please veryfiy the otp first','danger')
        return redirect(url_for('otp'))
    if(request.method=='POST'):
        name=request.form.get('fullname')
        rollno=request.form.get('rollno')
        branch=request.form.get('branch')
        hostelname=request.form.get('hostelname')
        roomno=request.form.get('roomno')
        mobileno=request.form.get('mobileno')
        
        cur=mysql.connection.cursor()
        x=cur.execute("SELECT * FROM users WHERE rollno=(%s)",(rollno,))
        if(int(x)>0):
            flash("ROLL NO. ALREADY EXIST PLEASE USE ANOTHER",'danger')
            return render_template('userdetails.html')
        if(len(name)==0 or len(rollno)==0 or len(branch)==0 or len(hostelname)==0 or len(roomno)==0 or len(mobileno)!=10):
           flash('enter a valid details','danger')
           return redirect(url_for('userdetails'))
        cur = mysql.connection.cursor()
        password = sha256_crypt.encrypt(session['password'])
        cur.execute("INSERT INTO users(username,email,password,name,rollno,branch,hostelname,roomno,mobileno) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (session['username'],session['email'],password,name,rollno,branch,hostelname,roomno,mobileno))
        mysql.connection.commit()
        cur.close()
        session['logged_in'] = True
        return redirect(url_for('home'))
    return render_template('userdetails.html')


@app.route('/otpverification',methods=['GET','POST'])
def otp():
    if('logged_in' in session and session['logged_in']==True):
        return redirect(url_for('home'))
    if ('signup' in session and session['signup'] == False):
        flash('PLEASE SIGNUP FIRST TO ENTER DETAILS','danger')
        return redirect(url_for('signup'))
    if(request.method=='POST'):
        num=request.form.get('otp')
        #print(num,session['otp'])
        if(int(num)==session['otp']):
            session['otpverify']=True
            session['signup'] = True
            flash('Successfully registered please enter your details','success')
            return redirect(url_for('userdetails'))
        else:
            flash('OTP ENTERED IS INCORRECT','danger')
            return render_template('otpverify.html')
    return render_template('otpverify.html')


@app.route('/signup',methods=["GET","POST"])
def signup():
    if('logged_in' in session and session['logged_in']==True):
        return redirect(url_for('home'))
    if(request.method=='POST'):
        #add to data base
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        if(email[-10:]!='iitk.ac.in'):
            flash('Please use institute mail id only','danger')
            return redirect(url_for('signup'))
        if(len(username)==0 or len(email)==0 or len(password)==0):
            flash('enter a valid details','danger')
            return redirect(url_for('signup'))
        cur=mysql.connection.cursor()
        x=cur.execute("SELECT * FROM users WHERE username=(%s)",(username,))
        if(int(x)>0):
            flash("USERNAME ALREADY EXIST PLEASE USE ANOTHER",'danger')
            return render_template('signup.html')
        x = cur.execute("SELECT * FROM users WHERE email=(%s)", (email,))
        if (int(x) > 0):
            flash("USER ALREADY REGISTERED WITH THIS EMAIL ID",'danger')
            return render_template('signup.html')
        cur.close()
        x1=random.randrange(111111,999999)
        send_otp(email,x1)
        #d={'x':x1,'username':username,'email':email,'password':password}
        session['username'] = username
        session['email'] = email
        session['password'] = password
        session['otp']=x1
        session['otpverify'] = False
        session['signup'] = True
        return redirect(url_for('otp'))
    return render_template('signup.html')

@app.route('/forgot-password',methods=['GET','POST'])
def forgotpassword():
    if('logged_in' in session and session['logged_in']==True):
        return redirect(url_for('home'))
    if(request.method=='POST'):
        email = request.form.get('email')
        cur = mysql.connection.cursor()
        x = cur.execute("SELECT * FROM users WHERE email=(%s)", (email,))
        if (int(x) > 0):
            x2=random.randrange(111111,999999)
            send_otp(email,x2)
            session['otp-2']=x2
            return redirect(url_for('otp2'))
        else:
            flash('Email not registered','danger')
            return render_template('forgotpassword.html')
    return render_template('forgotpassword.html')

@app.route('/otp-2-verify',methods=['GET','POST'])
def otp2():
    if('logged_in' in session and session['logged_in']==True):
        return redirect(url_for('home'))
    if(request.method=='POST'):
        num=request.form.get('otp')
        #print(num,session['otp'])
        if(int(num)==session['otp-2']): 
            flash('Successfully verified','success')
            return redirect(url_for('resetpassword'))
        else:
            flash('OTP ENTERED IS INCORRECT','danger')
            return render_template('otp2.html')
    return render_template('otp2.html')

@app.route('/reset-password',methods=['GET','POST'])
def resetpassword():
     if('logged_in' in session and session['logged_in']==True):
        return redirect(url_for('home'))
     if(request.method=='POST'):
        username=request.form.get('username')
        password=request.form.get('new password')
        confirm_password=request.form.get('confirm password')
        cur = mysql.connection.cursor()
        x = cur.execute("SELECT * FROM users WHERE username=(%s)", (username,))
        if (int(x) > 0 and password==confirm_password):
            password = sha256_crypt.encrypt(password)
            cur.execute("""update users set password=%s where username=%s""",(password,username,))
            mysql.connection.commit()
            return redirect(url_for('login'))
        else:
            flash("Invalid entry.Please check and try again")
            return render_template('resetpassword.html')
     return render_template('resetpassword.html')
        
    
@app.route('/complaints',methods=['GET','POST'])
def complaints():
    if('logged_in' in session and session['logged_in']==False):
        flash('PLEASE LOG IN FIRST','danger')
        return redirect(url_for('login'))
    session['hostelname']='REGISTER YOUR COMPLAINTS'
    session['show']=True
    if(request.method=='POST'):
        subject=request.form.get('subject')
        category=request.form.get('category')
        urgency=request.form.get('urgency')
        timeofavilibility=request.form.get('timeofavial')
        details=request.form.get('details')
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO complaints(username,subject,category,time_of_availability,details,urgency) VALUES(%s,%s,%s,%s,%s,%s)",(session['username'],subject,category,timeofavilibility,details,urgency))
        mysql.connection.commit()
        cur.close()
        flash('Complaint registered','success')
        return render_template('complaints.html',scrollToAnchor='complaints')

    return render_template('complaints.html')

@app.route('/suggetions',methods=['GET','POST'])
def suggetions():
    if('logged_in' in session and session['logged_in']==False):
        flash('PLEASE LOG IN FIRST','danger')
        return redirect(url_for('login'))
    session['hostelname']='PROVIDE YOUR VALUABLE SUGGESTIONS'
    session['show']=True
    if(request.method=='POST'):
        subject=request.form.get('subject')
        details=request.form.get('details')
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO suggetions(username,subject,details) VALUES(%s,%s,%s)",(session['username'],subject,details))
        mysql.connection.commit()
        cur.close()
        flash('THANK YOU FOR YOUR VALUABLE SUGGESTIONS. WE WILL IMPROVE OURSELF','success')
        return render_template('suggetions.html',scrollToAnchor='contact')

    return render_template('suggetions.html')

@app.route('/profile',methods=['GET','POST'])
def profile():
    if('logged_in' in session and session['logged_in']==False):
        flash('PLEASE LOG IN FIRST','danger')
        return redirect(url_for('login'))
    session['hostelname'] = 'PROFILE'
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email=(%s)",(session['email'],))
    x = cur.fetchone()
    if(request.method=='POST'):
        username=request.form.get('username')
        if (username==''):      
            username=x[0]
        name=request.form.get('name')
        if (name==''):
            name=x[3]
        rollno=request.form.get('rollno')
        if (rollno==''):
            rollno=x[4]
        branch=request.form.get('branch')
        if (branch==''):
            branch=x[5]
        hostelname=request.form.get('hostelname')
        if(hostelname==''):
            hostelname=x[6]
        roomno=request.form.get('roomno')
        if(roomno==''):
            roomno=x[7]
        mobileno=request.form.get('mobileno')
        if(mobileno==''):
            mobileno=x[8]
        password=request.form.get('password')
        file = request.files['file']
        cur=mysql.connection.cursor()
        x2=cur.execute("SELECT * FROM users WHERE username=%s OR rollno=%s",(username,rollno,))
        if(x2!=0 and username!=x[0] or rollno!=x[4]):
            flash('Username or Roll No. already Exist!!')
            return render_template('profile.html',x=x,scrollToAnchor='profile')
        else:
            cur.execute("SELECT * FROM users WHERE email=(%s)", (session['email'],))
            x = cur.fetchone()
            if (sha256_crypt.verify(request.form.get('password'), x[2])):

                session['username']=username
               
                cur.execute('update users set username=%s,name=%s,rollno=%s,branch=%s,hostelname=%s,roomno=%s,mobileno=%s where email=%s',(username,name,rollno,branch,hostelname,roomno,mobileno,session['email'],))
                mysql.connection.commit()
                if (file and file.filename != ''):
                    if(os.path.isfile('C:\\Users\\devan\\OneDrive\\Desktop\\newdesk\\fllask\\fllask\\static\\img\\users\\'+str(x[0])+'.jpg')):
                        os.remove('C:\\Users\\devan\\OneDrive\\Desktop\\newdesk\\fllask\\fllask\\static\\img\\users\\'+str(x[0])+'.jpg')
                    l=file.filename.split('.')
                    file.filename = str(session['username']) +'1'+'.'+str(l[-1])
                    filename = secure_filename(file.filename)
                    file.save(os.path.join('C:\\Users\\devan\\OneDrive\\Desktop\\newdesk\\fllask\\fllask\\static\\img\\users', filename))
                    s='C:\\Users\\devan\\OneDrive\\Desktop\\newdesk\\fllask\\fllask\\static\\img\\users\\'+str(filename)
                    img1=Image.open(s)
                    img2=img1.convert('RGB')
                    s = 'C:\\Users\\devan\\OneDrive\\Desktop\\newdesk\\fllask\\fllask\\static\\img\\users\\' + str(session['username'])+'.jpg'
                    img2.save(s)
                    os.remove(os.path.join('C:\\Users\\devan\\OneDrive\\Desktop\\newdesk\\fllask\\fllask\\static\\img\\users', filename))
            else:
                flash('Incorrect Password')
                return render_template('profile.html', x=x, scrollToAnchor = 'profile')
    return render_template('profile.html', x=x)

@app.route('/update_verify',methods=['GET','POST'])
def update_verify():
    if (request.method=='POST'):
        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=(%s)",(session['email'],))
        x = cur.fetchone()
        if(sha256_crypt.verify(request.form.get('password'), x[2])):
            session['update_verify']=True
            session['username']=x[0]
            return redirect(url_for('profile'))
        else:
            flash('Incorrect Password!')
    return render_template('update_verify.html')

app.run(debug=True)
