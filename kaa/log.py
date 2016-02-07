import logging
import logging.handlers
import os


def init(logdir):
    logfile = os.path.join(logdir, 'kaa.log')

    logging.basicConfig(
        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
        datefmt='%Y/%m/%d %H:%M:%S',
        level=logging.DEBUG,
        handlers=[logging.handlers.RotatingFileHandler(
                filename=logfile, encoding='utf-8',
            maxBytes=10 * 1024 * 1024)])

    global LOG, debug, info, warning, error, critical, exception
    LOG = logging.getLogger('kaa')

    debug = LOG.debug
    info = LOG.info
    warning = LOG.warning
    error = LOG.error
    critical = LOG.critical
    exception = LOG.exception
