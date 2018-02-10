# coding=utf-8

import shutil
import time
import sys
import os.path
import re
import ConfigParser
import traceback
import logging.handlers
import platform

# load_sql_file = r'd:\tmp\etrans\etrans_load_doc_data.sql'
load_sql_file = '/tmp/etrans_load_doc_data.sql'

# config_file = r'd:\tmp\etrans\etc\conf.ini'
config_file = '/usr/local/etrans/etc/conf.ini'

log_file = '/usr/local/etrans/log/etrans.log'


def get_configs():
    config_parser = ConfigParser.ConfigParser()
    config_parser.read(config_file)

    return {
        'source_dir': config_parser.get('Path', 'SourceDirectory'),
        'target_dir': config_parser.get('Path', 'TargetDirectory'),
        'db_server': config_parser.get('Database', 'DatabaseServer'),
        'db_name': config_parser.get('Database', 'DatabaseName'),
        'db_user': config_parser.get('Database', 'DatabaseUser'),
        'db_pass': config_parser.get('Database', 'DatabasePass'),
    }


def load_doc_data(data_file):
    data_file = open(data_file, "r")

    sql_file = open(load_sql_file, "w")

    line = data_file.readline()

    data_file.close()

    columns = line.split("|")

    delete_sql = "delete from {database_name}.bp_shared_doc where id = '{id}';\n".format(
        database_name=configs['db_name'], id=columns[0]
    )

    insert_sql = (
            "insert into {database_name}.bp_shared_doc values " +
            "('{id}', '{name}', '{category_id}', '{keyword}', '{caption}', '{file_path}'" +
            ",{browse_times}, {download_times}, {comment_times}, {like_times}, {status}, '{opinion}'" +
            ", '{createby}', '{createtime}', '{lastmodifyby}', '{lastmodifytime}', {version}" +
            ");\n"
    ).format(
        database_name=configs['db_name'],
        id=columns[0], name=columns[1], category_id=columns[2], keyword=columns[3], caption=columns[4],
        file_path=columns[5], browse_times=columns[6], download_times=columns[7], comment_times=columns[8],
        like_times=columns[9], status=columns[10], opinion=columns[11], createby=columns[12],
        createtime=int(time.mktime(time.strptime(columns[13], '%Y-%m-%d %H:%M:%S'))), lastmodifyby=columns[14],
        lastmodifytime=int(time.mktime(time.strptime(columns[15], '%Y-%m-%d %H:%M:%S'))), version=columns[16]
    )

    sql_file.write(delete_sql)
    sql_file.write(insert_sql)

    sql_file.close()

    os.system("mysql -u{user} -p{password} < {sql_file}".format(
        user=configs['db_user'], password=configs['db_pass'], sql_file=load_sql_file))


def do_job():
    try:
        global configs
        configs = get_configs()

        search_pattern = re.compile('_data$')
        while True:
            logger.info('Checking directory %s ...' % configs['source_dir'])
            for root, sub_dirs, files in os.walk(configs['source_dir']):
                for afile in files:
                    if search_pattern.search(afile):
                        logger.info('Find source file %s' % afile)
                        source_file = os.path.join(configs['source_dir'], afile[:-5])
                        target_file = os.path.join(configs['target_dir'], afile[:-5])
                        if os.path.exists(source_file):
                            shutil.copy(source_file, target_file)
                            logger.info('Copied %s to %s' % (source_file, target_file))

                            load_doc_data(os.path.join(configs['source_dir'], afile))
                            logger.info('Document info is loaded.')

                            os.unlink(source_file)
                            os.unlink(os.path.join(configs['source_dir'], afile))
                        else:
                            logger.error('Source file %s is not found.' % source_file)
            time.sleep(3)
    except Exception as e:
        warning_message = traceback.format_exc()
        logger.error(warning_message)
        sys.exit(-1)


if __name__ == "__main__":
    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)

    global logger

    logger = logging.getLogger('doc-sync')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    os_version = platform.platform()

    if os_version.find('centos-6') > 0:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)

        try:
            while True:
                pid = os.fork()
                if pid > 0:
                    status = os.wait()
                    logger.error('Child process(%d) terminated with status %d' % (status[0], status[1]))
                    logger.error('Restarting ...')
                else:
                    logger.info('Document Sync server started.')
                    do_job()
        except Exception as e:
            warning_message = traceback.format_exc()
            logger.error(warning_message)
            sys.exit(-1)
    elif os_version.find('centos-7') > 0:
        do_job()
    else:
        logger.error('Unsupported platform %s' % os_version)
        sys.exit(1)
