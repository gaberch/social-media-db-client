# Social Media Database Client

This is a simple Python3 and MySQL implementation that contains code client meant to act as a command line interface for social media users. When running `client.py`, the following commands are available:

```
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
```

Additional to the client, a `socialMedia.sql` file was developed to create the appropriate database for the client and a `loadData.sql` file was provided to load in example data. The original dataset, which was later modified for the purposes of this project, was downloaded from the [Twitter Friends Project](https://www.kaggle.com/hwassner/TwitterFriends) on the Kaggle platform.

Note: In order for you to run this project locally you must have a local running instance of MySQL and update variables `host`, `user`, `admin` from lines 10-13 of `client.py` with the appropriate connection information for your local MySQL running instance.
