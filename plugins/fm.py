
import numpy as np

PARAMETERS = {
    "deviation": "Frequency deviation of the FM signal in Hz"
}

def decode(samples, params):
    deviation = params.get('deviation', 75000)
    angles = np.angle(samples[1:] * np.conj(samples[:-1]))
    return np.unwrap(angles)

def squelch(audio):
    threshold = 0.01
    return np.max(np.abs(audio)) > threshold
