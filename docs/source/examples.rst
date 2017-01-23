Examples
========

.. toctree::

``instaLooter`` also provides an :abbr:`API (Application Programmable Interface)`
that can be used to extend the capabilities of ``instaLooter``.


Get a set of users that commented a given profile
-------------------------------------------------

.. code::

  from instaLooter import InstaLooter
  looter = InstaLooter(profile="targetprofile")

  users = set()
  for media in looter.medias(with_pbar=True):
     post_info = looter.get_post_info(media['code'])
     for comment in post_info['comments']['nodes']:
         user = comment['user']['username']
         users.add(user)


Get a set of users tagged in pictures of a given profile
--------------------------------------------------------

.. code::

   from instaLooter import InstaLooter
   looter = InstaLooter(profile="targetprofile")

   users = set()
   for media in looter.medias(with_pbar=True):
       post_info = looter.get_post_info(media['code'])
       for usertag in post_info['usertags']['nodes']:
           user = usertag['user']['username']
           users.add(user)
