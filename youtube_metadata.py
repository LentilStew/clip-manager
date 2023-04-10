

# import required modules
import random
import datetime


# define title templates
community_title_template = "Best Clips of {creator1}, {creator2} and more! - week {week_num} of {month} {year}"
streamer_title_template = "{streamer}'s Best Clips of {month} {year}"

# define description template
description_template = "Check out the best clips of {streamers}! Don't forget to show some love to the creators of these clips.\n\nTimestamps:\n"

# define tags list
tags = ["best_clips", "twitch", "stream_highlights"]

def generate_youtube_data(clips):
    # get current date
    today = datetime.date.today()
    week_num = today.strftime("%U")
    month = today.strftime("%B")
    year = today.strftime("%Y")

    # generate title based on video type and community or streamer name

    # select random creators from clips
    creators = list(set([clip['broadcaster_name'] for clip in clips]))
    random.shuffle(creators)

    if len(creators) > 1: 
        title = community_title_template.format(creator1=creators[0], creator2=creators[1], week_num=week_num, month=month, year=year)
    else:
        title = streamer_title_template.format(streamer=creators[0], month=month, year=year)

    # generate description
    description = description_template.format(streamers=" ".join(creators[:5]))

    # initialize variables to keep track of timestamp
    time_sum = 0
    # add clips to description
    for i, clip in enumerate(clips):
        # get duration of clip in seconds
        duration = int(clip['duration'])

        # calculate timestamp for clip
        time_sum += duration
        timestamp = datetime.timedelta(seconds=time_sum)

        # add clip information to description
        description += f"{i+1}. ({str(timestamp - datetime.timedelta(seconds=duration))} - {str(timestamp)}) {clip['url']} \n"
        
    # generate tag string
    tags_str = "#" + " #".join(tags + creators[:2])

    # return video information as a dictionary
    return {"title": title, "description": description, "tags": tags_str}
