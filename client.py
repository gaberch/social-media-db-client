import mysql.connector
from mysql.connector import Error
import datetime
import base64
import sys



"""
What should the client be able to do?

    (a) A person should be able to initial a post on a topic
    (b) A person should be able to follow/join a group with another person
    (c) A person should be able to follow a topic
    (d) A person should be able to determine what posts have been added by people and/or topics that
    they are following since they last read from those people/topics
    (e) A person should be able to respond to a post with thumbs up/down and/or a response post.
    (f) Additional as appropriate ...


    - Define api rules (ie. --help printout?)
    - Clean up output when sending data to user
    - Create continous loop that waits for user commands until quit command

- Clean up ER diagram
- Load csv file into database
- Demo video

"""


# DB connection
try:
    connection = mysql.connector.connect(host='192.168.56.101',
                                         database='CourseProject',
                                         user='admin',
                                         password='admin')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        # print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        # print("You're connected to database: ", record)


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
def userCreatePost(authorID, inResponseToPostID='NULL', textContent='NULL', imageFile='NULL', linkContent='NULL', topicNameList=[]):

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


def userGetNotifications(userID):

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
    
    if len(resultrows) == 0:
        print("No new updates for this user since the last request")
    else:        
        print("postID    authorID      inResponseToPostID   creationTimeStamp    textContent               imageContent      linkContent")
        for row in resultrows:
            query = "INSERT INTO Seen(userID, postID) VALUES({},{})".format(userID, row[0])
            create_commit(query)

            row = list(row)
            for i in range(len(row)):
                row[i] = 'null' if row[i] == None else row[i]
                if i == 4 and row[i] != 'null':
                    row[i] = row[i][0:21] + "..."
                if i == 5 and row[i] != 'null':
                    row[i] = row[i][0:13] + "..."

            if(row[3] == 'null'):
                print("{:<8}  {:<12}  {:<19}  {:<19}  {:<24}  {:<16}  {}".format(row[0],row[1],row[2],row[3],row[4],row[5], row[6]))
            else:            
                print("{:<8}  {:<12}  {:<19}  {:<19}  {:<24}  {:<16}  {}".format(row[0],row[1],row[2],row[3].strftime('%Y-%m-%d %H:%M:%S'),row[4],row[5],row[6]))
        

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


def viewAllUsers():
    query = 'SELECT * FROM User'
    mycursor = connection.cursor()
    mycursor.execute(query)
    
    resultrows = mycursor.fetchall()
    if (resultrows == []):
        raise Exception('No users currently exist in system')
    
    print ("userID          username            Birth Date      Gender          Vocation        Religion")
    for row in resultrows:
        row = list(row)
        for i in range(len(row)):
            row[i] = 'null' if row[i] == None else row[i]
        if(row[2] == 'null'):
            print("{:<14}  {:<18}  {:<14}  {:<14}  {:<14}  {}".format(row[0],row[1],row[2],row[3],row[4],row[5]))
        else:            
            print("{:<14}  {:<18}  {:<14}  {:<14}  {:<14}  {}".format(row[0],row[1],row[2].strftime('%Y-%m-%d'),row[3],row[4],row[5]))


def viewAllPosts():
    query = 'SELECT * FROM Post'
    mycursor = connection.cursor()
    mycursor.execute(query)
    
    resultrows = mycursor.fetchall()
    if (resultrows == []):
        raise Exception('No posts currently exist in system')
    
    print ("postID    authorID      inResponseToPostID   creationTimeStamp    textContent               imageContent      linkContent")
    for row in resultrows:
        row = list(row)
        for i in range(len(row)):
            row[i] = 'null' if row[i] == None else row[i]
            if i == 4 and row[i] != 'null':
                row[i] = row[i][0:21] + "..."
            if i == 5 and row[i] != 'null':
                row[i] = row[i][0:13] + "..."

        if(row[3] == 'null'):
            print("{:<8}  {:<12}  {:<19}  {:<19}  {:<24}  {:<16}  {}".format(row[0],row[1],row[2],row[3],row[4],row[5], row[6]))
        else:            
            print("{:<8}  {:<12}  {:<19}  {:<19}  {:<24}  {:<16}  {}".format(row[0],row[1],row[2],row[3].strftime('%Y-%m-%d %H:%M:%S'),row[4],row[5],row[6]))


def viewAllTopics():
    query = 'SELECT * FROM Topic'
    mycursor = connection.cursor()
    mycursor.execute(query)
    
    resultrows = mycursor.fetchall()
    if (resultrows == []):
        raise Exception('No topics currently exist in system')
    
    print("Topics")
    for row in resultrows:
        print(row[0])


