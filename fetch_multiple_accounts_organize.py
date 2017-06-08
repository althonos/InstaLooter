import os
import sys
import subprocess
import instaLooter
basepath = "/Users/kovid.rathee/Desktop/instaLooter/"
accounts = ['rupikaur_','fursty','tropicalratchet','dylankato','asyrafacha','tomashavel','runawayueli','dreamingandwandering']
for account in accounts:
    dir = basepath + account
    print(os.path.isdir(dir))
    if not os.path.exists(dir):
       os.makedirs(dir)
       command = "instaLooter %s %s -v -m -T {username}.{datetime}" % (account, dir)
       p = subprocess.Popen(command.split(), shell=False, stdout=subprocess.PIPE)
