



# def login(looter, args):
#     if args['--username']:
#         username = args['--username']
#         if not looter.is_logged_in():
#             password = args['--password'] or getpass.getpass()
#             looter.login(username, password)
#             if not args['--quiet']:
#                 hues.success('Logged in.')
#         elif not args['--quiet']:
#             hues.success("Already logged in.")
