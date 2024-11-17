# Simple Text-to-Speech Generator

A simple Python script for generating speech from text using multiple providers (Google TTS and OpenAI TTS).

## About

Built to generate audio files which are played at the end of long-running scripts, as a replacement for the `espeak` command.

## Features

- Generate speech using Google Text-to-Speech (free)
- Generate speech using OpenAI's TTS service (requires API key)
- Command-line interface with Typer
- Save audio files in MP3 format
- Multiple voice options (when using OpenAI)

## Installation

```bash
uv venv
source venv/bin/activate
uv install -e .
```

## Dependencies

The project requires Python 3.8 or higher and the following packages:
- gtts
- openai
- requests
- typer

## Command Line Usage

After installation, you can use the `tts` command:

```bash
# Basic usage with Google TTS (free)
tts 'Hello, World!'

# Using OpenAI TTS with specific voice
tts 'Hello, World!' --provider openai --voice nova

# Save to specific file without playing
tts 'Hello, World!' --output my_speech.mp3 

# Save and play
paplay $(tts "Hello TTS")

# Show help
tts --help
```

Available options:
- `--provider [google|openai]`: Choose TTS provider (default: google)
- `--output FILENAME`: Specify output filename
- `--voice [alloy|echo|fable|onyx|nova|shimmer]`: Choose OpenAI voice
- `--lang LANG`: Language code for Google TTS (default: en)

## Python API Usage

You can also use the library programmatically:

```python
from tts_generator import TextToSpeech

tts = TextToSpeech()

# Using Google TTS (free)
output_path = tts.generate_google('Hello, World!')

# Using OpenAI TTS (requires API key)
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"
output_path = tts.generate_openai('Hello, World!', voice="nova")
```


## Configuration

For OpenAI TTS, set your API key as an environment variable:
```bash
export OPENAI_API_KEY='your-api-key'
```

## License

MIT