"""
Routes and views for the igauthentication.
"""
from sms import app
from flask import redirect, request, url_for
from flask_login import current_user, login_required
import requests
import json
import awshelper


clientID = '26d2405a54464c8d93cc2cc786401246'
clientSecret = '3f6f68e1ab2841a9831f10bf6a13bcfd'
redirectUrl = 'http://127.0.0.1:5000/index'


@app.route('/igauth')
@login_required
def authenticate():
	igAuthUrl = 'https://api.instagram.com/oauth/authorize/?client_id='+clientID+'&redirect_uri='+redirectUrl+'&response_type=code&scope=basic+public_content+follower_list+comments+relationships+likes'

	#initialize the global variables and settings
	return redirect(igAuthUrl)

@app.route('/index')
@login_required
def index():
    code = request.args.get('code')
    r = requests.post('https://api.instagram.com/oauth/access_token', data={ 'client_id' : clientID, 
																			'client_secret' : clientSecret, 
																			'grant_type' : 'authorization_code', 
																			'redirect_uri' : redirectUrl,
																			'code' : code })

    resObj = json.loads(r.text)
    
    igData = {}

    #access token is must, should always be present
    igData['igAccessToken'] = resObj['access_token']
    igData['igUserID'] = resObj['user']['id']
    igData['igUserName'] = resObj['user']['username']
    igData['igProfilePic'] = resObj['user']['profile_picture']
    igData['igFullName'] = resObj['user']['full_name']
    igData['igBio'] = resObj['user']['bio']
    igData['igWebsite'] = resObj['user']['website']

	#save the ig data to the Login table as attributes
    awshelper.save_ig_user_and_auth_data(current_user.id, igData)

    return redirect(url_for('index_page'))


