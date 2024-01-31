import logging
from typing import Any
import aiomysql


async def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global pool
    pool = await aiomysql.create_pool(
		host = kw.get('host', '127.0.0.1'),
		port = kw.get('post', 3306),
		user = kw['user'],
		password = kw['password'],
		db = kw['db'],
		charset = kw.get('charset', 'utf8'),
		autocommit = kw.get('autocommit', True),
		maxsize = kw.get('maxsize', 10),
		minsize = kw.get('minsize', 1),
		loop = loop
	)
 
    
async def select(sql, args, size = None):
    logging.info('SQL: %s' % sql)
    global pool
    async with pool.acquire() as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace('?', '%s'), args)
        if size:
            result = await cur.fetchmany(size)
        else:
            result = await cur.fetchall()
        await cur.close()
        logging.info('%d row(s) returned' % len(result))
        return result


async def modify(sql, args):
    logging.info('SQL: %s' % sql)
    async with pool.acquire() as conn:
        try:
            cur = await conn.cursor()
            await cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount
            await cur.close()
        except BaseException as e:
            raise
        logging.info('%d row(s) changed' % affected)
        return affected


class Field(object):
    
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default
    
    def __str__(self):
        return '<Field Type: %s Name: %s>' % (self.column_type, self.name)


class IntField(Field):
    def __init__(self, name = None, column_type = 'INT', primary_key = False, default = None):
        super().__init__(name, column_type, primary_key, default)

class StringField(Field):
    
    def __init__(self, name = None, column_type = 'varchar(100)', primary_key = False, default = None):
        super().__init__(name, column_type, primary_key, default)


def create_args_string(num):
    L = []
    for i in range(num):
        L.append('?')
    return ', '.join(L)


class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        logging.info('found model %s' % name)
        table_name = attrs.get('__table__', None)
        if not table_name:
            raise RuntimeError('lack table name')
        mappings = dict()
        other_fields = []
        primary_key = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('    found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    if primary_key:
                        raise RuntimeError('Duplicate primary key for field: %s and %s' % (primary_key, k))
                    else:
                        primary_key = k
                else:
                    other_fields.append(k)
        if not primary_key:
            raise RuntimeError('Primary key not found')
        for k in mappings.keys():
            attrs.pop(k)
        protected_fields = list(map(lambda f : '`%s`' % f, other_fields))
        attrs['__mappings__'] = mappings
        attrs['__primary_key__'] = primary_key
        attrs['__other_fields__'] = other_fields
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primary_key, ', '.join(protected_fields), table_name)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (table_name, ', '.join(protected_fields), primary_key, create_args_string(len(protected_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (table_name, ', '.join(map(lambda f : '`%s`=?' % (mappings.get(f).name or f), other_fields)), primary_key)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (table_name, primary_key)
        return type.__new__(cls, name, bases, attrs)
                

class Model(dict, metaclass = ModelMetaclass):
    
    def __init__(self, **kw):
        super().__init__(**kw)
        
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError('Model has no attribute (%s)' % key)
        
    def __setattr__(self, key, value):
        self[key] = value

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value

    @classmethod
    async def find(cls, pk):
        result = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(result) == 0:
            return None
        else:
            return cls(**result[0])
        
    async def save(self):
        args = list(map(self.getValueOrDefault, self.__other_fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        affected = await modify(self.__insert__, args)
        if affected != 1:
            logging.warn('failed to insert record: affected rows: %d' % affected)


