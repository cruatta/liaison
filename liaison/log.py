from __future__ import print_function
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

    :param pri: Syslog Priority
    :type pri: int

    :param level: Priority as string
    :type level: str

    :param message: Log message
    :type message: str
    """
    log = json.dumps({'time': time.time(), 'level': level, 'message': message})

    syslog.openlog('liaison')
    syslog.syslog(pri, log)
    if not sys.stdout.isatty():
        if pri in [syslog.LOG_DEBUG, syslog.LOG_INFO]:
            print(log, file=sys.stderr)
        else:
            print(log)


def debug(log):
    """
    Detailed error messages describing the exact state of
    internal variables that may be helpful when debugging problems.

    :param log: Structured log message
    :type log: str
    """
    write(syslog.LOG_DEBUG, 'debug', '{log}'.format(log=log))


def info(log):
    """
     For completely informational purposes, the application is
     simply logging what it is doing.

    :param log: Structured log message
    :type log: str
    """
    write(syslog.LOG_INFO, 'info', '{log}'.format(log=log))


def warning(log):
    """
    The application encountered a situation that it was not expecting,
    but it can continue.

    :param log: Structured log message
    :type log: str
    """
    write(syslog.LOG_WARNING, 'warning', '{log}'.format(log=log))


def error(log):
    """
    An error occurred that should be logged, however it is not critical.

    :param log: Structured log message
    :type log: str
    """
    write(syslog.LOG_ERR, 'error', '{log}'.format(log=log))


def critical(log):
    """
    A serious error occurred during application execution.

    :param log: Structured log message
    :type log: str
    """
    write(syslog.LOG_CRIT, 'info', '{log}'.format(log=log))
