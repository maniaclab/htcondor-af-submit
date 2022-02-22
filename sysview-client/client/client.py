import os
import pwd
import time
import logging
import argparse
import tabulate

from sysview.common.utils import get_config
from sysview.common.utils import expand_hostlist
from sysview.common.utils import get_base_parser

"""
Parser for systools
"""
def get_parser():
    parser = get_base_parser('sysclient')

    subparsers = parser.add_subparsers(help='Subcommand to run')

    parser_hoststatus = subparsers.add_parser('hoststatus', help='Get current manual status of a host list')
    parser_hoststatus.add_argument('hostlist', help='Host(s) to query')
    parser_hoststatus.set_defaults(func=hoststatus)

    parser_nodestatus = subparsers.add_parser('nodestatus', help='Get current machine status of a host list')
    parser_nodestatus.add_argument('hostlist', help='Host(s) to query')
    parser_nodestatus.set_defaults(func=nodestatus)

    parser_online = subparsers.add_parser('online', help='Mark a list of hosts "online" in the cache')
    parser_online.add_argument('hostlist', help='Host(s) to mark online')
    parser_online.set_defaults(func=online)

    parser_offline = subparsers.add_parser('offline', help='Mark a list of hosts "offline" in the cache with the reason "Reason"')
    parser_offline.add_argument('hostlist', help='Host(s) to mark offline')
    parser_offline.add_argument('-r', '--reason', help="Reason")
    parser_offline.set_defaults(func=offline)

    parser_backfill = subparsers.add_parser('backfill', help='Mark a list of hosts "backfill" in the cache with the reason "Reason"')
    parser_backfill.add_argument('hostlist', help='Host(s) to mark backfill')
    parser_backfill.add_argument('-r', '--reason', help="Reason")
    parser_backfill.set_defaults(func=backfill)

    parser_dumpsite = subparsers.add_parser('dump_site', help='Dump site information from the cache')
    parser_dumpsite.add_argument('site', help='Site name')
    parser_dumpsite.add_argument('--filename', help='Filename for output (write to stdout if unspecified)')
    parser_dumpsite.set_defaults(func=dump_site)

    parser_loadsite = subparsers.add_parser('load_site', help='Load site information in dump_site format back into the cache')
    parser_loadsite.add_argument('filename', help='Filename for input')
    parser_loadsite.set_defaults(func=load_site)

    return parser


"""
Get current status of a host list
"""
def get_status(keynames, hostlist, cache):
    logger = logging.getLogger(__name__)
    logger.info('Running get_status')
    data = []
    header = [
        'Node',
        'TimeStamp',
        'Last updated by user on date',
        'State',
        'Reason']
    hosts = expand_hostlist(hostlist)
    keys = ['%s.%s' % (host, keyname) for host in hosts for keyname in keynames.values()]
    values = cache.get_multi(keys)

    logger.debug('Hostlist: %s' % hosts)
    logger.debug('Keys: %s' % keynames)

    for host in hosts:
        try:
            timestamp = time.strftime(
                "%F %T",
                time.localtime(
                    int(values["%s.%s" % (host, keynames['timestamp'])])))
        except KeyError:
            timestamp = 'UNDEF'
        try:
            mtimestamp = time.strftime(
                "%F %T",
                time.localtime(
                    int(values["%s.%s" % (host, keynames['mtimestamp'])])))
        except KeyError:
            mtimestamp = 'UNDEF'
        try:
            status = values["%s.%s" % (host, keynames['status'])]
        except KeyError:
            status = 'UNDEF'
        try:
            reason = values["%s.%s" % (host, keynames['message'])]
        except KeyError:
            reason = 'UNDEF'
        try:
            user = values["%s.%s" % (host, keynames['user'])]
        except KeyError:
            user = 'UNDEF'
        data.append((host, timestamp, ' '.join((user, mtimestamp)), status, reason))

    print(tabulate.tabulate(data, headers=header, tablefmt='orgtbl'))


"""
Get current manual status of a host list
"""
def hoststatus(args, cache):
    logger = logging.getLogger(__name__)
    logger.info('Running hoststatus')
    keynames = {
        'status': 'manualstatus',
        'message': 'manualreason',
        'user': 'manualuser',
        'mtimestamp': 'manualtimestamp',
        'timestamp': 'timestamp'}
    get_status(keynames=keynames, hostlist=args.hostlist, cache=cache)


