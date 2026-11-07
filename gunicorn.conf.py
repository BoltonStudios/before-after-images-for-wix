"""
Gunicorn settings loaded automatically from ./gunicorn.conf.py.

The hosting buildpack enables access logging (GUNICORN_CMD_ARGS="--access-logfile -").
This format keeps operational detail (time, method, path, status, size, duration)
but omits the query string, which carries Wix's signed `instance` parameter
(including the anonymous visitor ID), plus the client address, referrer and user agent.

Only the log format is set here, so worker count and bind address stay as configured
by the run command and the platform.
"""

# %(U)s is the URL path without the query string; %(L)s is request time in seconds.
access_log_format = '%(t)s "%(m)s %(U)s %(H)s" %(s)s %(b)s %(L)ss'
