from data_collection.helix import Twitch
import datetime
import json

class Member():
    id = None
    name = None
    size = 0

class Community():
    def __init__(self,twitch:Twitch, name=None, members=[], language="en"):
        self.name:str = name
        self.members:list = members
        self.language:str = language
        self.twitch  = twitch
        pass

    def add_member(self,member:Member):
        self.members.append(member)

    def get_member_ids(self):
        member_names = [member.name for member in self.members]
        ids:dict = self.twitch.get_user_ids(member_names)

        for member in self.members:
            member.id = ids.get(member.name, None)

    def get_best_community_clips(self, clips_to_get=10, members_to_get=10):

        self.members = sorted(self.members, key=lambda member: member.size, reverse=True)

        clips = []
        count = 0

        for member in self.members[:members_to_get]:
            if(not member.id):
                print("Member", member.name, "has no id")
                continue

            count += 1
            res = self.twitch.get_top_clips(member.id, clips=clips_to_get)
            clips.extend(res)
            
        # sort clips by views
        clips.sort(key=lambda x: x["view_count"], reverse=True)

        return clips

    def get_best_member_clips(self, clips_to_get=10, top_members=10):
        # get todays day number of the year
        day = datetime.datetime.now().timetuple().tm_yday
        if top_members > len(self.members):
            top_members = len(self.members)
            print("Top members number is greater than the number of members in the community. Setting top_members to " + str(top_members))

        res = self.twitch.get_top_clips(self.members[day % top_members].id, clips=clips_to_get, started_at=datetime.datetime.now() - datetime.timedelta(days=30))

        return res

    def to_json(self):

        return self.__dict__


def load_community(path):
    with open(path, "r") as f:
        community = json.load(f)
        return Community(community["name"], community["members"])
