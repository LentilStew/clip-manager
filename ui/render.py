from firestore import get_clips_from_firestore, save_clip_to_firestore
import streamlit as st
import datetime
from settings import SETTINGS
from get_videos import make_community_general_videos,make_community_member_videos, get_communities,load_cached_communities




def render_clip_settings():
    
    st.header("Settings")
    with st.expander("video making settings"):
        col1, col2 = st.columns(2)
        settings = st.session_state["settings"]
        with col1:
            settings['max_video_duration'] = st.number_input('Max video duration (seconds)', min_value=1, value=settings['max_video_duration'], step=1)
            settings['framerate'] = st.number_input('Framerate', min_value=1, value=settings['framerate'], step=1)
            settings['video_width'] = st.number_input('Video width', min_value=1, value=settings['video_width'], step=1)
            settings['video_height'] = st.number_input('Video height', min_value=1, value=settings['video_height'], step=1)
            
        with col2:
            settings['output_options']['vcodec'] = st.text_input('Output video codec', value=settings['output_options']['vcodec'])
            settings['output_options']['crf'] = st.text_input('Output video CRF', value=settings['output_options']['crf'])
            settings['output_options']['acodec'] = st.text_input('Output audio codec', value=settings['output_options']['acodec'])
            settings['output_options']['f'] = st.text_input('Output video format', value=settings['output_options']['f'])
            
            settings['clip_options']['vcodec'] = st.text_input('Video decoder', value=settings['clip_options']['vcodec'])
            settings['clip_options']['acodec'] = st.text_input('Audio decoder', value=settings['clip_options']['acodec'])
            
        settings['community_video'] = st.checkbox('Generate community video', value=settings['community_video'])
        settings['clips_to_get'] = st.number_input('Number of clips to get', min_value=1, value=settings['clips_to_get'], step=1)
        settings['members_to_get'] = st.number_input('Number of members to get', min_value=1, value=settings['members_to_get'], step=1)
        settings['member_video'] = st.checkbox('Generate member video', value=settings['member_video'])
        settings['member_clips_to_get'] = st.number_input('Number of member clips to get', min_value=1, value=settings['member_clips_to_get'], step=1)
        settings['member_top_members'] = st.number_input('Number of top members to include', min_value=1, value=settings['member_top_members'], step=1)


        
def as_code(text:str):
    return "```python\n"+text+"\n```"

def render_clips(clips):
    for clip in clips:
        with st.expander(clip["title"]):
            st.title(clip["title"])
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Tags")
                st.write(as_code(' '.join(clip["tags"])))
                st.write(as_code(clip["description"]))

            with col2:
                st.subheader("FFmpeg Data")
                st.write(as_code(clip["ffmpeg_command"]))

                
def render_page():
    
    st.set_page_config(layout="wide")

    st.header('Clips 🎬')
    
    if "date" not in st.session_state:
        st.session_state["date"] = datetime.datetime.now()
    if "settings" not in st.session_state:
        st.session_state["settings"] = SETTINGS.copy()

    if "show_video_settings" not in st.session_state:
        st.session_state["show_video_settings"] = True    
        
    st.date_input(label="Clips date",key="date")
    
    with st.spinner('Finding clips'):
        clips = get_clips_from_firestore(st.session_state["date"])  
        if clips:
            render_clips(clips)
        else:
            st.header("No clips found 🤷‍♂️")
        

        