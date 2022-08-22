from data_collection.helix import Twitch
import datetime
import json
client_id = ""
client_secret = ""
communities_path = ""
with open("settings.json", "r") as f:
    settings = json.load(f)
    client_id = settings["twitch"]["client_id"]
    client_secret = settings["twitch"]["client_secret"]
    communities_path = settings["communities"]["save_path"]

twitch = Twitch(client_id, client_secret)


class Community():
    def __init__(self, name, members, language="en"):
        self.name = name
        self.members = members
        self.language = language

        pass

    def get_best_community_clips(self, clips_to_get=10, members_to_get=10):
        clips = []
        count = 0
        for member in self.members[:members_to_get]:
            print(str(count) + "/" + str(len(self.members)))
            count += 1
            res = twitch.get_top_clips(member["id"], clips=clips_to_get)
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

        res = twitch.get_top_clips(
            self.members[day % top_members]["id"], clips=clips_to_get)

        return res

    def to_json(self):

        return self.__dict__


def load_community(path):
    with open(path, "r") as f:
        community = json.load(f)
        return Community(community["name"], community["members"])
