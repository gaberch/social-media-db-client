import mysql.connector
from mysql.connector import Error
import datetime
import base64


"""
What should the client be able to do?

    (a) A person should be able to initial a post on a topic
    (b) A person should be able to follow/join a group with another person
    (c) A person should be able to follow a topic
    (d) A person should be able to determine what posts have been added by people and/or topics that
    they are following since they last read from those people/topics
    (e) A person should be able to respond to a post with thumbs up/down and/or a response post.
    (f) Additional as appropriate ...

"""


# DB connection
try:
    connection = mysql.connector.connect(host='192.168.56.101',
                                         database='CourseProject',
                                         user='admin',
                                         password='admin')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)


except Error as e:
    print("Error while connecting to MySQL", e)


def create_commit(query):
    if not connection.is_connected():
        raise Exception('No connection to db when attempting to add user')
    connection.cursor().execute(query)
    connection.commit()

# Check if userID exists
def userIDExists(userID):
    query = "SELECT COUNT(*) FROM User WHERE userID={}".format(userID)
    mycursor = connection.cursor()
    mycursor.execute(query)
    return(mycursor.fetchone()[0] != 0)

# Check if Topic Exists
def topicNameExists(topicName):
    query = "SELECT COUNT(*) FROM Topic WHERE topicName='{}'".format(topicName)
    mycursor = connection.cursor()
    mycursor.execute(query)
    return (mycursor.fetchone()[0] != 0)


def postIDExists(postID):
    query = "SELECT COUNT(*) FROM Post WHERE postID={}".format(postID)
    mycursor = connection.cursor()
    mycursor.execute(query)
    return(mycursor.fetchone()[0] != 0)


def groupExists(groupID):
    query = "SELECT COUNT(*) FROM Club WHERE groupID={}".format(groupID)
    mycursor = connection.cursor()
    mycursor.execute(query)
    return(mycursor.fetchone()[0] != 0)

# Add User function
def addUser (userID, username, birthDate='NULL', gender='NULL', vocation='NULL', religion='NULL'):

    if(userIDExists(userID)):
        raise Exception ('userID already exists')

    username = "'" + username + "'"
    if (birthDate != 'NULL'):
        birthDate = "'" + birthDate.strftime('%Y-%m-%d') + "'"
    if (gender != 'NULL'):
        gender = "'" + gender + "'"
    if (vocation != 'NULL'):
        vocation = "'" + vocation + "'"
    if (religion != 'NULL'):
        religion = "'" + religion + "'"

    query = """ INSERT INTO User(userID, username, birthDate, gender, vocation, religion)
    VALUES ({},{},{},{},{},{})""".format(userID, username, birthDate, gender, vocation, religion)

    create_commit(query)

# Image file to long blob
def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = base64.b64encode(file.read()).decode("utf-8")
        file.close()
    return binaryData

# Create a post
def createPost(authorID, inResponseToPostID='NULL', textContent='NULL', imageFile='NULL', linkContent='NULL', topicNameList=[]):

    # validate authorID
    if not (userIDExists(authorID)):
        raise Exception ('Failed to create post: userID does not exist')

    # validate inResponseToPostID
    if (inResponseToPostID != 'NULL'):
        if not (postIDExists(inResponseToPostID)):
            raise Exception ('Failed to create post: postID does not exist for inResponseToPostID')
    

    # new postID
    query = """SELECT MAX(postID) FROM Post"""
    mycursor = connection.cursor()
    mycursor.execute(query)
    result = mycursor.fetchone()[0]


    newPostID=0
    if(result != None):
        newPostID = result + 1
    
    # Create userID - topic connection
    creationTime = datetime.datetime.now()   
    creationTimeStamp = "'" + creationTime.strftime('%Y-%m-%d %H:%M:%S') + "'"

    
    if (textContent != 'NULL'):
        textContent = '"' + textContent + '"'
    if (imageFile != 'NULL'):
        imageContent = "'" + convertToBinaryData(imageFile) + "'"
    else:
        imageContent = 'NULL'
    if (linkContent != 'NULL'):
        linkContent = "'" + linkContent + "'"


    query = """ INSERT INTO Post(postID, authorID, inResponseToPostID, creationTimeStamp, textContent, imageContent, linkContent)
    VALUES ({},{},{},{},{},{},{})""".format(newPostID, authorID, inResponseToPostID, creationTimeStamp, textContent, imageContent, linkContent)

    create_commit(query)

    # Check existence of topics in Topic table, adding them if needed, adding mapping between topics and posts
    for topicName in topicNameList:

        if not (topicNameExists(topicName)):
            query = "INSERT INTO Topic(topicName) VALUES('{}')".format(topicName)
            create_commit(query)

        query = "INSERT INTO PostTopicMapping(postID,topicName) VALUES({},'{}')".format(newPostID,topicName)
        create_commit(query) 

# User follows topic
def userFollowTopic(userID, topicName):
    
    if not (userIDExists(userID)):
        raise Exception ('Failed to Follow Topic: User ID does not exist')

    if not (topicNameExists(topicName)):
        raise Exception ('Failed to Follow Topic: Topic Name does not exist')

    query = 'SELECT COUNT(*) FROM TopicFollowing WHERE userID={} AND topicName="{}"'.format(userID, topicName)
    mycursor = connection.cursor()
    mycursor.execute(query)
    if (mycursor.fetchone()[0] != 0):
        raise Exception ('Failed to Follow Topic: User is already following this topic')

    query = "INSERT INTO TopicFollowing(userID, topicName) VALUES ({}, '{}')".format(userID, topicName)
    create_commit(query)

    
