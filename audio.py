import math
import array
import pyaudio
from random import randint


# Audio helper constants
_T = 11025
_q = 127
_p = -_q
_N = 255 * 4


class SoundFX:
    # Defined sounds
    NO_SOUND = ''
    CRASH_SOUND = array.array('b', (max(_p, min(_q, int(_T * math.sin(i * 0.01))))
                                    for i in range(_N))).tostring()
    THRUST_SOUND = array.array('b', (randint(_p, _q)
                                     for i in range(_N))).tostring()

    def __init__(self):

        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(rate=_T, channels=1,
                                   format=pyaudio.paInt8, output=True)
        self.sound_stream = self.NO_SOUND

    def set_sound_stream(self, sound_stream):
        self.sound_stream = sound_stream

    def play(self, sound_stream=None):
        ss = sound_stream if sound_stream is not None else self.sound_stream
        self.stream.write(ss)
        # If internal sound_stream was used, reset it (already played)
        if sound_stream is None:
            self.sound_stream = self.NO_SOUND

    def terminate(self):
        self.stream.close()
        self.pa.terminate()
