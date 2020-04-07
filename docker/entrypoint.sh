#!/bin/sh
set -e

if [ "$1" = "start-http" ];
then
  uwsgi \
    --plugins http,python \
    --http 0.0.0.0:3001 \
    --uid=uwsgi \
    --gid=uwsgi \
    --master \
    --module=letscheck.wsgi:application
    --processes 4
elif [ "$1" = "start-wsgi" ];
then
  uwsgi --socket=0.0.0.0:3031 \
          --uid=uwsgi \
          --plugins=python3 \
          --protocol=uwsgi \
          --module=letscheck.wsgi:application
else
  python3 manage.py $@
fi
