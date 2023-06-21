import os
import threading
import time
import wave

import numpy as np
import pyfiglet
import simpleaudio as sa
from playsound import playsound
from pydub import AudioSegment
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from scipy.io.wavfile import read

# Assuming generate_music, gpt_describe, and keyboard2abc are your own modules
import generate_music
import gpt_describe
import keyboard2abc

console = Console()
layout = Layout()

ascii_title = "The Rolling Stones 🎸"
colored_ascii_title = (
    f"[bold yellow]{pyfiglet.figlet_format(ascii_title)}[/bold yellow]"
)
description = colored_ascii_title + "\n\n"

# Define Panels
describe_music_panel = Panel(description, title="Rolling Stones Review")
generate_music_file_panel = Panel("", title="Generate Music File")
credits_panel = Panel("", title="Credits")


def update_layout(token, live):
    global description
    # Append the new token to the existing content
    description += token
    # Update the layout with the new content
    describe_music_panel.renderable = description
    live.update(layout)


def describe_music_section(prompt, abc, live):
    try:
        gpt_describe.describe_music(
            prompt, abc, lambda token: update_layout(token, live)
        )
    except:
        pass


def generate_and_play_music_section(prompt, abc, live, progress, task):
    try:
        # Dummy code to simulate the generation process, replace this with the real process
        for i in range(50):
            time.sleep(0.1)  # simulate work being done
            progress.update(task)
            live.update(layout)

        music_file_path = generate_music.generate(prompt, abc)

        # Replacing the progress bar with a success message
        ascii_waveform = (
            f"[bold purple]{ascii_art_waveform(music_file_path)}[/bold purple]"
        )
        layout["lower"].update(ascii_waveform)
        live.update(layout)
        playsound(music_file_path)
    except:
        pass


def ascii_art_waveform(path):
    # Load the audio file
    audio, sr = librosa.load(path)

    # Calculate the duration of the audio in seconds
    duration = librosa.get_duration(y=audio, sr=sr)

    # Set the width and height of the ASCII art representation
    width = 80
    height = 20

    # Calculate the number of audio samples per ASCII art column
    samples_per_column = len(audio) // width

    # Initialize the ASCII art representation
    ascii_art = [[" " for _ in range(width)] for _ in range(height)]

    # Iterate over each column of the ASCII art
    for i in range(width):
        # Calculate the starting and ending indices for the current column
        start_idx = i * samples_per_column
        end_idx = start_idx + samples_per_column

        # Extract the audio samples for the current column
        column_audio = audio[start_idx:end_idx]

        # Calculate the absolute maximum amplitude in the current column
        max_amplitude = np.max(np.abs(column_audio))

        # Calculate the number of ASCII art rows for the current column
        num_rows = int(max_amplitude * height)

        # Set the ASCII art representation for the current column
        if num_rows == 0:
            ascii_art[height // 2][i] = "|"
        else:
            row_start = (height - num_rows) // 2
            row_end = row_start + num_rows
            for j in range(row_start, row_end):
                ascii_art[j][i] = "|"

    # Convert the ASCII art representation to a string
    ascii_str = "\n".join(["".join(row) for row in ascii_art])

    return ascii_str


def play_audio(path):
    # Convert mp3 file to wav file for processing
    audio = AudioSegment.from_mp3(path)
    audio.export("output.wav", format="wav")

    # Play the audio
    wave_obj = sa.WaveObject.from_wave_file("output.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()


def main():
    abc = keyboard2abc.capture_midi_and_convert()
    prompt = gpt_describe.generate_prompt(abc)

    # Setup layout
    layout.split(
        Layout(name="upper", size=40),
        Layout(name="lower", size=10),
        Layout(name="credits", size=5),
    )
    layout["upper"].update(describe_music_panel)
    layout["lower"].update(generate_music_file_panel)
    layout["credits"].update(credits_panel)

    # Describe music in a thread
    with Live(
        layout,
        console=console,
        screen=True,
        auto_refresh=True,
        refresh_per_second=20,
    ) as live:
        # Setup fancy indeterminate progress bar
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green"),
            console=live.console,
            transient=True,
        )
        task = progress.add_task("[cyan]Generating Music...", total=None)
        layout["lower"].update(progress)

        describe_music_thread = threading.Thread(
            target=describe_music_section, args=(prompt, abc, live)
        )
        describe_music_thread.start()

        # Generate and play music in a different thread
        generate_and_play_music_thread = threading.Thread(
            target=generate_and_play_music_section,
            args=(prompt, abc, live, progress, task),
        )
        generate_and_play_music_thread.start()

        while (
            describe_music_thread.is_alive()
            or generate_and_play_music_thread.is_alive()
        ):
            live.update(layout)


import tempfile

import librosa
import numpy as np
import scipy.io.wavfile as wavfile
from art import text2art
from pydub import AudioSegment


def waveform_to_ascii(file_path, width=70, height=20):
    # Convert mp3 file to wav
    audio = AudioSegment.from_mp3(file_path)
    # Use a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_wav:
        temp_wav_name = temp_wav.name
        audio.export(temp_wav_name, format="wav")
        # Load wav file with librosa
        data, _ = librosa.load(temp_wav_name, sr=None, mono=True)

    # Downsample the data so it fits the width
    data = np.mean(data.reshape(-1, len(data) // width), axis=1)
    # Normalize to height and round
    data = np.round(
        (data - data.min()) / (data.max() - data.min()) * (height - 1)
    ).astype(int)
    # Create ASCII art
    ascii_art = ""
    for i in data:
        ascii_art += text2art(str(i), "block") + "\n"
    return ascii_art


if __name__ == "__main__":
    main()
