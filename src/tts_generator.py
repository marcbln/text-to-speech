import os
from typing import Literal, Optional
from pathlib import Path
from enum import Enum
import requests
from slugify import slugify
from gtts import gTTS
from openai import OpenAI
import typer
from typing_extensions import Annotated


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

    def _get_filename(self, text: str, suffix: str = "") -> str:
        """Generate a slugified filename from the text."""
        # Take first 50 chars of text to avoid too long filenames
        slugified = slugify(text[:50], max_length=50)
        if suffix:
            return f"{slugified}_{suffix}.mp3"
        return f"{slugified}.mp3"

    def generate_google(self, text: str, lang: str = 'en',
                        output_filename: Optional[str] = None) -> str:
        """Generate speech using Google TTS."""
        if output_filename is None:
            output_filename = self._get_filename(text, f"google_{lang}")
        output_path = self.output_dir / output_filename
        output_path = self.output_dir / output_filename
        tts = gTTS(text=text, lang=lang)
        tts.save(str(output_path))
        return str(output_path)

    def generate_openai(self, text: str,
                        voice: Voice = Voice.NOVA,
                        model: str = "tts-1",
                        output_filename: Optional[str] = None) -> str:
        """Generate speech using OpenAI's TTS service."""
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        if output_filename is None:
            output_filename = self._get_filename(text, f"openai_{voice}")
        output_path = self.output_dir / output_filename

        client = OpenAI()
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )

        response.stream_to_file(str(output_path))
        return str(output_path)



app = typer.Typer()


@app.command()
def speak(
        text: Annotated[str, typer.Argument(help="Text to convert to speech")],
        provider: Annotated[Provider, typer.Option(help="TTS provider to use")] = Provider.GOOGLE,
        output: Annotated[Optional[str], typer.Option(help="Output filename")] = None,
        voice: Annotated[Voice, typer.Option(help="Voice to use (OpenAI only)")] = Voice.NOVA,
        lang: Annotated[str, typer.Option(help="Language code (Google only)")] = "en"
) -> None:
    """
    Convert text to speech using either Google TTS (free) or OpenAI TTS (requires API key).
    """
    tts = TextToSpeech()

    # output filename will be auto-generated if None

    try:
        if provider == Provider.GOOGLE:
            output_path = tts.generate_google(text, lang=lang, output_filename=output)
            print(output_path)
        else:  # OpenAI
            output_path = tts.generate_openai(text, voice=voice, output_filename=output)
            print(output_path)

    except Exception as e:
        typer.secho(f"Error: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
