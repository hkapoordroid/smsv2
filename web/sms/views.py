"""
Routes and views for the sms web application.
"""
from flask import Flask, render_template, flash, request, redirect, url_for, g
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from datetime import datetime
from sms import app
from wtforms import StringField, BooleanField, SelectField, TextAreaField, PasswordField, DateField
from wtforms.validators import InputRequired, Email
from flask import flash
from model.user import User
from flask_login import login_user, login_required, current_user, logout_user
import awshelper
#from enum import Enum


Types = ['Shoes', 'Watch', 'Hangbag', 'Clothes']
Countries = ['USA']


#class ContestStatus(Enum):
#    Active = "Active"
#    Past = "Past"
#    Future = "Future"

#class ContestDataFields(Enum):
#    Title = "title"
#    StartTime = "starttime"
#    EndTime = "endtime"
#    Description = "description"
#    ContestID = "contestid"
#    ImageUrl = "imageurl"

class LoginForm(FlaskForm):
    loemail = StringField("Email",  [InputRequired("Please enter your email address."), Email("This field requires a valid email address")])
    lopass = PasswordField("Password", [InputRequired("Please enter your password.")])
    #PasswordField("Password", [InputRequired(), Length(min=5, max=10), AnyOf(['secret','password'])]


class UploadForm(FlaskForm):
    gaphoto = FileField('Example File')
    gatype = SelectField("gatype", choices=[(f, f) for f in Types])
    gatitle = StringField("gatitle")
    gadescription = TextAreaField("description")

class Profile(FlaskForm):
    fullname = StringField("Full Name", [InputRequired("Please enter your full name")])
    igusername = StringField("Instagram Username", [InputRequired("Please enter IG Username")])

class ActiveContest():
    
    def __init__(self):
        self.imageurl = None
        self.title = None
        self.description = None
        self.starttime = None
        self.endtime = None
        self.contestid = None
        self.likes = None
        self.comments = None
        self.followersgained = None
        

@app.route('/dashboard', methods=['GET'])
@login_required
def index_page():
    #print("Current user : " + str(current_user.id))

    contestsData = awshelper.getUserContests(str(current_user.id))

    activeContests = list()
    if contestsData:
        #lets get the active contests first
        if "Active" in contestsData:
            for ack, acv in contestsData["Active"].iteritems():
                #print(ac.keys)
                acObj = ActiveContest()
                acObj.title = acv['title']
                acObj.description = acv['description']
                acObj.starttime = datetime.strptime(acv['starttime'], '%m/%d/%YT%H:%M:%SZ').strftime('%I:%M %p %b %d, %Y')
                acObj.endtime = datetime.strptime(acv['endtime'], '%m/%d/%YT%H:%M:%SZ').strftime('%I:%M %p %b %d, %Y')
                acObj.imageurl = acv['imageurl']
                acObj.contestid = ack
                #TODO: get likes, comments, followers gained data from active contests table and add it to the acObj
                acObj.likes = 1340
                acObj.comments = 982
                acObj.followersgained = 982

                
                activeContests.append(acObj)
                
                     

    return render_template('dashboard.html', page_title="Dashboard", activeContests=activeContests)

@app.route('/', methods=['POST', 'GET'])
def login_page():
    #if request.method == "GET":
    #    logout_user()

    form = LoginForm()

    if form.validate_on_submit():
        useremail = form.loemail.data
        userpass = form.lopass.data

        print('Username = ' + useremail)
        print('Password = ' + userpass)

        #TODO: Authentication goes here

        #if the authentication is success
        #create an instance of User class 
        #user = User(useremail, userpass)
        #save the logged in user

        #if userpass == users[useremail]['pw']:
        if awshelper.verify_login(useremail, userpass):
            user = User()
            user.id = useremail
            login_user(user)
            
            #session['logged_in'] = True
            flash('Welcome!')
            next = request.args.get('next')
            return redirect(url_for('index_page'))
        else:
            print("Invalid username or password")
            flash("Invalid username or password")
            
        #TODO: If authentication fails, return error message to user

    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
def logout_page():
    logout_user()
    #session['logged_in'] = False
    return redirect(url_for('login_page'))    

@app.route('/sga', methods=['POST', 'GET'])
@login_required
def upload_page():
    form = UploadForm()
    if form.validate_on_submit():
        #print(form.gaphoto.data.filename)
        s3PhotoUrl = awshelper.upload_image_to_s3(form.gaphoto)

        #get the fields to display
        #rwtitle = str(form.gatitle.data)
        #rwdescription = str(form.gadescription.data)
        #rwtype = str(form.gatype.data)
        #rwphoto = "<img src=\"" + s3PhotoUrl + "\" height=\"150\" width=\"75\">"
        

        return render_template('giveawayconfirmation.html', page_title="Submit Giveaway")
        
		#output = s3_upload(form.example)
        #flash('{src} uploaded to S3 as {dst}'.format(src=form.example.data.filename, dst=output))
    return render_template('giveawayform.html', form=form, page_title="Submit Giveaway")

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    form = Profile()
    if form.validate_on_submit():
        print(form.fullname.data)
        print(form.igusername.data)

        #return render_template(url_for('giveawayform.html'), page_title="Profile")

    return render_template('profile.html', form=form, page_title="Profile")
        