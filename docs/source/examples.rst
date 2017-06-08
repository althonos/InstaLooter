Examples
========

.. toctree::

``instaLooter`` also provides an :abbr:`API (Application Programmable Interface)`
that can be used to extend the capabilities of ``instaLooter``, to fit your
needs more tightly or to integrate ``instaLooter`` to your program.


Store the links to the pictures and videos of a profile into a file
-------------------------------------------------------------------

.. code::

   from instaLooter import InstaLooter
   looter = InstaLooter(profile="targetprofile")

   with open("outputfile.txt", "w") as output:
       for media in looter.medias():
           if media['is_video']:
               url = looter.get_post_info(media['code'])['video_url']
           else:
               url = media['display_src']
           output.write("{}\n".format(url))


Get a set of users that commented a given profile
-------------------------------------------------

.. code::

  from instaLooter import InstaLooter
  looter = InstaLooter(profile="targetprofile")

  users = set()
  for media in looter.medias(with_pbar=True):
     post_info = looter.get_post_info(media['code'])
     for comment in post_info['edge_media_to_comment']['edges']:
         user = comment['node']['owner']['username']
         users.add(user)


Get a set of users tagged in pictures of a given profile
--------------------------------------------------------

.. code::

   from instaLooter import InstaLooter
   looter = InstaLooter(profile="targetprofile")

   users = set()
   for media in looter.medias(with_pbar=True):
       post_info = looter.get_post_info(media['code'])
       for usertag in post_info['edge_media_to_tagged_user']['edges']:
           user = usertag['node']['user']['username']
           users.add(user)


Download resized pictures
-------------------------

Downloaded pictures will all be resized by IG to be 320 pixels wide
with the same aspect ratio before being downloaded.

.. code::

    from instaLooter import InstaLooter
    from instaLooter.urlgen import resizer

    looter = InstaLooter(profile="xxxx", get_videos=True, url_generator=resizer(320))
    looter.download()


Download thumbnails
-------------------

.. code::

    from instaLooter import InstaLooter
    from instaLooter.urlgen import thumbnail

    looter = InstaLooter(profile="xxxx", get_videos=True, url_generator=thumbnail)
    looter.download()
