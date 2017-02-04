import os
import subprocess
basepath = "/Users/kovid.rathee/Desktop/instaLooter/"
accounts = ['rupikaur_','fursty','tropicalratchet','dylankato','asyrafacha','tomashavel','runawayueli','dreamingandwandering']
for account in accounts:
    directory = basepath + account
    print(os.path.isdir(directory))
    if not os.path.exists(directory):
       os.makedirs(directory)
       command = "instaLooter %s %s -v -m -T {username}.{datetime}" % (account, directory)
       p = subprocess.Popen(command.split(), shell=False, stdout=subprocess.PIPE)
