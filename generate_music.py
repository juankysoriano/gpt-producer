import os
import subprocess
import tempfile
import uuid

import requests
import runpod
import torchaudio
from audiocraft.data.audio import audio_write
from audiocraft.models import MusicGen
from google.cloud import storage

## load your model(s) into vram here
model = MusicGen.get_pretrained("melody")


def generate(prompt, abc):
    melody_path = abc_to_mp3(abc)
    result = do_post_production(melody_path, prompt)
    return result


def abc_to_mp3(abc):
    # Create a temporary file to store the ABC content
    with tempfile.NamedTemporaryFile(
        suffix=".abc", delete=False
    ) as tmp_abc_file:
        # Write the ABC content to the temporary file
        tmp_abc_file.write(abc.encode())
        tmp_abc_file.flush()

        # Temporary file names for the conversion process
        tmp_midi_file = tmp_abc_file.name + ".mid"
        tmp_wav_file = tmp_abc_file.name + ".wav"

        # Convert ABC to MIDI using abc2midi
        command_abc_to_midi = f"abc2midi {tmp_abc_file.name} -o {tmp_midi_file}"
        subprocess.run(command_abc_to_midi, shell=True)

        # Convert MIDI to WAV using Timidity
        command_midi_to_wav = f"timidity {tmp_midi_file} -Ow -o {tmp_wav_file}"
        subprocess.run(command_midi_to_wav, shell=True)

        # Convert WAV to MP3 using FFmpeg
        output_mp3 = "motif.mp3"
        command_wav_to_mp3 = f"ffmpeg -i {tmp_wav_file} -codec:a libmp3lame -qscale:a 2 {output_mp3}"
        subprocess.run(command_wav_to_mp3, shell=True)

        # Optionally, delete temporary files
        os.remove(tmp_abc_file.name)
        os.remove(tmp_midi_file)
        os.remove(tmp_wav_file)

        return output_mp3


def do_post_production(parameters, motif_path, prompt):
    model.set_generation_params(duration=30)
    melody, sr = torchaudio.load(motif_path)
    wav = model.generate_with_chroma(
        [prompt], melody[None].expand(1, -1, -1), sr
    )[0]
    audio_write("output", wav.cpu(), model.sample_rate, format="mp3")
    return "output.mp3"