def userReactPost(userID, postID, reaction):
    # validate userID
    if not (userIDExists(userID)):
        raise Exception ('Failed to React to Post: User ID does not exist')

    # validate postID
    if not (postIDExists(postID)):
        raise Exception ('Failed to React to Post: Post ID does not exist')


    # update reaction if previously already reacted
    query = 'SELECT COUNT(*) FROM Reaction WHERE userID={} AND postID={}'.format(userID, postID)
    mycursor = connection.cursor()
    mycursor.execute(query)
    if (mycursor.fetchone()[0] != 0):
        query = 'UPDATE Reaction SET type="{}" WHERE userID={} AND postID={}'.format(reaction, userID, postID)
    else:
        query = 'INSERT INTO Reaction(userID,postID,type) VALUES({},{},"{}")'.format(userID, postID, reaction)
    create_commit(query)


def userFollowUser(followerID,followedID):
    if not userIDExists(followerID):
        raise Exception('Could not follow user: followerID does not exist')
    if not userIDExists(followedID):
        raise Exception('Could not follow user: followed userID does not exist')
        
    query = "SELECT COUNT(*) FROM UserFollowing WHERE followerID={} AND followedID={}".format(followerID,followedID)
    mycursor = connection.cursor()
    mycursor.execute(query)
    if (mycursor.fetchone()[0] != 0):
        raise Exception('Current user is already following the other user')
    
    query = "INSERT INTO UserFollowing(followerID, followedID) VALUES({},{})".format(followerID,followedID)
    create_commit(query)


def userJoinGroup(userID, groupID):
    if not (userIDExists(userID)):
        raise Exception('Cannot join group: userID does not exist')
    
    if not (groupExists(groupID)):
        raise Exception('Cannot join group: groupID does not exist')

    query = "SELECT COUNT(*) FROM UserGroupMapping WHERE userID={} AND groupID={}".format(userID, groupID)
    mycursor = connection.cursor()
    mycursor.execute(query)
    if (mycursor.fetchone()[0] != 0):
        raise Exception('Current user is already in group')

    query = "INSERT INTO UserGroupMapping(userID, groupID) VALUES({},{})".format(userID, groupID)
    create_commit(query)
    

def userCreateGroup(userID, groupName):
    if not (userIDExists(userID)):
        raise Exception('Cannot create group: userID does not exist')
    
    query = """SELECT MAX(groupID) FROM Club"""
    mycursor = connection.cursor()
    mycursor.execute(query)
    result = mycursor.fetchone()[0]
    groupID=0
    if(result != None):
        groupID = result + 1

    query = "INSERT INTO Club(groupID, groupName) VALUES({},'{}')".format(groupID, groupName)
    create_commit(query)
    userJoinGroup(userID, groupID)


def getUpdates(userID):

    if not (userIDExists(userID)):
        raise Exception('Cannot get updated: userID does not exist')

    query = """
        SELECT *
        FROM Post
        WHERE postID IN (
            SELECT postID
            FROM (
                SELECT postID
                FROM PostTopicMapping
                WHERE topicName IN (
                    SELECT topicName
                    FROM TopicFollowing
                    WHERE userID={}
                )
                UNION DISTINCT
                SELECT postID
                FROM Post
                WHERE authorID IN (
                    SELECT followedID
                    FROM UserFollowing
                    WHERE followerID={}
                )
            ) AS postsThatIFollow
            WHERE postID NOT IN (
                SELECT postID
                FROM Seen
                WHERE userID={}
            )
        )
    """.format(userID, userID, userID)

    mycursor = connection.cursor()
    mycursor.execute(query)
    resultrows = mycursor.fetchall()
    
    for row in resultrows:
        print(row)
        query = "INSERT INTO Seen(userID, postID) VALUES({},{})".format(userID, row[0])
        create_commit(query)
        

def addSubTopicMapping(topicName, subTopicName):
    if not (topicNameExists(topicName)):
        raise Exception('Cannot add SubTopic Mapping: topicName does not exist')

    if not (topicNameExists(subTopicName)):
        raise Exception('Cannot add SubTopic Mapping: subTopicName does not exist')

    query = "SELECT COUNT(*) FROM SubTopicMapping WHERE topicName='{}' AND subTopicName='{}'".format(topicName, subTopicName)
    mycursor = connection.cursor()
    mycursor.execute(query)
    if (mycursor.fetchone()[0] != 0):
        raise Exception('SubTopic Mapping already exists')

    query = "INSERT INTO SubTopicMapping(topicName, subTopicName) VALUES('{}','{}')".format(topicName,subTopicName)
    create_commit(query)


# addUser(birthDate=datetime.date(2020, 3, 23), userID=1, username='theOriginal', gender='female', vocation='sex worker')
# createPost(authorID=1, textContent="The weather is amazing but we cant go out" ,inResponseToPostID=0, topicNameList=["#Superman", "#Batman"])
# createPost(authorID=1231, textContent="Summer is coming!!" ,inResponseToPostID=0, topicNameList=["#Dogs"])
# userFollowTopic(1231,'#Discrimination')
# userReactPost(1231,2,'Hate')
# userFollowUser(1,1231)
# userCreateGroup(1,"Sex Workers Annonymous")
# userJoinGroup(1231, 0)
# getUpdates(1231)
# addSubTopicMapping("#Superheroes","#Batman")
# addSubTopicMapping("#Superheroes","#Superman")


if (connection.is_connected()):
    cursor.close()
    connection.close()
    print("MySQL connection is closed")
