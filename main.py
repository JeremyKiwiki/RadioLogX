
import os
import json
import importlib
import rtlsdr
import pyaudio
from datetime import datetime
import numpy as np
import wave

def select_config_file():
    config_files = [f for f in os.listdir('config') if f.endswith('.json')]
    print("Available configuration files:")
    for i, filename in enumerate(config_files):
        print(f"{i}: {filename}")
    file_index = int(input("Select the configuration file index: "))
    return os.path.join('config', config_files[file_index])

def select_rtl_sdr():
    try:
        sdrs = rtlsdr.RtlSdr.get_device_serial_addresses()
        print(f"Found {len(sdrs)} device(s):")
        for i, sdr in enumerate(sdrs):
            print(f"Device {i}: {sdr}")
        device_index = int(input("Select the RTL-SDR device index: "))
        return device_index
    except Exception as e:
        print(f"Error finding RTL-SDR devices: {e}")
        exit(1)

def log_recording(text):
    with open('recordings/logs.txt', 'a') as f:
        f.write(f"{datetime.now()}: {text}\n")

def record(audio, filename):
    audio = (audio * 32767).astype(np.int16)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio.tobytes())

def process_samples(samples, freq, plugin, params, stream):
    decoded_audio = plugin.decode(samples, params)
    if plugin.squelch(decoded_audio):
        log_recording(f"Recording on frequency {freq / 1e6} MHz with params {params}")
        stream.write(decoded_audio.tobytes())
        record(decoded_audio, f"recordings/{freq}.wav")

if __name__ == "__main__":
    config_file = select_config_file()
    with open(config_file, 'r') as f:
        config = json.load(f)

    plugins = {}
    for filename in os.listdir('plugins'):
        if filename.endswith('.py'):
            module_name = filename[:-3]
            module = importlib.import_module(f'plugins.{module_name}')
            plugins[module_name] = module

    sdr_device_index = select_rtl_sdr()
    sdr = rtlsdr.RtlSdr(sdr_device_index)

    sdr.sample_rate = 1e6
    sdr.gain = 'auto'

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=24000,
                    output=True)

    try:
        while True:
            for freq_config in config['frequencies']:
                freq = freq_config['frequency']
                modulation = freq_config['modulation']
                params = freq_config.get('params', {})
                plugin = plugins[modulation]
                
                sdr.center_freq = freq
                samples = sdr.read_samples(256*1024)
                
                process_samples(samples, freq, plugin, params, stream)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        sdr.close()
