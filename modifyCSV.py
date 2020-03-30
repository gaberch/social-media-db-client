# fo = open("../twitterDataset/dataUpdated.csv", "r")

# wo = open("../twitterDataset/User.csv", "w")               # 40,001           # 570
# wo = open("../twitterDataset/TopicFollowing.csv", "w")     # 40,802           # 577
# wo = open("../twitterDataset/UserFollowing.csv", "w")      # 32,887,246       # 634

# def findnth(haystack, needle, n):
#     parts= haystack.split(needle, n+1)
#     if len(parts)<=n+1:
#         return -1
#     return len(haystack)-len(parts[-1])-len(needle)

# newLine = line[0:findnth(line,'[',0)].replace(',', ';') + line[findnth(line,'[',0):1+findnth(line,']',0)] + line[1+findnth(line,']',0):findnth(line,'[',1)].replace(',', ';') + line[findnth(line,'[',1):]

# for i in range(40001):
#     line = fo.readline()

#     id = line[0:findnth(line,';',0)].strip()
#     userName = line[1+findnth(line,';',0):findnth(line,';',1)].strip()
#     topics = [x.strip() for x in line[1+findnth(line,'[',0):findnth(line,']',0)].split(',')]
#     friends = [x.strip() for x in line[1+findnth(line,'[',1):findnth(line,']',1)].split(',')]

#     # if(i != 0):
#     #     for topic in topics:
#     #           wo.write(id.replace('"', '').replace("'", "'") + ',' + topic.replace('"', '').replace("'", "'") + '\n')
#     # else:
#     #       wo.write('userID,topicName\n')

#     # if(i != 0):
#     #     wo.write(id.replace('"', '').replace("'", "'") + ',' + userName.replace('"', '').replace("'", "'") + '\n')
#     # else:
#     #     wo.write('userID,username\n')
    
#     # if(i != 0):
#     #     for friend in friends:
#     #           wo.write(id.replace('"', '').replace("'", "'") + ',' + friend.replace('"', '').replace("'", "'") + '\n')
#     # else:
#     #       wo.write('followerID,followedID\n')



# userIDsSet = set()

# fo = open("../twitterDataset/User.csv", "r")
# wo = open("../twitterDataset/UserRefined.csv", "w")

# for i in range(40001):
#     line = fo.readline()
#     userID = line[0:line.find(',')].strip()
#     userName = line[1+line.find(','):-1].strip()
#     if(i!=0):
#         if((len(userID) <= 8) and (int(userID) <= 16000000)):
#             wo.write(userID + ',' + userName + '\n')
#             userIDsSet.add(int(userID))
#     else:
#         wo.write(userID + ',' + userName + '\n')


# fo = open("../twitterDataset/TopicFollowing.csv", "r")
# wo = open("../twitterDataset/TopicFollowingRefined.csv", "w")

# for i in range(40802):
#     line = fo.readline()
#     userID = line[0:line.find(',')].strip()
#     topicName = line[1+line.find(','):-1].strip()
#     if(i!=0):
#         if((len(userID) <= 8) and (int(userID) <= 16000000)):
#             wo.write(userID + ',' + topicName + '\n')
#     else:
#         wo.write(userID + ',' + topicName + '\n')


# fo = open("../twitterDataset/UserFollowing.csv", "r")
# wo = open("../twitterDataset/UserFollowingRefined.csv", "w")

# for i in range(32887246):
#     line = fo.readline()
#     followerID = line[0:line.find(',')].strip()
#     followedID = line[1+line.find(','):-1].strip()
#     if(i!=0):
#         if(((len(followerID) <= 8) and (int(followerID) <= 16000000)) and ((len(followedID) <= 8) and (int(followedID) <= 16000000))):
#             if((int(followerID) in userIDsSet) and (int(followedID) in userIDsSet)):
#                 wo.write(followerID + ',' + followedID + '\n')
#     else:
#         wo.write(followerID + ',' + followedID + '\n')
