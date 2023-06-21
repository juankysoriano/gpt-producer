import subprocess
import time

import mido
from rich.console import Console
from rich.table import Table

console = Console()


def capture_midi_and_convert():
    # List available MIDI input ports
    input_ports = mido.get_input_names()

    # Display input ports with numeric options
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("No.", style="dim", width=4)
    table.add_column("MIDI Input Port")
    for i, port_name in enumerate(input_ports):
        table.add_row(f"{i + 1}", port_name)

    console.print("Available MIDI input ports:", table)

    # Prompt user to select a MIDI input port by number
    selected_port = console.input(
        "[cyan]Enter the number of the MIDI input port you want to use:[/cyan] "
    )

    # Check if selection is valid
    try:
        selected_port = int(selected_port) - 1
        if 0 <= selected_port < len(input_ports):
            port_name = input_ports[selected_port]
        else:
            console.print("[red]Invalid selection[/red]")
            return None
    except ValueError:
        console.print("[red]Invalid selection[/red]")
        return None

    # Open the MIDI input port
    with mido.open_input(port_name) as inport:
        # Create a new MIDI file with one track and 480 ticks per beat
        mid = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        mid.tracks.append(track)

        # Set initial time
        start_time = time.time()

        # Set the tempo (in microseconds per beat), 950000 for a slower tempo
        track.append(mido.MetaMessage("set_tempo", tempo=950000, time=0))

        # Capture MIDI messages until 5 seconds of inactivity
        console.print(
            "[magenta]Capturing MIDI messages... (Will stop after 5 seconds of inactivity)[/magenta]"
        )
        prev_time = 0
        last_msg_time = time.time()
        while time.time() - last_msg_time < 5:
            messages_received = False
            for msg in inport.iter_pending():
                messages_received = True
                # Add relative timestamp to messages (in ticks)
                elapsed_time = time.time() - start_time
                relative_ticks = int(
                    (elapsed_time - prev_time) * mid.ticks_per_beat
                )
                msg.time = relative_ticks
                prev_time = elapsed_time
                track.append(msg)

            # Update the last message time if messages were received
            if messages_received:
                last_msg_time = time.time()

    # Save the captured MIDI messages to a file
    mid.save("output.mid")

    # Convert the MIDI file to ABC notation
    try:
        # Run midi2abc and save the output to a file
        subprocess.run(["midi2abc", "output.mid", "-o", "temp.abc"])

        # Use grep to filter out the lines with '%' and save the final output to 'output.abc'
        with open("output.abc", "w") as output_file:
            subprocess.run(["grep", "-v", "^%", "temp.abc"], stdout=output_file)

    except Exception as e:
        console.print(f"[red]Error converting MIDI to ABC notation: {e}[/red]")
        return None

    # Optionally, you can delete the temp.abc file after you're done
    subprocess.run(["rm", "temp.abc"])

    # Read the content of the ABC file and return it
    with open("output.abc", "r") as abc_file:
        abc_content = abc_file.read()

    return abc_content