def userGetReactedPosts(userID):
    if not (userIDExists(userID)):
        raise Exception('Cannot create group: userID does not exist')

    query = """
        SELECT r.type,p.postID,p.authorID,p.inResponseToPostID,p.creationTimeStamp,p.textContent,p.imageContent,p.linkContent
        FROM Post p, Reaction r
        WHERE p.postID = r.postID AND r.userID={}
    """.format(userID)

    mycursor = connection.cursor()
    mycursor.execute(query)

    resultrows = mycursor.fetchall()
    if (resultrows == []):
        raise Exception('No reactions to any posts for this user')
    
    for row in resultrows:
        new_row = []
        for element in row:
            new_row.append(element)
        if new_row[6] != None:
            new_row[6] = new_row[6][0:17] + "..."

    print ("reaction        postID    authorID      inResponseToPostID   creationTimeStamp    textContent               imageContent      linkContent")
    for row in resultrows:
        row = list(row)
        for i in range(len(row)):
            row[i] = 'null' if row[i] == None else row[i]
            if i == 5 and row[i] != 'null':
                row[i] = row[i][0:21] + "..."
            if i == 6 and row[i] != 'null':
                row[i] = row[i][0:13] + "..."

        if(row[4] == 'null'):
            print("{:<14}  {:<8}  {:<12}  {:<19}  {:<19}  {:<24}  {:<16}  {}".format(row[0],row[1],row[2],row[3],row[4],row[5], row[6],row[7]))
        else:            
            print("{:<14}  {:<8}  {:<12}  {:<19}  {:<19}  {:<24}  {:<16}  {}".format(row[0],row[1],row[2],row[3],row[4].strftime('%Y-%m-%d %H:%M:%S'),row[5],row[6],row[7]))



# - ADMIN COMMANDS:
#     - addUser(userID, username, birthDate='NULL', gender='NULL', vocation='NULL', religion='NULL')
#     - addSubtopicMapping(topicName, subTopicName)
#     - viewAllPosts()
#     - viewAllUsers()
#     - viewAllTopics()


# - USER COMMANDS:
#     - userCreatePost(authorID, inResponseToPostID='NULL', textContent='NULL', imageFile='NULL', linkContent='NULL', topicNameList=[])
#     - userFollowTopic(userID, topicName)
#     - userReactPost(userID, postID, reaction)
#     - userFollowUser(followerID,followedID)
#     - userJoinGroup(userID, groupID)
#     - userCreateGroup(userID, groupName)
#     - userGetNotifications(userID)
#     - userGetReactedPosts(userID)


def man():
    print("""
Welcome to the social media client. Below are a list of commands available
for a specific user or for an administrator:

    Admin Commands:

    +    addUser(userID, username, birthDate, gender, vocation, religion)                                                           
    |    addUser: Adds a new user to system                                                                                         
    |        userID(INT), username(STRING): required arguments                                                                      
    |        birthDate("YYYY-MM-DD"), gender(STRING), vocation(STRING), religion(STRING) : optional arguments(default NULL)
    |    Example with one optional argument: addUser(1090, test_username, , ,student, )
    
    +    addSubtopicMapping(topicName, subTopicName)                                                                                
    |    addSubtopicMapping: Creates a subtopic relationship between two already existing topics                                    
    |        topicName(STRING), subTopicName(STRING): required arguments                                                            

    +    viewAllPosts()                                                                                                             
    |    viewAllPosts: Prints all available posts in the system                                                                     

    +    viewAllUsers()
    |    viewAllUsers: Prints all available users in the system

    +    viewAllTopics()
    |    viewAllTopics: Prints all available topics in the system


    User Commands:

    +    userCreatePost(authorID, inResponseToPostID, textContent, imageFile, linkContent, topicNameList)
    |    userCreatePost: Creates a post for specified user
    |        authorID(INT): required argument
    |        inResponseToPostID(INT), textContent(STRING), imageFile('Path/to/image/file'), linkContent(STRING), topicNameList([STRING,STRING,STRING...]): optional arguments
    |    Parameter Explanations:
    |        inResponseToPostID: postID of the post that you are responding to (in case you want to respond to a post)
    |        topicNameList: List of topic names (strings). Topic names to begin with a '#'. If topic does not exist, it will be automatically created.
    |    Example with one optional argument: userCreatePost(1,3, , , ,[#test_topic, #tp2, #tp3])
    |    Example with no optional argument: userCreatePost(1,3, , , ,[])
    |    Example with two optional argument: userCreatePost(1,3,this is my post text content ,path/to/my/image , ,[])

    +    userFollowTopic(userID, topicName)
    |    userFollowTopic: Adds an existing topic to the list of topics that this user is following
    |       userID(INT), topicName(STRING): required arguments

    +    userReactPost(userID, postID, reaction)
    |    userReactPost: Creates a reaction for specified user to specified post
    |       userID(INT), postID(INT), reaction(STRING): required arguments
        
    +    userFollowUser(followerID,followedID)
    |    userFollowUser: user with followerID Follows the user with followedID
    |        followerID(INT), followedID(INT): required arguments
        
    +    userJoinGroup(userID, groupID)
    |    userJoinGroup: Adds the user to an exisiting group
    |        userID(INT), groupID(INT): required arguments
        
    +    userCreateGroup(userID, groupName)
    |    userCreateGroup: Creates a group and adds the creator to the group
    |        userID(INT), groupName(STRING): required arguments
        
    +    userGetNotifications(userID)
    |    userGetNotifications: Prints all posts with the topics or autherID's that the current user is following and has not seen yet
    |        userID(INT): required arguments
        
    +    userGetReactedPosts(userID)
    |    userGetReactedPosts: Prints all posts that the requested user has reacted to
    |        userID(INT): required argument

    
To quit program, type 'quit()' and hit Enter. To see the manual again type 'manual()' and hit Enter!
For any other commands, follow the manual above!
"""
    )


