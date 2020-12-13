import sys
import mitzasql.sql_parser.tokens as Token

symbol_operators = [
    '->>',
    '<=>',
    '>>',
    '>=',
    '<>',
    '!=',
    '<<',
    '<=',
    '->',
    ':=',
    '||',
    '&&',
    '&',
    '>',
    '<',
    '%',
    '*',
    '+',
    '-',
    '-',
    '/',
    '=',
    '=',
    '^',
    '|',
    '~'
]

index = {}

literals = {
    'false': Token.Boolean,
    'true': Token.Boolean,
    'null': Token.Null
}
index['literals'] = literals

word_operators = {
    'and': Token.Operator,
    'between': Token.Operator,
    'case': Token.Operator,
    'div': Token.Operator,

    'is': Token.Operator,
    'not': Token.Operator,
    'like': Token.Operator,
    'mod': Token.Operator,
    'regexp': Token.Operator,

    'or': Token.Operator,
    'rlike': Token.Operator,
    'sounds': Token.Operator,
    'xor': Token.Operator,
}
index['word_operators'] = word_operators

reserved_keywords = {
    'accessible': Token.Keyword.Reserved,
    'add': Token.Keyword.Reserved,
    'all': Token.Keyword.Reserved,
    'alter': Token.Keyword.Reserved,
    'analyze': Token.Keyword.Reserved,
    'as': Token.Keyword.Reserved,
    'asc': Token.Keyword.Reserved,
    'asensitive': Token.Keyword.Reserved,
    'before': Token.Keyword.Reserved,
    'bigint': Token.Keyword.Reserved,
    'binary': Token.Keyword.Reserved,
    'blob': Token.Keyword.Reserved,
    'both': Token.Keyword.Reserved,
    'by': Token.Keyword.Reserved,
    'call': Token.Keyword.Reserved,
    'cascade': Token.Keyword.Reserved,
    'change': Token.Keyword.Reserved,
    'char': Token.Keyword.Reserved,
    'character': Token.Keyword.Reserved,
    'check': Token.Keyword.Reserved,
    'collate': Token.Keyword.Reserved,
    'column': Token.Keyword.Reserved,
    'condition': Token.Keyword.Reserved,
    'constraint': Token.Keyword.Reserved,
    'continue': Token.Keyword.Reserved,
    'convert': Token.Keyword.Reserved,
    'create': Token.Keyword.Reserved,
    'cross': Token.Keyword.Reserved,
    'cube': Token.Keyword.Reserved,
    'cume_dist': Token.Keyword.Reserved,
    'current_date': Token.Keyword.Reserved,
    'current_time': Token.Keyword.Reserved,
    'current_timestamp': Token.Keyword.Reserved,
    'current_user': Token.Keyword.Reserved,
    'cursor': Token.Keyword.Reserved,
    'database': Token.Keyword.Reserved,
    'databases': Token.Keyword.Reserved,
    'day_hour': Token.Keyword.Reserved,
    'day_microsecond': Token.Keyword.Reserved,
    'day_minute': Token.Keyword.Reserved,
    'day_second': Token.Keyword.Reserved,
    'dec': Token.Keyword.Reserved,
    'decimal': Token.Keyword.Reserved,
    'declare': Token.Keyword.Reserved,
    'default': Token.Keyword.Reserved,
    'delayed': Token.Keyword.Reserved,
    'delete': Token.Keyword.Reserved,
    'dense_rank': Token.Keyword.Reserved,
    'desc': Token.Keyword.Reserved,
    'describe': Token.Keyword.Reserved,
    'deterministic': Token.Keyword.Reserved,
    'distinct': Token.Keyword.Reserved,
    'distinctrow': Token.Keyword.Reserved,
    'double': Token.Keyword.Reserved,
    'drop': Token.Keyword.Reserved,
    'dual': Token.Keyword.Reserved,
    'each': Token.Keyword.Reserved,
    'else': Token.Keyword.Reserved,
    'elseif': Token.Keyword.Reserved,
    'empty': Token.Keyword.Reserved,
    'enclosed': Token.Keyword.Reserved,
    'escaped': Token.Keyword.Reserved,
    'except': Token.Keyword.Reserved,
    'exists': Token.Keyword.Reserved,
    'exit': Token.Keyword.Reserved,
    'explain': Token.Keyword.Reserved,
    'fetch': Token.Keyword.Reserved,
    'first_value': Token.Keyword.Reserved,
    'float': Token.Keyword.Reserved,
    'float4': Token.Keyword.Reserved,
    'float8': Token.Keyword.Reserved,
    'for': Token.Keyword.Reserved,
    'force': Token.Keyword.Reserved,
    'foreign': Token.Keyword.Reserved,
    'from': Token.Keyword.Reserved,
    'fulltext': Token.Keyword.Reserved,
    'function': Token.Keyword.Reserved,
    'generated': Token.Keyword.Reserved,
    'get': Token.Keyword.Reserved,
    'grant': Token.Keyword.Reserved,
    'group': Token.Keyword.Reserved,
    'grouping': Token.Keyword.Reserved,
    'groups': Token.Keyword.Reserved,
    'having': Token.Keyword.Reserved,
    'high_priority': Token.Keyword.Reserved,
    'hour_microsecond': Token.Keyword.Reserved,
    'hour_minute': Token.Keyword.Reserved,
    'hour_second': Token.Keyword.Reserved,
    'if': Token.Keyword.Reserved,
    'ignore': Token.Keyword.Reserved,
    'in': Token.Keyword.Reserved,
    'index': Token.Keyword.Reserved,
    'infile': Token.Keyword.Reserved,
    'inner': Token.Keyword.Reserved,
    'inout': Token.Keyword.Reserved,
    'insensitive': Token.Keyword.Reserved,
    'insert': Token.Keyword.Reserved,
    'int': Token.Keyword.Reserved,
    'int1': Token.Keyword.Reserved,
    'int2': Token.Keyword.Reserved,
    'int3': Token.Keyword.Reserved,
    'int4': Token.Keyword.Reserved,
    'int8': Token.Keyword.Reserved,
    'integer': Token.Keyword.Reserved,
    'interval': Token.Keyword.Reserved,
    'into': Token.Keyword.Reserved,
    'io_after_gtids': Token.Keyword.Reserved,
    'io_before_gtids': Token.Keyword.Reserved,
    'iterate': Token.Keyword.Reserved,
    'join': Token.Keyword.Reserved,
    'json_table': Token.Keyword.Reserved,
    'key': Token.Keyword.Reserved,
    'keys': Token.Keyword.Reserved,
    'kill': Token.Keyword.Reserved,
    'lag': Token.Keyword.Reserved,
    'last_value': Token.Keyword.Reserved,
    'lateral': Token.Keyword.Reserved,
    'lead': Token.Keyword.Reserved,
    'leading': Token.Keyword.Reserved,
    'leave': Token.Keyword.Reserved,
    'left': Token.Keyword.Reserved,
    'limit': Token.Keyword.Reserved,
    'linear': Token.Keyword.Reserved,
    'lines': Token.Keyword.Reserved,
    'load': Token.Keyword.Reserved,
    'localtime': Token.Keyword.Reserved,
    'localtimestamp': Token.Keyword.Reserved,
    'lock': Token.Keyword.Reserved,
    'long': Token.Keyword.Reserved,
    'longblob': Token.Keyword.Reserved,
    'longtext': Token.Keyword.Reserved,
    'loop': Token.Keyword.Reserved,
    'low_priority': Token.Keyword.Reserved,
    'master_bind': Token.Keyword.Reserved,
    'master_ssl_verify': Token.Keyword.Reserved,
    'match': Token.Keyword.Reserved,
    'maxvalue': Token.Keyword.Reserved,
    'mediumblob': Token.Keyword.Reserved,
    'mediumint': Token.Keyword.Reserved,
    'mediumtext': Token.Keyword.Reserved,
    'middleint': Token.Keyword.Reserved,
    'minute_microsecond': Token.Keyword.Reserved,
    'minute_second': Token.Keyword.Reserved,
    'modifies': Token.Keyword.Reserved,
    'natural': Token.Keyword.Reserved,
    'no_write_to_binlog': Token.Keyword.Reserved,
    'nth_value': Token.Keyword.Reserved,
    'ntile': Token.Keyword.Reserved,
    'numeric': Token.Keyword.Reserved,
    'of': Token.Keyword.Reserved,
    'on': Token.Keyword.Reserved,
    'optimize': Token.Keyword.Reserved,
    'optimizer_costs': Token.Keyword.Reserved,
    'option': Token.Keyword.Reserved,
    'optionally': Token.Keyword.Reserved,
    'order': Token.Keyword.Reserved,
    'out': Token.Keyword.Reserved,
    'outer': Token.Keyword.Reserved,
    'outfile': Token.Keyword.Reserved,
    'over': Token.Keyword.Reserved,
    'partition': Token.Keyword.Reserved,
    'percent_rank': Token.Keyword.Reserved,
    'precision': Token.Keyword.Reserved,
    'primary': Token.Keyword.Reserved,
    'procedure': Token.Keyword.Reserved,
    'purge': Token.Keyword.Reserved,
    'range': Token.Keyword.Reserved,
    'rank': Token.Keyword.Reserved,
    'read': Token.Keyword.Reserved,
    'reads': Token.Keyword.Reserved,
    'read_write': Token.Keyword.Reserved,
    'real': Token.Keyword.Reserved,
    'recursive': Token.Keyword.Reserved,
    'references': Token.Keyword.Reserved,
    'release': Token.Keyword.Reserved,
    'rename': Token.Keyword.Reserved,
    'repeat': Token.Keyword.Reserved,
    'replace': Token.Keyword.Reserved,
    'require': Token.Keyword.Reserved,
    'resignal': Token.Keyword.Reserved,
    'restrict': Token.Keyword.Reserved,
    'return': Token.Keyword.Reserved,
    'revoke': Token.Keyword.Reserved,
    'right': Token.Keyword.Reserved,
    'row': Token.Keyword.Reserved,
    'rows': Token.Keyword.Reserved,
    'row_number': Token.Keyword.Reserved,
    'schema': Token.Keyword.Reserved,
    'schemas': Token.Keyword.Reserved,
    'second_microsecond': Token.Keyword.Reserved,
    'select': Token.Keyword.Reserved,
    'sensitive': Token.Keyword.Reserved,
    'separator': Token.Keyword.Reserved,
    'set': Token.Keyword.Reserved,
    'show': Token.Keyword.Reserved,
    'signal': Token.Keyword.Reserved,
    'smallint': Token.Keyword.Reserved,
    'spatial': Token.Keyword.Reserved,
    'specific': Token.Keyword.Reserved,
    'sql': Token.Keyword.Reserved,
    'sqlexception': Token.Keyword.Reserved,
    'sqlstate': Token.Keyword.Reserved,
    'sqlwarning': Token.Keyword.Reserved,
    'sql_big_result': Token.Keyword.Reserved,
    'sql_calc_found_rows': Token.Keyword.Reserved,
    'sql_small_result': Token.Keyword.Reserved,
    'ssl': Token.Keyword.Reserved,
    'starting': Token.Keyword.Reserved,
    'stored': Token.Keyword.Reserved,
    'straight_join': Token.Keyword.Reserved,
    'system': Token.Keyword.Reserved,
    'table': Token.Keyword.Reserved,
    'terminated': Token.Keyword.Reserved,
    'then': Token.Keyword.Reserved,
    'tinyblob': Token.Keyword.Reserved,
    'tinyint': Token.Keyword.Reserved,
    'tinytext': Token.Keyword.Reserved,
    'to': Token.Keyword.Reserved,
    'trailing': Token.Keyword.Reserved,
    'trigger': Token.Keyword.Reserved,
    'undo': Token.Keyword.Reserved,
    'union': Token.Keyword.Reserved,
    'unique': Token.Keyword.Reserved,
    'unlock': Token.Keyword.Reserved,
    'unsigned': Token.Keyword.Reserved,
    'update': Token.Keyword.Reserved,
    'usage': Token.Keyword.Reserved,
    'use': Token.Keyword.Reserved,
    'using': Token.Keyword.Reserved,
    'utc_date': Token.Keyword.Reserved,
    'utc_time': Token.Keyword.Reserved,
    'utc_timestamp': Token.Keyword.Reserved,
    'values': Token.Keyword.Reserved,
    'varbinary': Token.Keyword.Reserved,
    'varchar': Token.Keyword.Reserved,
    'varcharacter': Token.Keyword.Reserved,
    'varying': Token.Keyword.Reserved,
    'virtual': Token.Keyword.Reserved,
    'when': Token.Keyword.Reserved,
    'where': Token.Keyword.Reserved,
    'while': Token.Keyword.Reserved,
    'window': Token.Keyword.Reserved,
    'with': Token.Keyword.Reserved,
    'write': Token.Keyword.Reserved,
    'year_month': Token.Keyword.Reserved,
    'zerofill': Token.Keyword.Reserved,
}
index['reserved_keywords'] = reserved_keywords

