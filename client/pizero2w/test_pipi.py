#!/usr/bin/env python3
import pvporcupine, pyaudio, struct, sys, os

ACCESS_KEY = os.getenv("PV_ACCESS_KEY", "YOUR_PICOVOICE_ACCESS_KEY")

# Path to custom wake word model
keyword_paths = [os.path.join(os.path.dirname(__file__), "hey-pee-dar_en_raspberry-pi_v3_0_0.ppn")]
keywords = ["hey pee dar"]  # for display purposes
porcupine = pvporcupine.create(access_key=ACCESS_KEY, keyword_paths=keyword_paths)

pa = pyaudio.PyAudio()
stream = pa.open(rate=porcupine.sample_rate,
                 channels=1, format=pyaudio.paInt16,
                 input=True, frames_per_buffer=porcupine.frame_length)

print("Listening... Say:", ", ".join(keywords))
try:
    while True:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        idx = porcupine.process(pcm)
        if idx >= 0:
            print(f"Wake word: {keywords[idx]}")
            # TODO: вызвать вашу логику
except KeyboardInterrupt:
    pass
finally:
    stream.stop_stream(); stream.close(); pa.terminate(); porcupine.delete()