man()

while True:
    sys.stdout.write(": ")
    sys.stdout.flush()
    line = sys.stdin.readline()

    try:

        if line.startswith('quit'):
            break

        elif line.startswith('manual()'):
            man()

        elif line.startswith('addUser'):
            result = [x.strip() for x in line[line.find("(")+1:line.find(")")].split(',')]
            if len(result) != 6:
                raise Exception('The number arguments given for addUser command is not 6')

            userID, username, gender, vocation, religion = int(result[0]), result[1], result[3], result[4], result[5]
            birthDate = ''
            if(result[2] != ''):
                birthDate = datetime.datetime.strptime(result[2], '%Y-%m-%d')

            if gender == '':
                gender = 'NULL'
            if vocation == '':
                vocation = 'NULL'
            if religion == '':
                religion = 'NULL'
            if birthDate == '':
                birthDate = 'NULL'

            addUser(userID,username,birthDate,gender,vocation,religion)
            print('User added successfully!')

        elif line.startswith('addSubtopicMapping'):
            result = [x.strip() for x in line[line.find("(")+1:line.find(")")].split(',')]
            topicName, subTopicName = result[0], result[1]      
            addSubTopicMapping(topicName, subTopicName)
            print("Sub topic mapping added successfully")

        elif line.startswith('viewAllPosts()'):
            viewAllPosts()
        
        elif line.startswith('viewAllUsers()'):
            viewAllUsers()

        elif line.startswith('viewAllTopics()'):
            viewAllTopics()
        
        elif line.startswith('userCreatePost'):
            if line.find("[") == -1:
                raise Exception('topicNameList or empty list not added')
                
            firstPart = line[0:line.find("[")]
            result = [x.strip() for x in firstPart[firstPart.find("(")+1:firstPart.find(")")].split(',')]

            if len(result) < 5:
                raise Exception('Not enough arguments given for userCreatePost command')
            
            topicNameList = [x.strip() for x in line[line.find("[")+1:line.find("]")].split(',')]
            authorID, inResponseToPostID, textContent, imageFile, linkContent = result[0], result[1], result[2], result[3], result[4]
            
            if inResponseToPostID == '':
                inResponseToPostID = 'NULL'
            if textContent == '':
                textContent = 'NULL'
            if imageFile == '':
                imageFile = 'NULL'
            if linkContent == '':
                linkContent = 'NULL'
            
            if topicNameList[0] == '':
                topicNameList = []
            
            userCreatePost(authorID,inResponseToPostID,textContent,imageFile,linkContent,topicNameList)
            print("Post created successfully")
           
        elif line.startswith('userFollowTopic'):   
           result = [x.strip() for x in line[line.find("(")+1:line.find(")")].split(',')]
           userID, topicName = int(result[0]), result[1]
           userFollowTopic(userID, topicName)
           print("user followed the specified topic successfully")

        elif line.startswith('userReactPost'):
            result = [x.strip() for x in line[line.find("(")+1:line.find(")")].split(',')]
            userID, postID, reaction = int(result[0]), int(result[1]), result[2]
            userReactPost(userID, postID, reaction)
            print("user reacted the specified post successfully")

        elif line.startswith('userFollowUser'):
            result = [x.strip() for x in line[line.find("(")+1:line.find(")")].split(',')]
            followerID, followedID = int(result[0]), int(result[1])
            userFollowUser(followerID, followedID)
            print("user with followerID followed the user with followedID successfully")

        elif line.startswith('userJoinGroup'):
            result = [x.strip() for x in line[line.find("(")+1:line.find(")")].split(',')]
            userID, groupID = int(result[0]), int(result[1])
            userJoinGroup(userID, groupID)
            print("user joined the group successfully")

        elif line.startswith('userCreateGroup'):
            result = [x.strip() for x in line[line.find("(")+1:line.find(")")].split(',')]
            userID, groupName = int(result[0]), result[1]
            userCreateGroup(userID, groupName)
            print("user created and joined the group successfully")

        elif line.startswith('userGetNotifications'):
            result = [x.strip() for x in line[line.find("(")+1:line.find(")")].split(',')]
            userID = int(result[0])
            userGetNotifications(userID)

        elif line.startswith('userGetReactedPosts'):
            result = [x.strip() for x in line[line.find("(")+1:line.find(")")].split(',')]
            userID = int(result[0])
            userGetReactedPosts(userID)
            
        else:
            print('Invalid Command!')
            
    except Exception as err:
            sys.stderr.write("Error: " + str(err) + "\n")

if (connection.is_connected()):
    cursor.close()
    connection.close()
    # print("MySQL connection is closed")

