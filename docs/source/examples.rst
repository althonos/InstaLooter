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


Use Instagram to get links to resized pictures
-----------------------------------------------

In this example, every link stored in the file called "links.csv" will refer
to a picture resized to be 320x320 pixel.

.. code::

    import re # the regex module
    from instaLooter import InstaLooter

    looter = InstaLooter(profile="xxxx", get_videos=True)
    cleaning_regex = re.compile(r"(s[0-9x]*/)?(e[0-9]*)/")

    with open("instagram_links.csv", "w+") as output:
        output.write('"instagram_link","picture_link","small_picture_link"\n')

        for media in looter.medias():
            post_url = "https://www.instagram.com/p/{}".format(media["code"])
            picture_url = media['display_src']
            small_picture_url = cleaning_regex.sub('s320x320/', media['display_src'])
            output.write('"{}","{}","{}"\n'.format(
                post_url, picture_url, small_picture_url
            ))
