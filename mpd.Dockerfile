FROM alpine:latest

COPY mpd.conf /etc/mpd.conf.new

RUN set -eux ; \
    apk --no-cache add \
        mpd \
        mpc \
    ; \
    mkdir /var/lib/mpd/data ; \
    touch /var/lib/mpd/data/database \
        /var/lib/mpd/data/state \
        /var/lib/mpd/data/sticker.sql \
    ; \
    chown -R mpd:audio /var/lib/mpd ; \
    cp /etc/mpd.conf /etc/mpd.conf.backup ; \
    mv /etc/mpd.conf.new /etc/mpd.conf ; \
    chown -R mpd:audio /etc/mpd.con*

VOLUME /var/lib/mpd
WORKDIR /var/lib/mpd
EXPOSE 6600 8000

CMD ["/usr/bin/mpd", "--no-daemon", "--stdout", "/etc/mpd.conf"]