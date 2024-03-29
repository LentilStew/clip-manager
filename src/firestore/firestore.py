from google.cloud import firestore
from typing import Union
import datetime
from settings import SETTINGS

db = firestore.Client.from_service_account_info(SETTINGS["firebase-key"])


def get_clips_from_firestore(date: Union[datetime.date, str, datetime.datetime] = None) -> list:
    if date is None:
        date = datetime.datetime.now()
    if not isinstance(date, str):
        date = date.strftime("%d-%m-%y")

    doc_ref = db.collection("clips").document(date)

    doc = doc_ref.get()

    if doc.exists:
        return doc.to_dict()["Videos"]

    return []

# Saves clip-data to firestore


def save_clip_to_firestore(clip_data: Union[dict, list], date: Union[datetime.datetime, str] = None):
    if date is None:
        date = datetime.datetime.now()
    if not isinstance(date, str):
        date = date.strftime("%d-%m-%y")

    if not isinstance(clip_data, list):
        clip_data = [clip_data]

    clips_ref = db.collection('clips')

    today_doc = clips_ref.document(date).get()

    if not today_doc.exists:
        clips_ref.document(date).set({'Videos': []})
        today_doc = clips_ref.document(date).get()

    clips = today_doc.get('Videos')
    for clip in clip_data:
        clips.append({
            'title': clip.get('title', ""),
            'description': clip.get('description', ""),
            'tags': clip.get('tags', "").split(" "),
            'ffmpeg_command': clip.get('ffmpeg_command', ""),
            'community_class': clip.get('community_class', ""),
            "id": clip.get('id', "")
        })

    clips_ref.document(date).update({'Videos': clips})


def change_video_status(video_id, uploaded:bool=True,date: Union[datetime.datetime, str] = None ) ->bool:
    if date is None:
        date = datetime.datetime.now()
    
    if not isinstance(date, str):
        date = date.strftime("%d-%m-%y")
    
    clips_ref = db.collection('clips')

    today_doc = clips_ref.document(date).get()

    if not today_doc.exists:
        return False

    clips = today_doc.get('Videos')
    for clip in clips:
        if clip['id'] == video_id:
            clip['uploaded'] = uploaded
            break

    clips_ref.document(date).update({'Videos': clips})

    return True
