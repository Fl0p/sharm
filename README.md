

#TO TRY
https://github.com/rawdlite/docker-rompr

#Issues:
https://github.com/jackaudio/jack2/issues/745


#testing from inside docker

cat /var/log/mpd/mpd.log

speaker-test -D jack_playback -c 6 -F FLOAT_LE
speaker-test -D jack_in -c 6

jack_lsp -c
jack_lsp -t -p