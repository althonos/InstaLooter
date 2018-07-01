from instalooter.looters import HashtagLooter
import os

hashtags = [
    'ramones']
loot_count = 1000

for hashtag in hashtags:
    looter = HashtagLooter(hashtag)
    download_dir = '/data/danieltc/{}'.format(hashtag)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    print("Looting hashtag {} into dir {}".format(
        hashtag, download_dir))
    looter.download_pictures(download_dir, media_count=loot_count)
print("Exit gracefully")
