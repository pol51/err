# -*- coding: utf-8 -*-
import logging
import inspect
import os

PLUGINS_SUBDIR = 'plugins'

def get_sender_username(mess):
    """Extract the sender's user name from a message"""
    type = mess.getType()
    jid = mess.getFrom()
    if type == "groupchat":
        username = jid.getResource()
    elif type == "chat":
        username = jid.getNode()
    else:
        username = ""
    return username


def get_jid_from_message(mess):
    if mess.getType() == 'chat':
        return str(mess.getFrom().getStripped())
        # this is a hipchat message from a group so find out from the sender node, for the moment hardcoded because it is not parsed, it could brake in the future
    jid = mess.getTagAttr('delay', 'from_jid')
    if jid:
        logging.debug('found the jid from the delay tag : %s' % jid)
        return jid
    jid = mess.getTagData('sender')
    if jid:
        logging.debug('found the jid from the sender tag : %s' % jid)
        return jid
    x = mess.getTag('x')
    if x:
        jid = x.getTagData('sender')

    if jid:
        logging.debug('found the jid from the x/sender tag : %s' % jid)
        return jid
    splitted = str(mess.getFrom()).split('/')
    jid = splitted[1] if len(splitted) > 1 else splitted[0] # despair

    logging.debug('deduced the jid from the chatroom to %s' % jid)
    return jid


def format_timedelta(timedelta):
    total_seconds = timedelta.seconds + (86400 * timedelta.days)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours == 0 and minutes == 0:
        return '%i seconds' % seconds
    elif not hours:
        return '%i minutes' % minutes
    elif not minutes:
        return '%i hours' % hours
    else:
        return '%i hours and %i minutes' % (hours, minutes)

BAR_WIDTH = 15.0

def drawbar(value, max):
    if max:
        value_in_chr = int(round((value * BAR_WIDTH / max)))
    else:
        value_in_chr = 0
    return u'[' + u'█' * value_in_chr + u'▒' * int(round(BAR_WIDTH - value_in_chr)) + u']'


# Introspect to know from which plugin a command is implemented
def get_class_for_method(meth):
    for cls in inspect.getmro(meth.im_class):
        if meth.__name__ in cls.__dict__: return cls
    return None


def human_name_for_git_url(url):
    # try to humanize the last part of the git url as much as we can
    if url.find('/') > 0:
        s = url.split('/')
    else:
        s = url.split(':')
    last_part = str(s[-1]) if s[-1] else str(s[-2])
    return last_part[:-4] if last_part.endswith('.git') else last_part


def tail( f, window=20 ):
    return ''.join(f.readlines()[-window:])


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def version2array(version):
    response = [int(el) for el in version.split('.')]
    if len(response) != 3:
        raise Exception('version %s in not in format "x.y.z" for example "1.2.2"' % version)
    return response


class ValidationException(Exception):
    pass


def recurse_check_structure(sample, to_check):
    sample_type = type(sample)
    to_check_type = type(to_check)
    if sample_type != to_check_type:
        raise ValidationException('%s [%s] is not the same type as %s [%s]' % (sample, sample_type, to_check_type, to_check_type))

    if sample_type in (list, tuple):
        for element in to_check:
            recurse_check_structure(sample[0], element)
        return

    if sample_type == dict:
        for key in sample:
            if not to_check.has_key(key):
                raise ValidationException("%s doesn't contain the key %s" % (to_check, key))
        for key in to_check:
            if not sample.has_key(key):
                raise ValidationException("%s contains an unknown key %s" % (to_check, key))
        for key in sample:
            recurse_check_structure(sample[key], to_check[key])
        return
