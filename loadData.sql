use CourseProject;

LOAD DATA LOCAL INFILE './refinedTwitterDataset/UserRefined.csv'
	INTO TABLE User
	FIELDS TERMINATED BY ','
	LINES TERMINATED BY '\n'
	IGNORE 1 ROWS
    (@userID, @username)
    SET 
    userID=@userID,
    username=@username;

LOAD DATA LOCAL INFILE './refinedTwitterDataset/TopicFollowingRefined.csv'
	INTO TABLE Topic
	FIELDS TERMINATED BY ','
	LINES TERMINATED BY '\n'
	IGNORE 1 ROWS
    (@userID, @topic)
    SET 
    topicName=@topic;

LOAD DATA LOCAL INFILE './refinedTwitterDataset/TopicFollowingRefined.csv'
	INTO TABLE TopicFollowing
	FIELDS TERMINATED BY ','
	LINES TERMINATED BY '\n'
	IGNORE 1 ROWS
    (@userID, @topic)
    SET 
    userID=@userID,
    topicName=@topic;

LOAD DATA LOCAL INFILE './refinedTwitterDataset/UserFollowingRefined.csv'
	INTO TABLE UserFollowing
	FIELDS TERMINATED BY ','
	LINES TERMINATED BY '\n'
	IGNORE 1 ROWS
    (@followerID, @followedID)
    SET 
    followerID=@followerID,
    followedID=@followedID;
 