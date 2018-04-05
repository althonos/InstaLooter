API Examples
============

.. toctree::

``instaLooter`` also provides an :abbr:`API (Application Programmable Interface)`
that can be used to extend the capabilities of ``instaLooter``, to fit your
needs more tightly or to integrate ``instaLooter`` to your program.


Download pictures
-----------------

Download 50 posts from the `Dream Wife band <https://www.instagram.com/dreamwifetheband/?hl=fr>`_
account to the `Pictures` directory in your home folder (you better be checking
their music though):

.. code:: python

   from instalooter.looters import ProfileLooter
   looter = ProfileLooter("dreamwifetheband")
   looter.download('~/Pictures', media_count=50)


Dump media links
----------------

Create a list with all the links to picture and video files tagged with
`#ramones <https://www.instagram.com/explore/tags/ramones/>`_ in a file
named `ramones.txt`:

.. code:: python

    def links(media, looter):
        if media.get('__typename') == "GraphSidecar":
            media = looter.get_post_info(media['shortcode'])
            nodes = [e['node'] for e in media['edge_sidecar_to_children']['edges']]
            return [n.get('video_url') or n.get('display_url') for n in nodes]
        elif media['is_video']:
            media = looter.get_post_info(media['shortcode'])
            return [media['video_url']]
        else:
            return [media['display_url']]

    from instalooter.looters import HashtagLooter
    looter = HashtagLooter("ramones")

    with open("ramones.txt", "w") as f:
        for media in looter.medias():
            for link in links(media, looter):
                f.write("{}\n".format(link))


Users from comments
-------------------

Obtain a subset of users that commented on some of the posts of
`Franz Ferdinand <https://www.instagram.com/franz_ferdinand>`_.

.. code:: python

    from instalooter.looters import ProfileLooter
    looter = ProfileLooter("franz_ferdinand")

    users = set()
    for media in looter.medias():
       info = looter.get_post_info(media['shortcode'])
       for comment in post_info['edge_media_to_comment']['edges']:
           user = comment['node']['owner']['username']
           users.add(user)


Users from mentions
-------------------



.. code:: python

    from instalooter.looters import ProfileLooter
    looter = ProfileLooter("mandodiaomusic")

    users = set()
    for media in looter.medias():
       info = looter.get_post_info(media['shortcode'])
       for comment in post_info['edge_media_to_tagged_user']['edges']:
           user = comment['node']['user']['username']
           users.add(user)


Download resized pictures
-------------------------

Unfortunately, this is not possible anymore as Instagram added a hash signature
to prevent messing with their URLs.

..
.. Downloaded pictures will all be resized by IG to be 320 pixels wide
.. with the same aspect ratio before being downloaded.
..
.. .. code::
..
..     from instaLooter import InstaLooter
..     from instaLooter.urlgen import resizer
..
..     looter = InstaLooter(profile="xxxx", get_videos=True, url_generator=resizer(320))
..     looter.download()


.. Download thumbnails
.. -------------------
.. .. code::
..
..     from instaLooter import InstaLooter
..     from instaLooter.urlgen import thumbnail
..
..     looter = InstaLooter(profile="xxxx", get_videos=True, url_generator=thumbnail)
..     looter.download()