"""
Get current machine status of a host list
"""
def nodestatus(args, cache):
    logger = logging.getLogger(__name__)
    logger.info('Running nodestatus')
    keynames = {
        'status': 'status',
        'message': 'message',
        'user': 'manualuser',
        'mtimestamp': 'manualtimestamp',
        'timestamp': 'timestamp'}
    get_status(keynames=keynames, hostlist=args.hostlist, cache=cache)


"""
Update the status of a given hostname (or list of hostnames)
"""
def update_status(hostlist, status, reason, cache):
    logger = logging.getLogger(__name__)
    logger.info('Running update_status')
    data = {}
    hosts = expand_hostlist(hostlist)
    mu = pwd.getpwuid(os.getuid()).pw_name
    mts = int(time.time())

    logger.debug('Hostlist: %s' % hosts)
    logger.debug('Status: %s' % status)
    logger.debug('Reason: %s' % reason)
    logger.debug('User: %s' % mu)
    logger.debug('Timestamp: %s' % mts)

    for host in hosts:
        data['%s.manualstatus' % host] = status
        data['%s.manualreason' % host] = reason
        data['%s.manualuser' % host] = mu
        data['%s.manualtimestamp' % host] = mts
        data['%s.timestamp' % host] = mts

    cache.set_multi(data)


"""
Set nodes to online
"""
def online(args, cache):
    logger = logging.getLogger(__name__)
    logger.info('Running online')
    reason = ''
    update_status(
        hostlist=args.hostlist,
        status='online',
        reason=reason,
        cache=cache)


"""
Set nodes to offline
"""
def offline(args, cache):
    logger = logging.getLogger(__name__)
    logger.info('Running offline')
    reason = args.reason or '*Reason Not Set By User*'
    update_status(
        hostlist=args.hostlist,
        status='offline',
        reason=reason,
        cache=cache)


"""
Set nodes to backfill
"""
def backfill(args, cache):
    logger = logging.getLogger(__name__)
    logger.info('Running backfill')
    reason = args.reason or '*Reason Not Set By User*'
    update_status(
        hostlist=args.hostlist,
        status='backfill',
        reason=reason,
        cache=cache)


"""
Dump site information from the cache

The dump is of the format Node:State:Reason:User:Timestamp

    Node        Short name of the node (such as uct2-c267, iut2-c199, mwt2-c103
    State       State of the node, online|backfill|offline
    Reason      Reason a node is not online
    User        User who updated the state
    Timestamp   Time the node state was last updated
"""
def dump_site(args, cache):
    logger = logging.getLogger(__name__)
    logger.info('Running dump_site')

    config = get_config(args.config_file)
    keynames = ['manualstatus', 'manualreason', 'manualuser', 'manualtimestamp']
    hosts = []

    if not config.has_section(args.site):
        logger.critical("Configuration file is missing site '%s'" % args.site)
        logger.critical("Valid sites: %s" % " ".join([c[0] for c in config.items('collectors')]))
        exit(1)

    if args.filename:
        f = open(args.filename, 'w')

    for hostlist in config.items(args.site):
        hosts.extend(expand_hostlist(hostlist[0]))

    keys = ["%s.%s" % (host, keyname) for host in hosts for keyname in keynames]

    values = cache.get_multi(keys)

    for host in hosts:
        try:
            status = values['%s.manualstatus' % host] or values['%s.status' % host]
        except KeyError:
            status = 'Unknown'
        try:
            reason = values['%s.manualreason' % host] or values['%s.message' % host]
        except KeyError:
            reason = 'Unknown'
        try:
            user = values['%s.manualuser' % host]
        except KeyError:
            user = 'Unknown'
        try:
            mts = values['%s.manualtimestamp' % host]
        except KeyError:
            mts = 0

        if args.filename:
            f.write('%s:%s:%s:%s:%s\n' % (host, status, reason, user, mts))
        else:
            print('%s:%s:%s:%s:%s' % (host, status, reason, user, mts))

    if args.filename:
        f.close()


"""
Load line in dump_site format back into memcache

The dump is of the format Node:State:Reason

    Node        Short name of the node (such as uct2-c267, iut2-c199, mwt2-c103
    State       State of the node, online|backfill|offline
    Reason      Reason a node is not online
    User        User who updated the state
    Timestamp   Time the node state was last updated
"""
def load_site(args, cache):
    logger = logging.getLogger(__name__)
    logger.info('Running load_site')

    with open(args.filename, 'r') as f:
        for line in f:
            host, status, reason, user, timestamp = line.split(':')
            update_status(host, status, reason, cache)

