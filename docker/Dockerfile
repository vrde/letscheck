FROM alpine:3

# App specific variables
ENV APP_DEBUG=0
ENV APP_STATIC_ROOT=/app/static
ENV APP_MEDIA_ROOT=/app/media

ENV PYTHONUNBUFFERED 1
EXPOSE 3001
# VOLUME ["/app/static", "/app/media"]

RUN apk add --no-cache \
        uwsgi-http \
        uwsgi-python3 \
        python3

COPY src /app/src
RUN pip3 install --no-cache-dir -r /app/src/requirements.txt
RUN python3 /app/src/manage.py collectstatic

COPY docker/entrypoint.sh /app

WORKDIR /app/src
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["start"]