# Test
# save_clip_to_firestore(date="22-04-23", clip_data={"title": "VALORANT's Best Clips of April 2023", "description": "Check out the best clips of VALORANT! Don't forget to show some love to the creators of these clips.\n\nTimestamps:\n1. (0:00:00 - 0:00:17) https://clips.twitch.tv/AthleticThirstyWoodpeckerPanicVis-WPbGtqSyY1FjXFHI \n2. (0:00:17 - 0:00:42) https://clips.twitch.tv/SuaveColdMonkeyBlargNaut-nmw4WXFYCCIoYve9 \n3. (0:00:42 - 0:01:07) https://clips.twitch.tv/BreakableOilyPieFunRun-i5vFrL5PZYEZto4_ \n4. (0:01:07 - 0:01:36) https://clips.twitch.tv/GrotesqueFantasticAlpacaEleGiggle-VXvftB3p2vphWw05 \n5. (0:01:36 - 0:02:03) https://clips.twitch.tv/TardyTsundereHyenaRickroll-8kwxaFwXkVxeB8T6 \n6. (0:02:03 - 0:03:03) https://clips.twitch.tv/PreciousSucculentSpindleWow-MIoaY6o7dYKIEBmW \n7. (0:03:03 - 0:03:32) https://clips.twitch.tv/ScrumptiousSleepyAppleBatChest-Q-jimg8Gn_TdCK3H \n8. (0:03:32 - 0:03:36) https://clips.twitch.tv/SavoryUgliestBearTBTacoLeft-sEhbQHE5Q8w-sY_y \n9. (0:03:36 - 0:03:45) https://clips.twitch.tv/FrigidTubularPangolinSpicyBoy-pGnpGWOjHiQ_5oC9 \n10. (0:03:45 - 0:04:01) https://clips.twitch.tv/TransparentCallousGerbilAMPEnergy-9L99KSrZletkdKgm \n11. (0:04:01 - 0:04:30) https://clips.twitch.tv/WiseImportantRabbitDxCat-54MBFLeiaMTaMhu0 \n12. (0:04:30 - 0:04:55) https://clips.twitch.tv/ProudAwkwardWaterCopyThis-4O3Ld5hSyxpCGhx9 \n13. (0:04:55 - 0:05:22) https://clips.twitch.tv/WiseBlazingButterOMGScoots-QNX1VfasiXpJhlMq \n14. (0:05:22 - 0:05:26) https://clips.twitch.tv/CooperativeLitigiousSparrowDendiFace-AInOMYnfEA8O62sp \n15. (0:05:26 - 0:05:34) https://clips.twitch.tv/ExcitedGentleEndivePlanking-0nLBhbFbdLjPMf7s \n16. (0:05:34 - 0:06:00) https://clips.twitch.tv/CourteousVastMagpieDatSheffy-LdVX9S9D3Znjv3GE \n17. (0:06:00 - 0:06:10) https://clips.twitch.tv/BumblingFunnyDogeWutFace-Et52WqeVdNY8d6DU \n18. (0:06:10 - 0:06:22) https://clips.twitch.tv/DeterminedIcyPigDerp-hOW4sTcHSaJtkSjv \n19. (0:06:22 - 0:06:52) https://clips.twitch.tv/EntertainingArbitraryPorpoisePraiseIt-qvcvS6IfRDM3uOOs \n20. (0:06:52 - 0:07:03) https://clips.twitch.tv/PrettiestPolishedSoymilkRedCoat-nAj4q9n_gEImQOm8 \n", "tags": "#best_clips #twitch #stream_highlights #VALORANT", "ffmpeg_command": "ffmpeg -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/rCuFcFj2xraksmNRY1xRyA/AT-cm%7CrCuFcFj2xraksmNRY1xRyA.mp4 -i .//inputs/transition_1s.mp4 -f lavfi -t 1 -i anullsrc=cl=mono -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/8AyJYJ5sOFlxWAgiKGL3vQ/40215963975-offset-13438.mp4 -i .///inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/y2ryE4ubxay-T2WBGbaOPw/40213305943-offset-13380.mp4 -i .////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/O_KhuFV737Qd6dr6YVsNOQ/40215963975-offset-15042.mp4 -i ./////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/GXoWiPJMMWhcF5FcXgfE-g/40215963975-offset-13768.mp4 -i .//////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/cVpgmzCKGmOqO3WCiBAZlg/AT-cm%7CcVpgmzCKGmOqO3WCiBAZlg.mp4 -i .///////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/1pLK20Po4poPBp_03Qitxw/40215963975-offset-16010.mp4 -i .////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/Jam8VbBIW0BxOUPMPrGP8g/AT-cm%7CJam8VbBIW0BxOUPMPrGP8g.mp4 -i ./////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/UA8EZqRp6Rljox4kP-aAvQ/AT-cm%7CUA8EZqRp6Rljox4kP-aAvQ.mp4 -i .//////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/I6AS2_S_fSkq2ZXrZHSoJg/AT-cm%7CI6AS2_S_fSkq2ZXrZHSoJg.mp4 -i .///////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/PL8SHueDARS3omjE2jIbtA/40213305943-offset-13140.mp4 -i .////////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/fBN-peDty3eYUssaQhocfQ/46765910876-offset-16544.mp4 -i ./////////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/HRten0DV9VX2rIl6SYZTKg/40215963975-offset-6980.mp4 -i .//////////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/IHtIjACJzjGJ3xAPDutrKQ/AT-cm%7CIHtIjACJzjGJ3xAPDutrKQ.mp4 -i .///////////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/NQEEKNJywYWxW3S4zzH-7A/AT-cm%7CNQEEKNJywYWxW3S4zzH-7A.mp4 -i .////////////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/dVWMjC3VV_UvQ92Z479xhA/AT-cm%7CdVWMjC3VV_UvQ92Z479xhA.mp4 -i ./////////////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/t7N7sxLedlqnlXTWPHeg1A/AT-cm%7Ct7N7sxLedlqnlXTWPHeg1A.mp4 -i .//////////////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/julUU4TluLE3B0mibZEo7w/AT-cm%7CjulUU4TluLE3B0mibZEo7w.mp4 -i .///////////////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/hnwT0ar3L0uiH0QzN7jjrA/AT-cm%7ChnwT0ar3L0uiH0QzN7jjrA.mp4 -i .////////////////////inputs/transition_1s.mp4 -acodec aac -vcodec h264 -i https://clips-media-assets2.twitch.tv/iIFDU5wI-KvZ_4BCJkDpvA/AT-cm%7CiIFDU5wI-KvZ_4BCJkDpvA.mp4 -filter_complex \"[0:v]scale=1920x1080[s0];[s0]fps=30[s1];[s1]setdar=16/9[s2];[1:v]scale=1920x1080[s3];[s3]fps=30[s4];[s4]setdar=16/9[s5];[3:v]scale=1920x1080[s6];[s6]fps=30[s7];[s7]setdar=16/9[s8];[4:v]scale=1920x1080[s9];[s9]fps=30[s10];[s10]setdar=16/9[s11];[5:v]scale=1920x1080[s12];[s12]fps=30[s13];[s13]setdar=16/9[s14];[6:v]scale=1920x1080[s15];[s15]fps=30[s16];[s16]setdar=16/9[s17];[7:v]scale=1920x1080[s18];[s18]fps=30[s19];[s19]setdar=16/9[s20];[8:v]scale=1920x1080[s21];[s21]fps=30[s22];[s22]setdar=16/9[s23];[9:v]scale=1920x1080[s24];[s24]fps=30[s25];[s25]setdar=16/9[s26];[10:v]scale=1920x1080[s27];[s27]fps=30[s28];[s28]setdar=16/9[s29];[11:v]scale=1920x1080[s30];[s30]fps=30[s31];[s31]setdar=16/9[s32];[12:v]scale=1920x1080[s33];[s33]fps=30[s34];[s34]setdar=16/9[s35];[13:v]scale=1920x1080[s36];[s36]fps=30[s37];[s37]setdar=16/9[s38];[14:v]scale=1920x1080[s39];[s39]fps=30[s40];[s40]setdar=16/9[s41];[15:v]scale=1920x1080[s42];[s42]fps=30[s43];[s43]setdar=16/9[s44];[16:v]scale=1920x1080[s45];[s45]fps=30[s46];[s46]setdar=16/9[s47];[17:v]scale=1920x1080[s48];[s48]fps=30[s49];[s49]setdar=16/9[s50];[18:v]scale=1920x1080[s51];[s51]fps=30[s52];[s52]setdar=16/9[s53];[19:v]scale=1920x1080[s54];[s54]fps=30[s55];[s55]setdar=16/9[s56];[20:v]scale=1920x1080[s57];[s57]fps=30[s58];[s58]setdar=16/9[s59];[21:v]scale=1920x1080[s60];[s60]fps=30[s61];[s61]setdar=16/9[s62];[22:v]scale=1920x1080[s63];[s63]fps=30[s64];[s64]setdar=16/9[s65];[23:v]scale=1920x1080[s66];[s66]fps=30[s67];[s67]setdar=16/9[s68];[24:v]scale=1920x1080[s69];[s69]fps=30[s70];[s70]setdar=16/9[s71];[25:v]scale=1920x1080[s72];[s72]fps=30[s73];[s73]setdar=16/9[s74];[26:v]scale=1920x1080[s75];[s75]fps=30[s76];[s76]setdar=16/9[s77];[27:v]scale=1920x1080[s78];[s78]fps=30[s79];[s79]setdar=16/9[s80];[28:v]scale=1920x1080[s81];[s81]fps=30[s82];[s82]setdar=16/9[s83];[29:v]scale=1920x1080[s84];[s84]fps=30[s85];[s85]setdar=16/9[s86];[30:v]scale=1920x1080[s87];[s87]fps=30[s88];[s88]setdar=16/9[s89];[31:v]scale=1920x1080[s90];[s90]fps=30[s91];[s91]setdar=16/9[s92];[32:v]scale=1920x1080[s93];[s93]fps=30[s94];[s94]setdar=16/9[s95];[33:v]scale=1920x1080[s96];[s96]fps=30[s97];[s97]setdar=16/9[s98];[34:v]scale=1920x1080[s99];[s99]fps=30[s100];[s100]setdar=16/9[s101];[35:v]scale=1920x1080[s102];[s102]fps=30[s103];[s103]setdar=16/9[s104];[36:v]scale=1920x1080[s105];[s105]fps=30[s106];[s106]setdar=16/9[s107];[37:v]scale=1920x1080[s108];[s108]fps=30[s109];[s109]setdar=16/9[s110];[38:v]scale=1920x1080[s111];[s111]fps=30[s112];[s112]setdar=16/9[s113];[39:v]scale=1920x1080[s114];[s114]fps=30[s115];[s115]setdar=16/9[s116];[s2][0:a][s5][2][s8][3:a][s11][2][s14][5:a][s17][2][s20][7:a][s23][2][s26][9:a][s29][2][s32][11:a][s35][2][s38][13:a][s41][2][s44][15:a][s47][2][s50][17:a][s53][2][s56][19:a][s59][2][s62][21:a][s65][2][s68][23:a][s71][2][s74][25:a][s77][2][s80][27:a][s83][2][s86][29:a][s89][2][s92][31:a][s95][2][s98][33:a][s101][2][s104][35:a][s107][2][s110][37:a][s113][2][s116][39:a]concat=a=1:n=39:v=1[s117][s118]\" -map [s117] -map [s118] -f mp4 -acodec aac -crf 18 -vcodec libx264 output.mp4 -y", "community_class": "5"})
