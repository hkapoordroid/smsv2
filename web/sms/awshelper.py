from uuid import uuid4
import os.path
from flask import current_app as app
from werkzeug.utils import secure_filename
import boto3
import json

BUCKETNAME = "isharemystyle"
S3_BASEURL = "https://s3-us-west-1.amazonaws.com/isharemystyle/"

ACCESS_KEY = 'AKIAISYC66Z4KPI2LEBQ'
SECRET_ACCESS_KEY = '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' 

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


#def UnitTest():
#    print(check_if_login_exists('hkapoordroid@gmail.com'))
#    print(check_if_login_exists('test@test.com'))

#if __name__ == "__main__":
#    UnitTest()