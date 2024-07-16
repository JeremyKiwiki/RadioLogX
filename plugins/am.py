
import numpy as np
import scipy.signal as signal

PARAMETERS = {
    "bandwidth": "Bandwidth of the AM signal in Hz"
}

def decode(samples, params):
    samples = np.real(samples)
    bandwidth = params.get('bandwidth', 10000)
    analytic_signal = signal.hilbert(samples)
    amplitude_envelope = np.abs(analytic_signal)
    return amplitude_envelope

def squelch(audio):
    threshold = 0.01
    return np.max(np.abs(audio)) > threshold
