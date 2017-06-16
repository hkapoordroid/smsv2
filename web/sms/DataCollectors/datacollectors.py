import boto3
import json
import urllib2
from uuid import uuid4
import datetime

ACCESS_KEY = 'AKIAISYC66Z4KPI2LEBQ'
SECRET_ACCESS_KEY = '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'
S3_BASEURL = "https://s3-us-west-1.amazonaws.com/" 


def saveDataToS3(bucketname, key, content, acl):
    '''
    Saves the data to the S3
    '''
    try:
        s3Client = boto3.client('s3', 
                                aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key = SECRET_ACCESS_KEY,
                                region_name='us-west-1')

        s3PutResponse = s3Client.put_object(Bucket=bucketname, 
                            Key=key,
                            Body=content,
                            ACL=acl)

        if s3PutResponse['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception

        return S3_BASEURL+bucketname+'/'+key
    except:
        raise

def getIGData(url):
    '''
    #	This method takes in url and return the response as json object
    '''
    try:
	    #r = requests.get(url)
        r = urllib2.urlopen(url)
        return json.load(r)
    except:
	    #TODO: logging
        raise

def getAccessToken(email):
    '''
    This method takes in user email and returns the IG access token for it.
    '''
    try:
        dyndb = boto3.resource('dynamodb', 
                                aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key = SECRET_ACCESS_KEY,
                                region_name='us-west-1'
                                )
        #get the Login table object
        loginTable = dyndb.Table('Login')

        #query the Login table and get the access token
        loginData = loginTable.get_item(
                    Key={
                       'email' : email
                    },
                    ProjectionExpression="igAccessToken"
                    )

        return loginData['Item']['igAccessToken']


    except:
        raise


def FollowersDataCollector(event, context):
    try:
        email = event['email']

        #get the access token
        accessToken = getAccessToken(email)

        #step 1: get the follower count
        urlFC = 'https://api.instagram.com/v1/users/self/?access_token={0}'.format(accessToken)
        print(urlFC)
        
        respFC = getIGData(urlFC)
        followerCount = int(respFC['data']['counts']['followed_by'])

        #step 2: get the followers names
        #maxId = '&max_id='+event['max_id'] if event['max_id'] else ''
        urlUN = 'https://api.instagram.com/v1/users/self/followed-by?access_token={0}'.format(accessToken)
        print(urlUN)

        followedByUsernames = list()
        #TODO: figure out the pagination of this response object
        respUN = getIGData(urlUN)
        for i in respUN['data']:
            followedByUsernames.append(i)

        #save the data to S3 and get the url
        key = uuid4().hex + '.json'
        fileUrl = saveDataToS3('isharemystyle', key, json.dumps(followedByUsernames), 'private') 

        #save the extraction data in dynamodb 
        dyndb = boto3.resource('dynamodb',
                                aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key = SECRET_ACCESS_KEY,
                                region_name='us-west-1')

        igUserFollowersMetricDataTable = dyndb.Table('IGUserFollowersMetricData')
        
        item = {} 
        item['email'] = email
        item['extractiondate'] = datetime.datetime.strftime(datetime.datetime.now(),'%m/%d/%YT%H:%M:%SZ')
        item['followercount'] = followerCount
        item['followerdataurl'] = fileUrl      

        igUserFollowersMetricDataTable.put_item(Item=item)
    
        return 'Done'
        

        

    except:
        raise
    

if __name__ == "__main__":
    event = json.loads('{"email": "hkapoordroid@gmail.com", "endtime": "06/13/2017T00:00:00Z", "lastextractiondate": "06/10/2017T21:00:00Z", "starttime": "06/10/2017T21:00:00Z", "contestid": "91E64888-D1AF-4B1A-A146-38AD2126362D"}')

    FollowersDataCollector(event, None)