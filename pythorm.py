# -*- coding: utf-8 -*-

from tools import config

try:
    import psycopg2
except ImportError:
    print "Unable to found python library for connect \
with postgresql, try install it with 'pip install psycopg2'."
    exit()

PG_SETTINGS = {
    'user': 'postgres',
    'database': 'postgres',
    'host': 'localhost',
    'password': 'admin00',
    'port': 5432,
    'auto_commit': True
}


class Database(object):
    def __init__(self):
        super(Database, self).__init__()
        self.user = None
        self.host = None
        self.database = None
        self.password = None

    def connect_db(self, user=None, host=None, database=None, password=None, port=None):
        self.user = user if user is not None else config['db_user'] or PG_SETTINGS['user']
        self.host = host if host is not None else config['db_host'] or PG_SETTINGS['host']
        self.port = port if port is not None else config['db_port'] or PG_SETTINGS['port']
        self.database = database if database is not None else config['db_name'] or PG_SETTINGS['database']
        self.password = password if password is not None else config['db_password'] or PG_SETTINGS['password']

        try:
            PG_SETTINGS['connection'] = psycopg2.connect("dbname=%s user=%s \
            host=%s password=%s port=%d" % (self.database, self.user, self.host, self.password, self.port))
            print "(%s:%d): Successful connection for user \
'%s' in '%s' database." % (self.host, self.port, self.user, self.database)
        except Exception:
            print "(%s:%d): Connection error for the user \
'%s' in '%s' database." % (self.host, self.port, self.user, self.database)
        return PG_SETTINGS['connection']

    def create_database(self, name):
        db = self.connect_db()

    def get_cursor(self):
        return PG_SETTINGS['connection'].cursor()

    def _commit(self):
        if PG_SETTINGS['auto_commit']:
            PG_SETTINGS['connection'].commit()

    def _autocommit_close(self):
        PG_SETTINGS['auto_commit'] = False

    def _autocommit_open(self):
        PG_SETTINGS['auto_commit'] = True
        self._commit()

    def _execute_sql(self, cr, sql):
        try:
            cr.execute(sql)
        except Exception, e:
            print "Sql Failed"
            print sql
            raise e


class Field(object):
    _type = ''
    _level = 0
    _default = ''
    _required = False

    def field_sql(self, field_name):
        return '%s %s' % (field_name, self._type)


class Char(Field):
    def __init__(self, max_lenght=255, default='', required=False):
        self._type = 'varchar(%d)' % max_lenght
        self._default = default
        self.max_lenght = max_lenght
        self._required = required


class Model(object):
    def __init__(self, _id=0, **kw):
        self.__class__._create_table()
        self._table_name = self.__class__._name or self.__class__.__name__.lower()
        self.id = _id
        for name in self.field_names:
            field = getattr(self.__class__, name.replace('`', ''))
            print field._required
            setattr(self, name.replace('`', ''), field._default)
        for k, v in kw.items():
            setattr(self, k.replace('`', ''), v)

    def __str__(self):
        return "%s_%s" %(self.__class__.__name__, self.id)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def field_names(self):
        names = []
        for name in dir(self.__class__):
            var = getattr(self.__class__, name.replace('`', ''))
            if isinstance(var, Field):
                names.append("`%s`" % name)
        return names

    @classmethod
    def _create_table(cls):
        pref = 'tbl_'
        table_name = pref + cls._name.replace('.', '_') if cls._name else pref + cls.__name__.lower()
        # print table_name
        db = Database()
        db.connect_db()
        cr = db.get_cursor()
        sql = "select * from pg_catalog.pg_tables where tablename='%s';" % table_name
        db._execute_sql(cr, sql)
        if not cr.fetchall():
            sql = '''drop table if exists "%s";''' % table_name
            db._execute_sql(cr, sql)

            fields_sql = ""
            for name in dir(cls):
                var = getattr(cls, name.replace('`', ''))
                if isinstance(var, Field):
                    field = var
                    field_sql = field.field_sql(name)
                    fields_sql += ", " + field_sql
            sql = 'create table "%s" (id int not null primary key %s );' % (table_name, fields_sql)
            db._execute_sql(cr, sql)
            db._commit()


class User(Model):
    _name = 'users'
    name = Char(128, required=True)
    last_name = Char(120)


if __name__ == '__main__':
    user = User()



