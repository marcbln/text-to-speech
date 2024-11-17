import os
from typing import Literal, Optional
from pathlib import Path
from enum import Enum
import requests
from gtts import gTTS
from openai import OpenAI
import typer
from typing_extensions import Annotated
import platform


class Provider(str, Enum):
    GOOGLE = "google"
    OPENAI = "openai"


class Voice(str, Enum):
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"


class TextToSpeech:
    def __init__(self, output_dir: str = "audio_output"):
        """Initialize TTS with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_google(self, text: str, lang: str = 'en',
                        output_filename: str = "output.mp3") -> str:
        """Generate speech using Google TTS."""
        output_path = self.output_dir / output_filename
        tts = gTTS(text=text, lang=lang)
        tts.save(str(output_path))
        return str(output_path)

    def generate_openai(self, text: str,
                        voice: Voice = Voice.NOVA,
                        model: str = "tts-1",
                        output_filename: str = "output.mp3") -> str:
        """Generate speech using OpenAI's TTS service."""
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        client = OpenAI()
        output_path = self.output_dir / output_filename

        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )

        response.stream_to_file(str(output_path))
        return str(output_path)


def play_audio(file_path: str):
    """Play the audio file using the system's default audio player."""
    try:
        if platform.system() == 'Darwin':  # macOS
            os.system(f'afplay "{file_path}"')
        elif platform.system() == 'Linux':  # Linux
            os.system(f'xdg-open "{file_path}"')
        elif platform.system() == 'Windows':  # Windows
            os.system(f'start "" "{file_path}"')
        else:
            typer.secho("Unsupported platform for audio playback", fg=typer.colors.YELLOW)
    except Exception as e:
        typer.secho(f"Error playing audio: {str(e)}", fg=typer.colors.RED)


app = typer.Typer()


@app.command()
def speak(
        text: Annotated[str, typer.Argument(help="Text to convert to speech")],
        provider: Annotated[Provider, typer.Option(help="TTS provider to use")] = Provider.GOOGLE,
        output: Annotated[Optional[str], typer.Option(help="Output filename")] = None,
        voice: Annotated[Voice, typer.Option(help="Voice to use (OpenAI only)")] = Voice.NOVA,
        lang: Annotated[str, typer.Option(help="Language code (Google only)")] = "en",
        play: Annotated[bool, typer.Option(help="Play the audio after generation")] = True
) -> None:
    """
    Convert text to speech using either Google TTS (free) or OpenAI TTS (requires API key).
    """
    tts = TextToSpeech()

    if output is None:
        output = f"output_{provider.value}.mp3"

    try:
        if provider == Provider.GOOGLE:
            output_path = tts.generate_google(text, lang=lang, output_filename=output)
            typer.echo(f"Generated audio using Google TTS: {output_path}")
        else:  # OpenAI
            output_path = tts.generate_openai(text, voice=voice, output_filename=output)
            typer.echo(f"Generated audio using OpenAI TTS: {output_path}")

        if play:
            typer.echo("Playing audio...")
            play_audio(output_path)

    except Exception as e:
        typer.secho(f"Error: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()