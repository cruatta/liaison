import syslog
import sys
import json
import time


def write(pri, level, message):
    """
    Encode a log message as a JSON object and write it to syslog.
    Currently just uses syslog, and if unattended, writes the log messages
    to stdout so they can be piped elsewhere.

    Inspired by: https://github.com/ryanuber/pakrat/blob/master/pakrat/log.py

    :type pri: int
    :type level: str
    :type message: str

    :param pri: Syslog Priority
    :param level: Priority as string
    :param message: Log message
    """
    log = json.dumps({'time': time.time(), 'level': level, 'message': message})

    syslog.openlog('liaison')
    syslog.syslog(pri, log)
    if not sys.stdout.isatty():
        print(log)


def debug(log):
    """
    Detailed error messages describing the exact state of
    internal variables that may be helpful when debugging problems.

    :type log: str
    :param log: Structured log message
    """
    write(syslog.LOG_DEBUG, 'debug', '{}'.format(log))


def info(log):
    """
     For completely informational purposes, the application is
     simply logging what it is doing.

    :type log: str
    :param log: Structured log message
    """
    write(syslog.LOG_INFO, 'info', '{}'.format(log))


def warning(log):
    """
    The application encountered a situation that it was not expecting,
    but it can continue.

    :type log: str
    :param log: Structured log message
    """
    write(syslog.LOG_WARNING, 'warning', '{}'.format(log))


def error(log):
    """
    An error occurred that should be logged, however it is not critical.

    :type log: str
    :param log: Structured log message
    """
    write(syslog.LOG_ERR, 'error', '{}'.format(log))


def critical(log):
    """
    A serious error occurred during application execution.

    :type log: str
    :param log: Structured log message
    """
    write(syslog.LOG_CRIT, 'info', '{}'.format(log))
