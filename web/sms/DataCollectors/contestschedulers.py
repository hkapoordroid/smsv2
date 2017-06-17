import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
import time
import datetime

ACCESS_KEY = 'AKIAISYC66Z4KPI2LEBQ'
SECRET_ACCESS_KEY = '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' 



def DataCollectorScheduler():
    '''
    This method scans all active contests and sends messages to data collection queues periodically
    '''
    try:
        dyndb = boto3.resource('dynamodb',
                                aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key = SECRET_ACCESS_KEY,
                                region_name='us-west-1')

        activeContestsTable = dyndb.Table('ActiveContests')
        
        resp = activeContestsTable.scan()

        completedContests = []
        
        #data collector queues
        sqs = boto3.resource('sqs',
                                aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key = SECRET_ACCESS_KEY,
                                region_name='us-west-1')
    
        commentsDataCollectorQueue = sqs.Queue('https://sqs.us-west-1.amazonaws.com/787766881935/CommentsDataCollectorQueue')
        followersDataCollectorQueue = sqs.Queue('https://sqs.us-west-1.amazonaws.com/787766881935/FollowersDataCollectorQueue')
        likesDataCollectorQueue = sqs.Queue('https://sqs.us-west-1.amazonaws.com/787766881935/LikesDataCollectorQueue')

        if resp['Count'] > 0:
            for i in resp['Items']:
                endTime = datetime.datetime.strptime(i['endtime'], "%m/%d/%YT%H:%M:%SZ")
                lastExtractionDate = datetime.datetime.strptime(i['lastextractiondate'], "%m/%d/%YT%H:%M:%SZ")
                if endTime < datetime.datetime.now():
                    completedContests.append(i)
                else:
                    if (datetime.datetime.now() - lastExtractionDate).seconds > 900:
                        print('Insert messages in the queues to collect the data')
                        commentsDataCollectorQueue.send_message(MessageBody=json.dumps(i))
                        followersDataCollectorQueue.send_message(MessageBody=json.dumps(i))
                        likesDataCollectorQueue.send_message(MessageBody=json.dumps(i))
                        


        """
        lets deal with completed contests
        1. Delete the contest from active contests
        2. Change status in the contests table
        3. Send message in the queue to select the winner
        """

        for c in completedContests:
            activeContestsTable.delete_item(
                                Key={
                                    'contestid' : c['contestid']
                                })

            contestsTable = dyndb.Table('Contests')
            contestsTable.update_item(
                                Key = { 'starttime' : c['startime'], 'email' : c['email'] },
                                UpdateExpression = 'set = status = :s',
                                ExpressionAttributeValues = { ':s' : 'Completed'},
                                ReturnValues = "NONE"    
                            )
            #insert message in to the queue to go select the winner


    except:
        raise


def ContestScheduler():
    '''
    This is the method which checks the Contest Table at start of every hour and finds all Contest which need to begin or end 
    and Updates Active Contest Tale accordingly. 
    '''
    try:
        dyndb = boto3.resource('dynamodb',
                                aws_access_key_id = ACCESS_KEY,
                                aws_secret_access_key = SECRET_ACCESS_KEY,
                                region_name='us-west-1')

        contestsTable = dyndb.Table('Contests')

        #get list of all contests which are supposed to start at this hour.
        startTime = time.strftime("%m/%d/%YT%H:00:00Z")

        resp = contestsTable.query(
                            KeyConditionExpression=Key('starttime').eq(startTime) 
        )

        #print(resp)

        #now insert tthe contests to active contest
        if int(resp['Count']) > 0:
            activeContestsTable = dyndb.Table('ActiveContests')

            with activeContestsTable.batch_writer() as batch:
                for i in resp['Items']:
                    item = {}
                    item['contestid'] = i['contestid']
                    item['email'] = i['email']
                    item['starttime'] = i['starttime']
                    item['endtime'] = i['endtime']
                    item['lastextractiondate'] = i['starttime']

                    batch.put_item(item)
                
            

        #TODO: scan the active contests table and remove all contests which have completed.        


    except:
        raise


if __name__ == "__main__":
    #ContestScheduler()
    DataCollectorScheduler()