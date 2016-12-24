from gmusicapi import Musicmanager


# login
mm = Musicmanager()
mm.perform_oauth() # once
mm.login()

# get music dict
mymusics = mm.get_uploaded_songs()

# diff?
# MUST consider directories
oldmusics = "hogehoge"

# for example
id = mymusics[0]["id"]
filename, audio_bytes = mm.download_song(id)

with open(filename, "wb") as f:
    f.write(audio_bytes)

# logout
mm.logout()

