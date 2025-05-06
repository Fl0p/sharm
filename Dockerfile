FROM debian:bookworm

ENV SHARM=true

ARG FIFO_PATH
ENV FIFO_PATH=${FIFO_PATH}

ARG MPD_CLIENT_PORT
ENV MPD_CLIENT_PORT=${MPD_CLIENT_PORT}

ARG MPD_STREAM_PORT
ENV MPD_STREAM_PORT=${MPD_STREAM_PORT}

ARG SNAPSERVER_PORT
ENV SNAPSERVER_PORT=${SNAPSERVER_PORT}

ARG SNAPSERVER_HTTP_PORT
ENV SNAPSERVER_HTTP_PORT=${SNAPSERVER_HTTP_PORT}

ARG YMPD_PORT
ENV YMPD_PORT=${YMPD_PORT}

ENV TZ=Europe/Rome
ARG DEBIAN_FRONTEND=noninteractive

ARG SNAP_DEV_ARM="https://github.com/badaix/snapcast/releases/download/v0.31.0/snapserver_0.31.0-1_arm64_bookworm.deb"
ARG SNAP_DEV_AMD="https://github.com/badaix/snapcast/releases/download/v0.31.0/snapserver_0.31.0-1_amd64_bookworm.deb"

RUN set -eux

RUN apt-get update

RUN apt-get install -y --no-install-recommends \
        ca-certificates \
        wget \
        git \
        alsa-utils \
        libasound2 \
        mpd \
        mpc \
        timidity \
        libmpdclient-dev \
        cmake \
        build-essential \
        libtool \
        pkg-config \
        libssl-dev \
        gettext

RUN update-ca-certificates

RUN rm -rf /var/lib/apt/lists/*

# alsa
COPY asound.conf /etc/asound.conf

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

#snapcast
RUN if [ "$(uname -m)" = "x86_64" ]; then \
    wget -O /tmp/snapserver.deb ${SNAP_DEV_AMD}; \
    else \
    wget -O /tmp/snapserver.deb ${SNAP_DEV_ARM}; \
    fi
RUN dpkg -i /tmp/snapserver.deb
RUN apt-get -f install
RUN rm /tmp/snapserver.deb

RUN snapserver -v

COPY snapserver.conf /home/snapserver.conf
RUN echo "FIFO_PATH=${FIFO_PATH}"
RUN envsubst < /home/snapserver.conf > /etc/snapserver.conf

EXPOSE 1704 1705

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