#!/bin/bash
set -e

XDG_RUNTIME_DIR="/tmp/xdg_runtime"

# Функция для корректного завершения (адаптировать для PA)
cleanup() {
    echo "Stopping services..."
    # Останавливаем в обратном порядке
    if pgrep -u "$USER" -f "snapserver -c /etc/snapserver.conf" > /dev/null; then
        pkill -u "$USER" -SIGTERM -f "snapserver -c /etc/snapserver.conf" && echo "Snapserver stopping..."
        # Дать время на корректное завершение
        c=0; while pgrep -u "$USER" -f "snapserver -c /etc/snapserver.conf" > /dev/null && [ $c -lt 10 ]; do sleep 0.5; c=$((c+1)); done
        if pgrep -u "$USER" -f "snapserver -c /etc/snapserver.conf" > /dev/null; then pkill -u "$USER" -SIGKILL -f "snapserver -c /etc/snapserver.conf"; echo "Snapserver killed."; fi
    fi

    if [ -f /var/run/mpd/pid ]; then
        mpd --kill || echo "MPD not running or failed to stop."
    fi

    # Останавливаем PulseAudio
    # Сначала пробуем корректно через pactl, потом через pulseaudio -k, потом kill
    if pactl info > /dev/null 2>&1 ; then
        PULSE_SINK_ID=$(pactl list short sinks | grep "snapcast_pa_sink" | awk '{print $1}')
        if [ -n "$PULSE_SINK_ID" ]; then
            pactl unload-module module-null-sink sink_name=snapcast_pa_sink # Удаляем наш модуль
        fi
        pulseaudio -k && echo "PulseAudio stopping via -k..." || echo "PulseAudio -k failed or PA not running."
    fi
    # Дополнительная проверка и kill, если PA все еще работает
    if pgrep -u "$USER" pulseaudio > /dev/null; then
        pkill -u "$USER" -SIGTERM pulseaudio
        sleep 1
        if pgrep -u "$USER" pulseaudio > /dev/null; then
            pkill -u "$USER" -SIGKILL pulseaudio
            echo "PulseAudio killed."
        else
            echo "PulseAudio stopped by TERM."
        fi
    fi
    echo "Cleanup finished."
    exit 0
}
trap cleanup SIGTERM SIGINT

mkdir -p "$XDG_RUNTIME_DIR/pulse" # Ensure log directory exists
echo "Starting PulseAudio..."
pulseaudio --daemonize --exit-idle-time=-1 --log-target=newfile:"$XDG_RUNTIME_DIR/pulse/pulseaudio.log" --log-level=info
# Ждем, пока PulseAudio запустится
c=0
while ! pactl info > /dev/null 2>&1 ; do
    sleep 0.5
    c=$((c+1))
    if [ $c -gt 20 ]; then
        echo "PulseAudio failed to start. Check $XDG_RUNTIME_DIR/pulse/pulseaudio.log"
        cat "$XDG_RUNTIME_DIR/pulse/pulseaudio.log" || true
        exit 1
    fi
done
echo "PulseAudio started."

echo "Configuring PulseAudio sink for ALSA..."
# Создаем null-sink, на который будет писать ALSA. Имя должно совпадать с asound.conf.
# Имя sink'а 'snapcast_pa_sink' должно совпадать с 'device' в ALSA pcm типа pulse.
pactl load-module module-null-sink sink_name=snapcast_pa_sink sink_properties=device.description="ALSA_to_Snapcast_Input_Sink"
echo "PulseAudio sink 'snapcast_pa_sink' created."