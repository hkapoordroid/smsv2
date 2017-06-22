"""
Routes and views for the sms web application.
"""
from flask import Flask, render_template, flash, request, redirect, url_for, g
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from datetime import datetime, timedelta
from sms import app
from wtforms import StringField, BooleanField, SelectField, TextAreaField, PasswordField, DateField
from wtforms.validators import InputRequired, Email, DataRequired
from flask import flash
from model.user import User
from flask_login import login_user, login_required, current_user, logout_user
import awshelper
import sys
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
    gaphoto = FileField('GA Picture')
    gatype = SelectField("GA Type", choices=[(f, f) for f in Types])
    gatitle = StringField("GA Title")
    gadescription = TextAreaField("description")

class Profile(FlaskForm):
    fullname = StringField("Full Name", [InputRequired("Please enter your full name")])
    igusername = StringField("Instagram Username", [InputRequired("Please enter IG Username")])


class FutureContest():
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

class PastContest():
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

    contestsData = awshelper.get_user_contests(str(current_user.id))

    activeContests = list()
    pastContests = list()
    futureContests = list()
    if contestsData:
        #lets get the active contests first
        if "Active" in contestsData:
            for i in contestsData['Active']:
                for ack, acv in i.iteritems():
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

        if "Past" in contestsData:
            for i in contestsData['Past']:
                for ack, acv in i.iteritems():
                    #print(ac.keys)
                    pcObj = PastContest()
                    pcObj.title = acv['title']
                    pcObj.description = acv['description']
                    pcObj.starttime = datetime.strptime(acv['starttime'], '%m/%d/%YT%H:%M:%SZ').strftime('%I:%M %p %b %d, %Y')
                    pcObj.endtime = datetime.strptime(acv['endtime'], '%m/%d/%YT%H:%M:%SZ').strftime('%I:%M %p %b %d, %Y')
                    pcObj.imageurl = acv['imageurl']
                    pcObj.contestid = ack
                    #TODO: get likes, comments, followers gained data from active contests table and add it to the acObj
                    pcObj.likes = 1340
                    pcObj.comments = 982
                    pcObj.followersgained = 982
                
                    pastContests.append(pcObj)

        if "Future" in contestsData:
            for i in contestsData['Future']:
                for ack, acv in i.iteritems():
                    #print(ac.keys)
                    fcObj = FutureContest()
                    fcObj.title = acv['title']
                    fcObj.description = acv['description']
                    fcObj.starttime = datetime.strptime(acv['starttime'], '%m/%d/%YT%H:%M:%SZ').strftime('%I:%M %p %b %d, %Y')
                    fcObj.endtime = datetime.strptime(acv['endtime'], '%m/%d/%YT%H:%M:%SZ').strftime('%I:%M %p %b %d, %Y')
                    fcObj.imageurl = acv['imageurl']
                    fcObj.contestid = ack
                    #TODO: get likes, comments, followers gained data from active contests table and add it to the acObj
                    fcObj.likes = 0
                    fcObj.comments = 0
                    fcObj.followersgained = 0
                
                    futureContests.append(fcObj)
                
    
    return render_template('dashboard.html', page_title="Dashboard", activeContests=activeContests, pastContests=pastContests, futureContests=futureContests)

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
        #get the data from the submit GA form
        gaS3PhotoUrl = awshelper.upload_image_to_s3(form.gaphoto)
        gaTitle = str(form.gatitle.data)
        gaType = str(form.gatype.data)
        gaDesc = str(form.gadescription.data)

        print gaTitle
        print gaS3PhotoUrl
        print gaType
        print gaDesc
        
        try:
            #TODO: figure out the starttime, by default lets keep starttime to one week from now and end time + 3 days from there.
            starttime = datetime.strftime(datetime.now() + timedelta(days=3),'%m/%d/%YT%H:00:00Z')
            endtime = datetime.strftime(datetime.now() + timedelta(days=10),'%m/%d/%YT%H:00:00Z')

            awshelper.add_contest(str(current_user.id), starttime, endtime, gaS3PhotoUrl, gaTitle, gaType, gaDesc)
        except:
            flash("There was some error processing your request. Please contact admin!")
            print("Unexpected Error : ", sys.exc_info()[0])
            raise
            
            return render_template('giveawayform.html', form=form, page_title="Submit Giveaway")
            

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
        