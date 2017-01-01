#!/usr/bin/env python3
from gmusicapi import Musicmanager
import sys
import os
import pickle
import configparser
import json # for test


def trim_name(name):
    """ replace "/" and "." to "_"
    if name length is more than 30, it is shorten to 30.
    """
    illigal_char = ("/",".",":","<",">",";","*","?","\"","|",",","*")
    tmp = name
    for el in illigal_char:
        tmp = tmp.replace(el, "_")

    if len(tmp) > 30:
        tmp = tmp[:30]
    return tmp

if __name__ == '__main__':

    # load settings
    inifile = configparser.SafeConfigParser()
    inifile.read("./settings.ini")
    pickle_filename = inifile.get("settings", "picklefile")
    music_root = inifile.get("settings", "musicroot")

    # # login
    mm = Musicmanager()
    # mm.perform_oauth() # once
    mm.login()

    # # get music dict
    mymusics = mm.get_uploaded_songs()
    # with open("newsonglist.json","r") as f:
    #     mymusics = json.load(f)# for test

    # get id list
    all_ids = set([el["id"] for el in mymusics])

    # convert list to dict
    music_dict = {el["id"]:el for el in mymusics}

    # get downloaded id list
    if os.path.isfile(pickle_filename):
        with open(pickle_filename, "rb") as f:
            downloaded_ids = pickle.load(f)
    else:
        downloaded_ids = set([])

    # set download ids
    tasks = all_ids - downloaded_ids
    num_tasks = len(tasks)

    for i, el in enumerate(tasks):
        print("processing...%d/%d" % (i+1, num_tasks))
        song_info = music_dict[el]
        
        # artist name
        if song_info["album_artist"] == "":
            if song_info["artist"] == "":
                artist = "undefined"
            else:
                artist = song_info["artist"]
        else:
            artist = song_info["album_artist"]
        artist = trim_name(artist)

        # album name
        if song_info["album"] == "":
            album = "undefined"
        else:
            album = song_info["album"]
        album = trim_name(album)

        # gen folder
        os.makedirs("%s/%s/%s" % (music_root, artist, album), exist_ok=True)
        
        try:
            filename, audio_bytes = mm.download_song(el)
            base, ext = os.path.splitext(filename)
            filename = trim_name(base) + ext

            target = "%s/%s/%s/%s" % (music_root, artist, album, filename)
            print("  save %s" % target)
            with open(target, "wb") as f:
                f.write(audio_bytes)
        except KeyboardInterrupt:
            print("!!!!!KeyboardInterrupt!!!!!")
            with open(pickle_filename, "wb") as f:
                pickle.dump(downloaded_ids, f)
            sys.exit(-1)
        except:
            print("  ignore!")
            continue

        # if download is success, song id is added to downloaded_ids
        downloaded_ids.add(el)

    with open(pickle_filename, "wb") as f:
        pickle.dump(downloaded_ids, f)
