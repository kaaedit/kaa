import logging, os

class KaaError(Exception):
    pass

LOGFILE = os.path.join(
        os.path.expandvars(os.path.expanduser('~/kaa.log')))

logging.basicConfig(
        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
        datefmt='%Y/%m/%d %H:%M:%S',
        level=logging.DEBUG, 
        handlers=[logging.FileHandler(filename=LOGFILE, encoding='utf-8')])


LOG = logging.getLogger(__name__)

def _fmt(fmt, args, kwargs):
    msg = fmt.format(*args, **kwargs)
    return msg

def _log(out, fmt, *args, **kwargs):
    out(fmt.format(*args, **kwargs), exc_info=kwargs.get('exc_info'),
              extra=kwargs.get('extra'), stack_info=kwargs.get('stack_info'))


def debug(*args, **kwargs):
    _log(LOG.debug, *args, **kwargs)

def info(*args, **kwargs):
    _log(LOG.info, *args, **kwargs)

def warning(*args, **kwargs):
    _log(LOG.warning, *args, **kwargs)

def error(*args, **kwargs):
    _log(LOG.error, *args, **kwargs)

def critical(*args, **kwargs):
    _log(LOG.critical, *args, **kwargs)

def exception(fmt, *args, **kwargs):
    LOG.exception(fmt.format(*args, **kwargs))

import kaa.tools
