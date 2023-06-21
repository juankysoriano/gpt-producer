# GPT-Producer 🤖🎹🎵🎧

GPT-Producer is an experimental project that allows your MIDI device to communicate with GPT, generate music given a prompt, and even generates a creative review written by a simulated "Rolling Stones Magazine" reviewer.

**Disclaimer:** This is not a production ready code. It's a fun illustration of what can be achieved over a weekend! Moreover, the majority of the code and this README have been generated with ChatGPT.

## Installation

1. Install dependencies with:

   ```
   pip install -r requirements.txt
   ```

2. Make sure you have `ffmpeg` and `abc2midi` already installed. You can use the following commands to do so:

   ```
   sudo apt update
   sudo apt install ffmpeg
   sudo apt install abcmidi
   ```
3. **IMPORTANT**: Remember to bring your OpenAI API Key, update `gpt_describe.py` with your key. `//TODO using .env` 
4. Connect your MIDI device to your computer.

5. Run the program with:
   
   ```
   python main.py
   ```

## Process Flow

1. Record MIDI events from your MIDI device as you play.
2. Convert the information to ABC format, which is then passed to GPT.
3. **GPT creates a prompt for the MusicGen model.** This is an important step because it means that GPT can reason about the music you just played.
4. MusicGen to generate the music given the prompt and what you played, which is used for guidance.
5. Meanwhile, GPT generates a creative review as if it was written by "The Rolling Stones Magazine." Think of it as a very creative loading spinner.

## License

GPT-Producer is released under the [MIT License](https://opensource.org/licenses/MIT). See [LICENSE](LICENSE) for details.

## Contributions

PRs are welcome! Feel free to contribute and experiment with the GPT-Producer, an intriguing blend of AI-generated code and user input.

## Lazy Code and README Generation

Most of the code in GPT-Producer and this README have been generated with the help of ChatGPT. Get inspired by this fascinating synergy of AI and human interaction in the realm of software development!
