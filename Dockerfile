FROM debian:bookworm

ENV SHARM=true

ARG YMPD_PORT
ENV YMPD_PORT=${YMPD_PORT}

ARG MPD_CLIENT_PORT
ENV MPD_CLIENT_PORT=${MPD_CLIENT_PORT}

ARG MPD_STREAM_PORT
ENV MPD_STREAM_PORT=${MPD_STREAM_PORT}

ENV TZ=Europe/Rome
ARG DEBIAN_FRONTEND=noninteractive

RUN set -eux

RUN apt-get update && \
    apt-get install -y git ca-certificates && \
    update-ca-certificates

RUN apt-get install -y --no-install-recommends \
        mpd \
        mpc \
        timidity \
        libmpdclient-dev \
        git \
        cmake \
        build-essential \
        libtool \
        pkg-config \
        libssl-dev \
        gettext
    
RUN rm -rf /var/lib/apt/lists/*

# mpd
RUN mkdir -p /var/lib/mpd/data ; \
    touch /var/lib/mpd/data/database \
        /var/lib/mpd/data/state \
        /var/lib/mpd/data/sticker.sql

COPY mpd.conf /home/mpd.conf

RUN echo "MPD_CLIENT_PORT=${MPD_CLIENT_PORT}"
RUN echo "MPD_STREAM_PORT=${MPD_STREAM_PORT}"
RUN envsubst < /home/mpd.conf > /etc/mpd.conf

RUN chown -R mpd:audio /var/lib/mpd ; \
    chown -R mpd:audio /etc/mpd.conf ; \
    mkdir -p /run/mpd && chown -R mpd:audio /run/mpd
    

VOLUME /var/lib/mpd
WORKDIR /var/lib/mpd
EXPOSE 6600 8000

# ympd

RUN mkdir -p /var/lib/ympd ; \
    chown -R mpd:audio /var/lib/ympd

WORKDIR /var/lib/ympd

RUN git clone https://github.com/notandy/ympd.git /var/lib/ympd

RUN cmake . -DCMAKE_C_FLAGS="-fcommon" -DCMAKE_INSTALL_PREFIX=/usr && \
    make && \
    make install

EXPOSE ${YMPD_PORT}

# start
WORKDIR /home

# copy .env
COPY .env /home/.env

# copy start.sh
COPY start.sh /home/start.sh
RUN chmod +x /home/start.sh

CMD ["/home/start.sh"]