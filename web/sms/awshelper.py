from uuid import uuid4
import os.path
from flask import current_app as app
from werkzeug.utils import secure_filename
from boto3.dynamodb.conditions import Key, Attr
import boto3
import json
import time
import datetime
import decimal

BUCKETNAME = "isharemystyle"
S3_BASEURL = "https://s3-us-west-1.amazonaws.com/isharemystyle/"

ACCESS_KEY = 'AKIAISYC66Z4KPI2LEBQ'
SECRET_ACCESS_KEY = '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' 


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def upload_image_to_s3(sourcefile):
    '''
        This method uploads the image to S3 as object and returns the url for it. Images are created as public for obvious reasons! 
    '''
    try:
        source_filename = secure_filename(sourcefile.data.filename)
        source_extension = os.path.splitext(source_filename)[1]
    
        destination_filename = uuid4().hex + source_extension

        #print('BUCKET NAME : ' + BUCKETNAME)
        #print('OBJECT KEY : ' + destination_filename)
    
        s3Client = boto3.client('s3', 
                                aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key = SECRET_ACCESS_KEY,
                                region_name='us-west-1')

        s3PutResponse = s3Client.put_object(Bucket=BUCKETNAME, 
                            Key=destination_filename,
                            Body=sourcefile.data.read(),
                            ACL="public-read")

        if s3PutResponse['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception

        return S3_BASEURL+destination_filename
    except:
        raise

def check_if_login_exists(email):
    '''
        This method checks if email exists in our database as login
    '''
    try:
        if not email:
            raise ValueError('Email cannot be empty')

        #get the dynamodb resource
        dyndb = boto3.resource('dynamodb', 
                                aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key = SECRET_ACCESS_KEY,
                                region_name='us-west-1'
                                )
        #get the Login table object
        loginTable = dyndb.Table('Login')

        #query the Login table
        loginData = loginTable.get_item(
                    Key={
                       'email' : email
                    }
                    )

        if loginData:
            return True
        else:
            return False
    except:
        raise

def verify_login(email, password):
    '''
        This method verified the login data against dynamodb 
    '''
    try:

        if not email or not password:
            raise ValueError('Email and password cannot be empty')

        #get the dynamodb resource
        dyndb = boto3.resource('dynamodb', 
                                aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key = SECRET_ACCESS_KEY,
                                region_name='us-west-1')
        #get the Login table object
        loginTable = dyndb.Table('Login')

        #get the login info from the Login table
        loginData = loginTable.get_item(
                    Key={
                       'email' : email
                    }
                    )

        if not loginData:
            return False

        if loginData['Item']['password'] == password:
            return True

        return False
        
    except:
        raise

def save_ig_user_and_auth_data(email, data):
    '''
    This method takes in dictionary of ig data and saves it to Login table as attributes
    input: email of the logged in user and IG Data dictionary
    '''
    try:
        #get the dynamodb resource
        dyndb = boto3.resource('dynamodb', 
                                aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key = SECRET_ACCESS_KEY,
                                region_name='us-west-1')
        #get the Login table object
        loginTable = dyndb.Table('Login')            

        #first get the item related to the email
        loginData = loginTable.get_item(
                    Key={
                        'email' : email
                    }
                    )

        if not loginData:
            raise StandardError('Unable to find the login')

        #remove all the attributes from ig data dictionary which have empty value
        dataToSave = dict((k, v) for k, v in data.iteritems() if v)

        #generate the update expression and expression attribute values dictionary
        updExp = ','.join((i+' = :'+i for i in dataToSave.keys()))
        expAttrVal = dict((':'+k, v) for k,v in dataToSave.iteritems())        

        updExp = 'set ' + updExp

        #print(updExp)
        #print('\n')
        #print(expAttrVal)

        response = loginTable.update_item(
                Key = {'email' : email},
                UpdateExpression=updExp,
                ExpressionAttributeValues=expAttrVal,
                ReturnValues = "NONE"
            )

        print(json.dumps(response, indent=4))
            
    except:
        raise

def get_user_contests(email):
    '''
        This method gets all contests for a given user
        input : email/username
        output: contest data in following structure
        { 'past/Active/future' : {
                                    [ 'contestid' : { starttime : value, endtime : endtime, title : title, type : type, description : description,imageurl : imageurl }
                                    ]
                                 }
        }
        
    '''
    try:
        if not email:
            raise ValueError('Email cannot be empty')

        #get the dynamodb resource
        dyndb = boto3.resource('dynamodb', 
                                aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key = SECRET_ACCESS_KEY,
                                region_name='us-west-1')

        #get the UserContests Table
        userContestsTable = dyndb.Table('UserContests')

        #get the data 
        userContestsData = userContestsTable.query(
                            KeyConditionExpression=Key('email').eq(email)
                            )

        
        contests = dict()
        #get the users contests data
        if userContestsData:
            for item in userContestsData['Items']:
                value = dict()
                starttime = datetime.datetime.strptime(item['starttime'], "%m/%d/%YT%H:00:00Z")
                endtime = datetime.datetime.strptime(item['endtime'], "%m/%d/%YT%H:00:00Z")
                
                value['starttime'] = item['starttime']
                value['endtime'] = item['endtime']
                value['title'] = item['title']
                value['type'] = item['type']
                value['description'] = item['description']
                value['imageurl'] = item['imageurl']

                contestValue = dict()
                contestValue[item['contestid']] = value
                
                if starttime <= datetime.datetime.now() and endtime >= datetime.datetime.now():
                    if 'Active' not in contests:
                        contests['Active'] = list()
                    contests['Active'].append(contestValue)
                elif starttime > datetime.datetime.now():
                    if 'Future' not in contests:
                        contests['Future'] = list()
                    contests['Future'].append(contestValue)
                elif endtime < datetime.datetime.now():
                    if 'Past' not in contests:
                        contests['Past'] = list()
                    contests['Past'].append(contestValue)                               
                
        return contests        

    except:
        raise

def add_contest(email, starttime, endttime, imageurl, title, type, description):
    try:
        #valid inputs
        if not email:
            raise ValueError("Email cannot be empty")

        if not starttime:
            raise ValueError("Start Time cannot be empty")

        if not endttime:
            raise ValueError("End Time cannot be empty")

        if not imageurl:
            raise ValueError("Image URL cannot be empty")

        if not title:
            raise ValueError("Title cannot be empty")

        if not type:
            raise ValueError("type cannot be empty")

        if not description:
            raise ValueError("Description cannot be empty")

        #get the dynamodb resource
        dyndb = boto3.resource('dynamodb', 
                                aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key = SECRET_ACCESS_KEY,
                                region_name='us-west-1')

        #get the UserContests Table
        userContestsTable = dyndb.Table('UserContests')

        #generate the item
        item = dict()
        item['email'] = email
        item['starttime'] = starttime
        item['endtime'] = endttime
        item['contestid'] = str(uuid4())
        item['imageurl'] = imageurl
        item['title'] = title
        item['type'] = type
        item['description'] = description
        item['status'] = 'Pending'

        resp1 = userContestsTable.put_item(Item=item)

        #get the contests Table
        contestsTable = dyndb.Table('Contests')

        print(json.dumps(resp1, indent=4, cls=DecimalEncoder))

        item.pop('imageurl')
        item.pop('title')
        item.pop('description')
        item.pop('type')        

        resp2 = contestsTable.put_item(Item=item)

        print(json.dumps(resp2, indent=4, cls=DecimalEncoder))
        
        

    except:
        raise


def UnitTest():
    contestsData = get_user_contests('hkapoordroid@gmail.com')
    print 'Got data'
    if contestsData:
        #lets get the active contests first
        if 'Active' in contestsData:
            for i in contestsData['Active']:
                for ack, acv in i.iteritems():
                    print ack
                    print acv['title']
                    #print(ac.keys)
                    #for k,v in acv.iteritems():
                    #acObj = ActiveContest(v['title'], v['description'], v['starttime'], 
                    #                        v['endttime'], k)

                    #activeContests.append(acObj)
    
    #print(check_if_login_exists('hkapoordroid@gmail.com'))
    #print(check_if_login_exists('test@test.com'))

if __name__ == "__main__":
    UnitTest()