keywords = {
    'account': Token.Keyword,
    'action': Token.Keyword,
    'active': Token.Keyword,
    'admin': Token.Keyword,
    'after': Token.Keyword,
    'against': Token.Keyword,
    'aggregate': Token.Keyword,
    'algorithm': Token.Keyword,
    'always': Token.Keyword,
    'any': Token.Keyword,
    'array': Token.Keyword,
    'ascii': Token.Keyword,
    'at': Token.Keyword,
    'attribute': Token.Keyword,
    'autoextend_size': Token.Keyword,
    'auto_increment': Token.Keyword,
    'avg': Token.Keyword,
    'avg_row_length': Token.Keyword,
    'backup': Token.Keyword,
    'begin': Token.Keyword,
    'binlog': Token.Keyword,
    'bit': Token.Keyword,
    'block': Token.Keyword,
    'bool': Token.Keyword,
    'boolean': Token.Keyword,
    'btree': Token.Keyword,
    'buckets': Token.Keyword,
    'byte': Token.Keyword,
    'cache': Token.Keyword,
    'cascaded': Token.Keyword,
    'catalog_name': Token.Keyword,
    'chain': Token.Keyword,
    'changed': Token.Keyword,
    'channel': Token.Keyword,
    'charset': Token.Keyword,
    'checksum': Token.Keyword,
    'cipher': Token.Keyword,
    'class_origin': Token.Keyword,
    'client': Token.Keyword,
    'clone': Token.Keyword,
    'close': Token.Keyword,
    'coalesce': Token.Keyword,
    'code': Token.Keyword,
    'collation': Token.Keyword,
    'columns': Token.Keyword,
    'column_format': Token.Keyword,
    'column_name': Token.Keyword,
    'comment': Token.Keyword,
    'commit': Token.Keyword,
    'committed': Token.Keyword,
    'compact': Token.Keyword,
    'completion': Token.Keyword,
    'component': Token.Keyword,
    'compressed': Token.Keyword,
    'compression': Token.Keyword,
    'concurrent': Token.Keyword,
    'connection': Token.Keyword,
    'consistent': Token.Keyword,
    'constraint_catalog': Token.Keyword,
    'constraint_name': Token.Keyword,
    'constraint_schema': Token.Keyword,
    'contains': Token.Keyword,
    'context': Token.Keyword,
    'cpu': Token.Keyword,
    'current': Token.Keyword,
    'cursor_name': Token.Keyword,
    'data': Token.Keyword,
    'datafile': Token.Keyword,
    'date': Token.Keyword,
    'datetime': Token.Keyword,
    'day': Token.Keyword,
    'deallocate': Token.Keyword,
    'default_auth': Token.Keyword,
    'definer': Token.Keyword,
    'definition': Token.Keyword,
    'delay_key_write': Token.Keyword,
    'description': Token.Keyword,
    'diagnostics': Token.Keyword,
    'directory': Token.Keyword,
    'disable': Token.Keyword,
    'discard': Token.Keyword,
    'disk': Token.Keyword,
    'do': Token.Keyword,
    'dumpfile': Token.Keyword,
    'duplicate': Token.Keyword,
    'dynamic': Token.Keyword,
    'enable': Token.Keyword,
    'encryption': Token.Keyword,
    'end': Token.Keyword,
    'ends': Token.Keyword,
    'enforced': Token.Keyword,
    'engine': Token.Keyword,
    'engines': Token.Keyword,
    'engine_attribute': Token.Keyword,
    'enum': Token.Keyword,
    'error': Token.Keyword,
    'errors': Token.Keyword,
    'escape': Token.Keyword,
    'event': Token.Keyword,
    'events': Token.Keyword,
    'every': Token.Keyword,
    'exchange': Token.Keyword,
    'exclude': Token.Keyword,
    'execute': Token.Keyword,
    'expansion': Token.Keyword,
    'expire': Token.Keyword,
    'export': Token.Keyword,
    'extended': Token.Keyword,
    'extent_size': Token.Keyword,
    'failed_login_attem': Token.Keyword,
    'fast': Token.Keyword,
    'faults': Token.Keyword,
    'fields': Token.Keyword,
    'file': Token.Keyword,
    'file_block_size': Token.Keyword,
    'filter': Token.Keyword,
    'first': Token.Keyword,
    'fixed': Token.Keyword,
    'flush': Token.Keyword,
    'following': Token.Keyword,
    'follows': Token.Keyword,
    'format': Token.Keyword,
    'found': Token.Keyword,
    'full': Token.Keyword,
    'general': Token.Keyword,
    'geomcollection': Token.Keyword,
    'geometry': Token.Keyword,
    'geometrycollection': Token.Keyword,
    'get_format': Token.Keyword,
    'get_master_public_': Token.Keyword,
    'global': Token.Keyword,
    'grants': Token.Keyword,
    'group_replication': Token.Keyword,
    'handler': Token.Keyword,
    'hash': Token.Keyword,
    'help': Token.Keyword,
    'histogram': Token.Keyword,
    'history': Token.Keyword,
    'host': Token.Keyword,
    'hosts': Token.Keyword,
    'hour': Token.Keyword,
    'identified': Token.Keyword,
    'ignore_server_ids': Token.Keyword,
    'import': Token.Keyword,
    'inactive': Token.Keyword,
    'indexes': Token.Keyword,
    'initial_size': Token.Keyword,
    'insert_method': Token.Keyword,
    'install': Token.Keyword,
    'instance': Token.Keyword,
    'invisible': Token.Keyword,
    'invoker': Token.Keyword,
    'io': Token.Keyword,
    'io_thread': Token.Keyword,
    'ipc': Token.Keyword,
    'isolation': Token.Keyword,
    'issuer': Token.Keyword,
    'json': Token.Keyword,
    'json_value': Token.Keyword,
    'key_block_size': Token.Keyword,
    'language': Token.Keyword,
    'last': Token.Keyword,
    'leaves': Token.Keyword,
    'less': Token.Keyword,
    'level': Token.Keyword,
    'linestring': Token.Keyword,
    'list': Token.Keyword,
    'local': Token.Keyword,
    'locked': Token.Keyword,
    'locks': Token.Keyword,
    'logfile': Token.Keyword,
    'logs': Token.Keyword,
    'master': Token.Keyword,
    'master_auto_positi': Token.Keyword,
    'master_compression': Token.Keyword,
    'master_connect_ret': Token.Keyword,
    'master_delay': Token.Keyword,
    'master_heartbeat_p': Token.Keyword,
    'master_host': Token.Keyword,
    'master_log_file': Token.Keyword,
    'master_log_pos': Token.Keyword,
    'master_password': Token.Keyword,
    'master_port': Token.Keyword,
    'master_public_key_': Token.Keyword,
    'master_retry_count': Token.Keyword,
    'master_server_id': Token.Keyword,
    'master_ssl': Token.Keyword,
    'master_ssl_ca': Token.Keyword,
    'master_ssl_capath': Token.Keyword,
    'master_ssl_cert': Token.Keyword,
    'master_ssl_crl': Token.Keyword,
    'master_ssl_crlpath': Token.Keyword,
    'master_ssl_key': Token.Keyword,
    'master_tls_ciphers': Token.Keyword,
    'master_tls_version': Token.Keyword,
    'master_user': Token.Keyword,
    'master_zstd_compre': Token.Keyword,
    'max_connections_pe': Token.Keyword,
    'max_queries_per_ho': Token.Keyword,
    'max_rows': Token.Keyword,
    'max_size': Token.Keyword,
    'max_updates_per_ho': Token.Keyword,
    'max_user_connectio': Token.Keyword,
    'medium': Token.Keyword,
    'member': Token.Keyword,
    'memory': Token.Keyword,
    'merge': Token.Keyword,
    'message_text': Token.Keyword,
    'microsecond': Token.Keyword,
    'migrate': Token.Keyword,
    'minute': Token.Keyword,
    'min_rows': Token.Keyword,
    'mode': Token.Keyword,
    'modify': Token.Keyword,
    'month': Token.Keyword,
    'multilinestring': Token.Keyword,
    'multipoint': Token.Keyword,
    'multipolygon': Token.Keyword,
    'mutex': Token.Keyword,
    'mysql_errno': Token.Keyword,
    'name': Token.Keyword,
    'names': Token.Keyword,
    'national': Token.Keyword,
    'nchar': Token.Keyword,
    'ndb': Token.Keyword,
    'ndbcluster': Token.Keyword,
    'nested': Token.Keyword,
    'network_namespace': Token.Keyword,
    'never': Token.Keyword,
    'new': Token.Keyword,
    'next': Token.Keyword,
    'no': Token.Keyword,
    'nodegroup': Token.Keyword,
    'none': Token.Keyword,
    'nowait': Token.Keyword,
    'no_wait': Token.Keyword,
    'nulls': Token.Keyword,
    'number': Token.Keyword,
    'nvarchar': Token.Keyword,
    'off': Token.Keyword,
    'offset': Token.Keyword,
    'oj': Token.Keyword,
    'old': Token.Keyword,
    'one': Token.Keyword,
    'only': Token.Keyword,
    'open': Token.Keyword,
    'optional': Token.Keyword,
    'options': Token.Keyword,
    'ordinality': Token.Keyword,
    'organization': Token.Keyword,
    'others': Token.Keyword,
    'owner': Token.Keyword,
    'pack_keys': Token.Keyword,
    'page': Token.Keyword,
    'parser': Token.Keyword,
    'partial': Token.Keyword,
    'partitioning': Token.Keyword,
    'partitions': Token.Keyword,
    'password': Token.Keyword,
    'password_lock_time': Token.Keyword,
    'path': Token.Keyword,
    'persist': Token.Keyword,
    'persist_only': Token.Keyword,
    'phase': Token.Keyword,
    'plugin': Token.Keyword,
    'plugins': Token.Keyword,
    'plugin_dir': Token.Keyword,
    'point': Token.Keyword,
    'polygon': Token.Keyword,
    'port': Token.Keyword,
    'precedes': Token.Keyword,
    'preceding': Token.Keyword,
    'prepare': Token.Keyword,
    'preserve': Token.Keyword,
    'prev': Token.Keyword,
    'privileges': Token.Keyword,
    'privilege_checks_u': Token.Keyword,
    'process': Token.Keyword,
    'processlist': Token.Keyword,
    'profile': Token.Keyword,
    'profiles': Token.Keyword,
    'proxy': Token.Keyword,
    'quarter': Token.Keyword,
    'query': Token.Keyword,
    'quick': Token.Keyword,
    'random': Token.Keyword,
    'read_only': Token.Keyword,
    'rebuild': Token.Keyword,
    'recover': Token.Keyword,
    'redo_buffer_size': Token.Keyword,
    'redundant': Token.Keyword,
    'reference': Token.Keyword,
    'relay': Token.Keyword,
    'relaylog': Token.Keyword,
    'relay_log_file': Token.Keyword,
    'relay_log_pos': Token.Keyword,
    'relay_thread': Token.Keyword,
    'reload': Token.Keyword,
    'remove': Token.Keyword,
    'reorganize': Token.Keyword,
    'repair': Token.Keyword,
    'repeatable': Token.Keyword,
    'replica': Token.Keyword,
    'replicas': Token.Keyword,
    'replicate_do_db': Token.Keyword,
    'replicate_do_table': Token.Keyword,
    'replicate_ignore_db': Token.Keyword,
    'replicate_ignore_t': Token.Keyword,
    'replicate_rewrite_': Token.Keyword,
    'replicate_wild_do_': Token.Keyword,
    'replicate_wild_ign': Token.Keyword,
    'replication': Token.Keyword,
    'require_row_format': Token.Keyword,
    'require_table_prim': Token.Keyword,
    'reset': Token.Keyword,
    'resource': Token.Keyword,
    'respect': Token.Keyword,
    'restart': Token.Keyword,
    'restore': Token.Keyword,
    'resume': Token.Keyword,
    'retain': Token.Keyword,
    'returned_sqlstate': Token.Keyword,
    'returning': Token.Keyword,
    'returns': Token.Keyword,
    'reuse': Token.Keyword,
    'reverse': Token.Keyword,
    'role': Token.Keyword,
    'rollback': Token.Keyword,
    'rollup': Token.Keyword,
    'rotate': Token.Keyword,
    'routine': Token.Keyword,
    'row_count': Token.Keyword,
    'row_format': Token.Keyword,
    'rtree': Token.Keyword,
    'savepoint': Token.Keyword,
    'schedule': Token.Keyword,
    'schema_name': Token.Keyword,
    'second': Token.Keyword,
    'secondary': Token.Keyword,
    'secondary_engine': Token.Keyword,
    'secondary_engine_a': Token.Keyword,
    'secondary_load': Token.Keyword,
    'secondary_unload': Token.Keyword,
    'security': Token.Keyword,
    'serial': Token.Keyword,
    'serializable': Token.Keyword,
    'server': Token.Keyword,
    'session': Token.Keyword,
    'share': Token.Keyword,
    'shutdown': Token.Keyword,
    'signed': Token.Keyword,
    'simple': Token.Keyword,
    'skip': Token.Keyword,
    'slave': Token.Keyword,
    'slow': Token.Keyword,
    'snapshot': Token.Keyword,
    'socket': Token.Keyword,
    'some': Token.Keyword,
    'soname': Token.Keyword,
    'source': Token.Keyword,
    'source_connection_': Token.Keyword,
    'sql_after_gtids': Token.Keyword,
    'sql_after_mts_gaps': Token.Keyword,
    'sql_buffer_result': Token.Keyword,
    'sql_no_cache': Token.Keyword,
    'sql_thread': Token.Keyword,
    'sql_tsi_day': Token.Keyword,
    'sql_tsi_hour': Token.Keyword,
    'sql_tsi_minute': Token.Keyword,
    'sql_tsi_month': Token.Keyword,
    'sql_tsi_quarter': Token.Keyword,
    'sql_tsi_second': Token.Keyword,
    'sql_tsi_week': Token.Keyword,
    'sql_tsi_year': Token.Keyword,
    'srid': Token.Keyword,
    'stacked': Token.Keyword,
    'start': Token.Keyword,
    'starts': Token.Keyword,
    'stats_auto_recalc': Token.Keyword,
    'stats_persistent': Token.Keyword,
    'stats_sample_pages': Token.Keyword,
    'status': Token.Keyword,
    'stop': Token.Keyword,
    'storage': Token.Keyword,
    'stream': Token.Keyword,
    'string': Token.Keyword,
    'subclass_origin': Token.Keyword,
    'subject': Token.Keyword,
    'subpartition': Token.Keyword,
    'subpartitions': Token.Keyword,
    'super': Token.Keyword,
    'suspend': Token.Keyword,
    'swaps': Token.Keyword,
    'switches': Token.Keyword,
    'tables': Token.Keyword,
    'tablespace': Token.Keyword,
    'table_checksum': Token.Keyword,
    'table_name': Token.Keyword,
    'temporary': Token.Keyword,
    'temptable': Token.Keyword,
    'text': Token.Keyword,
    'than': Token.Keyword,
    'thread_priority': Token.Keyword,
    'ties': Token.Keyword,
    'time': Token.Keyword,
    'timestamp': Token.Keyword,
    'timestampadd': Token.Keyword,
    'timestampdiff': Token.Keyword,
    'tls': Token.Keyword,
    'transaction': Token.Keyword,
    'triggers': Token.Keyword,
    'truncate': Token.Keyword,
    'type': Token.Keyword,
    'types': Token.Keyword,
    'unbounded': Token.Keyword,
    'uncommitted': Token.Keyword,
    'undefined': Token.Keyword,
    'undofile': Token.Keyword,
    'undo_buffer_size': Token.Keyword,
    'unicode': Token.Keyword,
    'uninstall': Token.Keyword,
    'unknown': Token.Keyword,
    'until': Token.Keyword,
    'upgrade': Token.Keyword,
    'user': Token.Keyword,
    'user_resources': Token.Keyword,
    'use_frm': Token.Keyword,
    'validation': Token.Keyword,
    'value': Token.Keyword,
    'variables': Token.Keyword,
    'vcpu': Token.Keyword,
    'view': Token.Keyword,
    'visible': Token.Keyword,
    'wait': Token.Keyword,
    'warnings': Token.Keyword,
    'week': Token.Keyword,
    'weight_string': Token.Keyword,
    'without': Token.Keyword,
    'work': Token.Keyword,
    'wrapper': Token.Keyword,
    'x509': Token.Keyword,
    'xa': Token.Keyword,
    'xid': Token.Keyword,
    'xml': Token.Keyword,
    'year': Token.Keyword,
    'zone': Token.Keyword,
}
index['keywords'] = keywords

