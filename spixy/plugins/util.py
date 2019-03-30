def chan_or_user(response, nick, target):
    if target.startswith('#'):
        return {'target': target, 'message': "%s: %s" % (nick, response)}
    else:
        return {'target': nick, 'message': response}
