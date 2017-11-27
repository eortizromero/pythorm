# -*- coding: utf-8 -*-

import optparse
import os
import sys


class DefOption(optparse.Option, object):
    def __init__(self, *opts, **attrs):
        self.by_default = attrs.pop('by_default', None)
        super(DefOption, self).__init__(*opts, **attrs)


class ConfigurationManager(object):
    def __init__(self, shortcut_name=None):
        self.options, self.casts = {}, {}
        self.config_f = shortcut_name

        if os.name == 'nt':
            conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'odoo.conf')
            print conf_file

        self.parser = parser = optparse.OptionParser(version='test version 1.0', option_class=DefOption)
        group = optparse.OptionGroup(parser, 'Database options', description='All settings for connect in your database')
        group.add_option('-d', '--database', dest='db_name', by_default=False, help='Database name')
        group.add_option('-u', '--db_user', dest='db_user', by_default=False, help='Database User name')
        group.add_option('-p', '--db_password', dest='db_password', by_default=False, help='Database Password')
        group.add_option('--db_host', dest='db_host', by_default=False, help='Database host name')
        group.add_option('--db_port', dest='db_port', by_default=False, help='Database port')
        group.add_option('--db_template', dest='db_template', by_default='template1', help='Default template for database')
        parser.add_option_group(group)

        for group in parser.option_groups:
            for o in group.option_list:
                if o.dest not in self.options:
                    self.options[o.dest] = o.by_default
                    self.casts[o.dest] = o

        self._parse_cfg()

    def _parse_cfg(self, args=None):
        if args is None:
            args = []
        opt, args = self.parser.parse_args(args)

        def die(c, msg):
            if c:
                self.parser.error(msg)

    def __setitem__(self, key, value):
        self.options[key] = value

    def __getitem__(self, key):
        return self.options[key]


config = ConfigurationManager()