functions = {
    'abs': Token.Function,
    'acos': Token.Function,
    'adddate': Token.Function,
    'addtime': Token.Function,
    'aes_decrypt': Token.Function,
    'aes_encrypt': Token.Function,
    'any_value': Token.Function,
    'ascii': Token.Function,
    'asin': Token.Function,
    'atan2': Token.Function,
    'atan': Token.Function,
    'avg': Token.Function,
    'benchmark': Token.Function,
    'bin': Token.Function,
    'bin_to_uuid': Token.Function,
    'bit_and': Token.Function,
    'bit_count': Token.Function,
    'bit_length': Token.Function,
    'bit_or': Token.Function,
    'bit_xor': Token.Function,
    'ceiling': Token.Function,
    'ceil': Token.Function,
    'character_length': Token.Function,
    'char_length': Token.Function,
    'charset': Token.Function,
    'char': Token.Function,
    'coercibility': Token.Function,
    'collation': Token.Function,
    'compress': Token.Function,
    'concat': Token.Function,
    'concat_ws': Token.Function,
    'connection_id': Token.Function,
    'convert_tz': Token.Function,
    'conv': Token.Function,
    'cos': Token.Function,
    'cot': Token.Function,
    'count': Token.Function,
    'count': Token.Function,
    'crc32': Token.Function,
    'cume_dist': Token.Function,
    'curdate': Token.Function,
    'current_date': Token.Function,
    'current_role': Token.Function,
    'current_timestamp': Token.Function,
    'current_time': Token.Function,
    'current_user': Token.Function,
    'curtime': Token.Function,
    'database': Token.Function,
    'date_add': Token.Function,
    'datediff': Token.Function,
    'date_format': Token.Function,
    'date_sub': Token.Function,
    'date': Token.Function,
    'dayname': Token.Function,
    'dayofmonth': Token.Function,
    'dayofweek': Token.Function,
    'dayofyear': Token.Function,
    'day': Token.Function,
    'default': Token.Function,
    'degrees': Token.Function,
    'dense_rank': Token.Function,
    'elt': Token.Function,
    'export_set': Token.Function,
    'exp': Token.Function,
    'extract': Token.Function,
    'extractvalue': Token.Function,
    'field': Token.Function,
    'find_in_set': Token.Function,
    'first_value': Token.Function,
    'floor': Token.Function,
    'format_bytes': Token.Function,
    'format_pico_time': Token.Function,
    'format': Token.Function,
    'found_rows': Token.Function,
    'from_base64': Token.Function,
    'from_days': Token.Function,
    'from_unixtime': Token.Function,
    'geomcollection': Token.Function,
    'geometrycollection': Token.Function,
    'get_format': Token.Function,
    'get_lock': Token.Function,
    'group_concat': Token.Function,
    'grouping': Token.Function,
    'gtid_subset': Token.Function,
    'gtid_subtract': Token.Function,
    'hex': Token.Function,
    'hour': Token.Function,
    'icu_version': Token.Function,
    'ifnull': Token.Function,
    'inet6_aton': Token.Function,
    'inet6_ntoa': Token.Function,
    'inet_aton': Token.Function,
    'inet_ntoa': Token.Function,
    'insert': Token.Function,
    'instr': Token.Function,
    'is_free_lock': Token.Function,
    'is_ipv4_compat': Token.Function,
    'is_ipv4_mapped': Token.Function,
    'is_ipv4': Token.Function,
    'is_ipv6': Token.Function,
    'is_used_lock': Token.Function,
    'is_uuid': Token.Function,
    'json_arrayagg': Token.Function,
    'json_array_append': Token.Function,
    'json_array_insert': Token.Function,
    'json_array': Token.Function,
    'json_contains_path': Token.Function,
    'json_contains': Token.Function,
    'json_depth': Token.Function,
    'json_extract': Token.Function,
    'json_insert': Token.Function,
    'json_keys': Token.Function,
    'json_length': Token.Function,
    'json_merge_patch': Token.Function,
    'json_merge_preserve': Token.Function,
    'json_merge': Token.Function,
    'json_objectagg': Token.Function,
    'json_object': Token.Function,
    'json_overlaps': Token.Function,
    'json_pretty': Token.Function,
    'json_quote': Token.Function,
    'json_remove': Token.Function,
    'json_replace': Token.Function,
    'json_schema_validation_report': Token.Function,
    'json_schema_valid': Token.Function,
    'json_search': Token.Function,
    'json_set': Token.Function,
    'json_storage_free': Token.Function,
    'json_storage_size': Token.Function,
    'json_table': Token.Function,
    'json_type': Token.Function,
    'json_unquote': Token.Function,
    'json_valid': Token.Function,
    'json_value': Token.Function,
    'lag': Token.Function,
    'last_day': Token.Function,
    'last_insert_id': Token.Function,
    'last_value': Token.Function,
    'lcase': Token.Function,
    'lead': Token.Function,
    'left': Token.Function,
    'length': Token.Function,
    'linestring': Token.Function,
    'ln': Token.Function,
    'load_file': Token.Function,
    'localtimestamp': Token.Function,
    'localtime': Token.Function,
    'locate': Token.Function,
    'log10': Token.Function,
    'log2': Token.Function,
    'log': Token.Function,
    'lower': Token.Function,
    'lpad': Token.Function,
    'ltrim': Token.Function,
    'makedate': Token.Function,
    'make_set': Token.Function,
    'maketime': Token.Function,
    'master_pos_wait': Token.Function,
    'match': Token.Function,
    'max': Token.Function,
    'mbrcontains': Token.Function,
    'mbrcoveredby': Token.Function,
    'mbrcovers': Token.Function,
    'mbrdisjoint': Token.Function,
    'mbrequals': Token.Function,
    'mbrintersects': Token.Function,
    'mbroverlaps': Token.Function,
    'mbrtouches': Token.Function,
    'mbrwithin': Token.Function,
    'md5': Token.Function,
    'microsecond': Token.Function,
    'mid': Token.Function,
    'min': Token.Function,
    'minute': Token.Function,
    'mod': Token.Function,
    'monthname': Token.Function,
    'month': Token.Function,
    'multilinestring': Token.Function,
    'multipoint': Token.Function,
    'multipolygon': Token.Function,
    'name_const': Token.Function,
    'now': Token.Function,
    'nth_value': Token.Function,
    'ntile': Token.Function,
    'nullif': Token.Function,
    'octet_length': Token.Function,
    'oct': Token.Function,
    'ord': Token.Function,
    'percent_rank': Token.Function,
    'period_add': Token.Function,
    'period_diff': Token.Function,
    'pi': Token.Function,
    'point': Token.Function,
    'polygon': Token.Function,
    'position': Token.Function,
    'power': Token.Function,
    'pow': Token.Function,
    'ps_current_thread_id': Token.Function,
    'ps_thread_id': Token.Function,
    'quarter': Token.Function,
    'quote': Token.Function,
    'radians': Token.Function,
    'random_bytes': Token.Function,
    'rand': Token.Function,
    'rank': Token.Function,
    'regexp_instr': Token.Function,
    'regexp_like': Token.Function,
    'regexp_replace': Token.Function,
    'regexp_substr': Token.Function,
    'release_all_locks': Token.Function,
    'release_lock': Token.Function,
    'repeat': Token.Function,
    'replace': Token.Function,
    'reverse': Token.Function,
    'right': Token.Function,
    'roles_graphml': Token.Function,
    'round': Token.Function,
    'row_count': Token.Function,
    'row_number': Token.Function,
    'rpad': Token.Function,
    'rtrim': Token.Function,
    'schema': Token.Function,
    'second': Token.Function,
    'sec_to_time': Token.Function,
    'session_user': Token.Function,
    'sha1': Token.Function,
    'sha2': Token.Function,
    'sha': Token.Function,
    'sign': Token.Function,
    'sin': Token.Function,
    'sleep': Token.Function,
    'soundex': Token.Function,
    'space': Token.Function,
    'sqrt': Token.Function,
    'st_area': Token.Function,
    'st_asbinary': Token.Function,
    'st_asgeojson': Token.Function,
    'st_astext': Token.Function,
    'statement_digest_text': Token.Function,
    'statement_digest': Token.Function,
    'st_buffer_strategy': Token.Function,
    'st_buffer': Token.Function,
    'st_centroid': Token.Function,
    'st_contains': Token.Function,
    'st_convexhull': Token.Function,
    'st_crosses': Token.Function,
    'stddev_pop': Token.Function,
    'stddev_samp': Token.Function,
    'stddev': Token.Function,
    'st_difference': Token.Function,
    'st_dimension': Token.Function,
    'st_disjoint': Token.Function,
    'st_distance_sphere': Token.Function,
    'st_distance': Token.Function,
    'std': Token.Function,
    'st_endpoint': Token.Function,
    'st_envelope': Token.Function,
    'st_equals': Token.Function,
    'st_exteriorring': Token.Function,
    'st_frechetdistance': Token.Function,
    'st_geohash': Token.Function,
    'st_geomcollfromtext': Token.Function,
    'st_geomcollfromwkb': Token.Function,
    'st_geometryn': Token.Function,
    'st_geometrytype': Token.Function,
    'st_geomfromgeojson': Token.Function,
    'st_geomfromtext': Token.Function,
    'st_geomfromwkb': Token.Function,
    'st_hausdorffdistance': Token.Function,
    'st_interiorringn': Token.Function,
    'st_intersection': Token.Function,
    'st_intersects': Token.Function,
    'st_isclosed': Token.Function,
    'st_isempty': Token.Function,
    'st_issimple': Token.Function,
    'st_isvalid': Token.Function,
    'st_latfromgeohash': Token.Function,
    'st_latitude': Token.Function,
    'st_length': Token.Function,
    'st_linefromtext': Token.Function,
    'st_linefromwkb': Token.Function,
    'st_lineinterpolatepoints': Token.Function,
    'st_lineinterpolatepoint': Token.Function,
    'st_longfromgeohash': Token.Function,
    'st_longitude': Token.Function,
    'st_makeenvelope': Token.Function,
    'st_mlinefromtext': Token.Function,
    'st_mlinefromwkb': Token.Function,
    'st_mpointfromtext': Token.Function,
    'st_mpointfromwkb': Token.Function,
    'st_mpolyfromtext': Token.Function,
    'st_mpolyfromwkb': Token.Function,
    'st_numgeometries': Token.Function,
    'st_numinteriorring': Token.Function,
    'st_numpoints': Token.Function,
    'st_overlaps': Token.Function,
    'st_pointatdistance': Token.Function,
    'st_pointfromgeohash': Token.Function,
    'st_pointfromtext': Token.Function,
    'st_pointfromwkb': Token.Function,
    'st_pointn': Token.Function,
    'st_polyfromtext': Token.Function,
    'st_polyfromwkb': Token.Function,
    'strcmp': Token.Function,
    'str_to_date': Token.Function,
    'st_simplify': Token.Function,
    'st_srid': Token.Function,
    'st_startpoint': Token.Function,
    'st_swapxy': Token.Function,
    'st_symdifference': Token.Function,
    'st_touches': Token.Function,
    'st_transform': Token.Function,
    'st_union': Token.Function,
    'st_validate': Token.Function,
    'st_within': Token.Function,
    'st_x': Token.Function,
    'st_y': Token.Function,
    'subdate': Token.Function,
    'substring_index': Token.Function,
    'substring': Token.Function,
    'substr': Token.Function,
    'subtime': Token.Function,
    'sum': Token.Function,
    'sysdate': Token.Function,
    'system_user': Token.Function,
    'tan': Token.Function,
    'timediff': Token.Function,
    'time_format': Token.Function,
    'timestampadd': Token.Function,
    'timestampdiff': Token.Function,
    'timestamp': Token.Function,
    'time': Token.Function,
    'time_to_sec': Token.Function,
    'to_base64': Token.Function,
    'to_days': Token.Function,
    'to_seconds': Token.Function,
    'trim': Token.Function,
    'truncate': Token.Function,
    'ucase': Token.Function,
    'uncompressed_length': Token.Function,
    'uncompress': Token.Function,
    'unhex': Token.Function,
    'unix_timestamp': Token.Function,
    'updatexml': Token.Function,
    'upper': Token.Function,
    'user': Token.Function,
    'utc_date': Token.Function,
    'utc_timestamp': Token.Function,
    'utc_time': Token.Function,
    'uuid_short': Token.Function,
    'uuid_to_bin': Token.Function,
    'uuid': Token.Function,
    'validate_password_strength': Token.Function,
    'values': Token.Function,
    'variance': Token.Function,
    'var_pop': Token.Function,
    'var_samp': Token.Function,
    'version': Token.Function,
    'wait_for_executed_gtid_set': Token.Function,
    'wait_until_sql_thread_after_gtids': Token.Function,
    'weekday': Token.Function,
    'weekofyear': Token.Function,
    'week': Token.Function,
    'weight_string': Token.Function,
    'year': Token.Function,
    'yearweek': Token.Function,
}
index['functions'] = functions

def classify(keyword):
    for keyword_dict in index:
        try:
            return index[keyword_dict][keyword.lower()]
        except KeyError:
            continue

    return Token.Other

