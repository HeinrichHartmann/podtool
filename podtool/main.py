#!/usr/bin/env python3
import click
import subprocess
import os
import logging
from pathlib import Path
from .transcript import Transcript
from .transcribe import Speech2Text

def setup_logging(verbosity):
    """Configure logging based on verbosity level"""
    log_levels = {
        0: logging.WARNING,  # Default
        1: logging.INFO,     # -v
        2: logging.DEBUG,    # -vv
    }
    level = log_levels.get(verbosity, logging.DEBUG)
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s' if level > logging.DEBUG else '%(levelname)s: [%(filename)s:%(lineno)d] %(message)s'
    )

@click.group()
@click.option('-v', '--verbose', count=True, help='Increase verbosity (use -v, -vv, or -vvv for more detailed output)')
def cli(verbose):
    """Podtool - Audio processing and transcript refinement utility"""
    setup_logging(verbose)
    logging.debug(f"Verbosity level set to {verbose}")
    pass

@cli.group()
def audio():
    """Audio processing commands"""
    pass

@audio.command()
@click.option('-o', '--output', default='mix.wav', help='Output file name')
@click.argument('input_files', nargs=-1, required=True, type=click.Path(exists=True))
def mix(output, input_files):
    """Mix provided audio files into a joined audio file"""
    click.echo(f"Mixing audio files into {output}...")
    
    try:
        cmd = ['sox', '-m', *input_files, output]
        subprocess.run(cmd, check=True)
        click.echo(f"Audio files mixed successfully into {output}.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error mixing audio files: {e}", err=True)
        raise click.Abort()

@audio.command()
@click.option('-o', '--output', default='mix.mp3', help='Output file name')
@click.argument('input_file', type=click.Path(exists=True))
def recode(output, input_file):
    """Convert provided audio file to MP3 format with high quality settings"""
    click.echo(f"Converting {input_file} to MP3 format with high quality settings into {output}...")
    
    try:
        cmd = [
            'ffmpeg', '-y',
            '-i', str(input_file),
            '-codec:a', 'libmp3lame',
            '-qscale:a', '0',
            output
        ]
        subprocess.run(cmd, check=True)
        click.echo(f"Conversion complete. Output file: {output}")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error converting audio file: {e}", err=True)
        raise click.Abort()

@audio.command()
@click.argument('input_file', type=click.Path(exists=True))
def edit(input_file):
    """Open audio file in Audacity for editing"""
    click.echo(f"Opening {input_file} in Audacity...")
    
    try:
        cmd = ['audacity', str(input_file)]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error launching Audacity: {e}", err=True)
        raise click.Abort()

@audio.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-l', '--length', default='1:00:00', help='Length of each segment in HH:MM:SS format (default: 1 hour)')
@click.option('-o', '--output-pattern', default=None, help='Output filename pattern (default: input_001.ext)')
def split(input_file, length, output_pattern):
    """Split audio file into segments of equal length"""
    input_path = Path(input_file)
    
    if output_pattern is None:
        # Create default pattern: input_001.ext
        output_pattern = f"{input_path.stem}_%03d{input_path.suffix}"
    
    click.echo(f"Splitting {input_file} into segments of {length}...")
    
    try:
        cmd = [
            'ffmpeg', '-y',
            '-i', str(input_file),
            '-f', 'segment',
            '-segment_time', length,
            '-c', 'copy',  # Copy without re-encoding
            '-reset_timestamps', '1',
            output_pattern
        ]
        subprocess.run(cmd, check=True)
        click.echo(f"Audio file split successfully using pattern: {output_pattern}")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error splitting audio file: {e}", err=True)
        raise click.Abort()

@audio.command()
@click.argument('input_file', type=click.Path(exists=True))
def transcribe(input_file):
    """Generate a transcript from an audio file"""
    click.echo(f"Transcribing {input_file}...")
    try:
        transcriber = Speech2Text(credentials_path=os.getenv('GOOGLE_SERVICE_CREDENTIALS'))
        text = transcriber.process(input_file)
        output_file = str(Path(input_file).with_suffix('.txt'))
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        click.echo(f"Transcription complete. Output saved to {output_file}")
    except Exception as e:
        click.echo(f"Error during transcription: {e}", err=True)
        raise click.Abort()

@cli.group()
def transcript():
    """Transcript management commands"""
    pass

@transcript.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', default=None, help='Output file name (defaults to input_file with _refined suffix)')
def refine(input_file, output):
    """Refine a transcript file by cleaning up formatting and common issues"""
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        click.echo("Error: OPENAI_API_KEY environment variable not set", err=True)
        raise click.Abort()
    
    input_path = Path(input_file)
    if output is None:
        output = str(input_path.with_stem(input_path.stem + '_refined'))
    
    click.echo(f"Refining transcript {input_file} to {output}...")
    
    try:
        transcript = Transcript(api_key)
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        refined_content = transcript.refine(content)
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(refined_content)
            
        click.echo(f"Transcript refined successfully. Output saved to {output}")
    except Exception as e:
        click.echo(f"Error refining transcript: {e}", err=True)
        raise click.Abort()
    
@transcript.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', default=None, help='Output file name (defaults to input_file with _summary suffix)')
def summarize(input_file, output):
    """Summarize a transcript file"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        click.echo("Error: OPENAI_API_KEY environment variable not set", err=True)
        raise click.Abort()
    
    input_path = Path(input_file)
    if output is None:
        output = str(input_path.with_stem(input_path.stem + '_summary'))
    
    click.echo(f"Summarizing transcript {input_file} to {output}...")
    
    try:
        transcript = Transcript(api_key)
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        summary = transcript.summarize(content)
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        click.echo(f"Transcript summarized successfully. Output saved to {output}")
    except Exception as e:
        click.echo(f"Error summarizing transcript: {e}", err=True)
        raise click.Abort()

@transcript.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', default=None, help='Output file name (defaults to input_file with _critique suffix)')
def critique(input_file, output):
    """Analyze the podcast transcript and provide detailed feedback for improvement"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        click.echo("Error: OPENAI_API_KEY environment variable not set", err=True)
        raise click.Abort()
    
    input_path = Path(input_file)
    if output is None:
        output = str(input_path.with_stem(input_path.stem + '_critique'))
    
    click.echo(f"Analyzing podcast transcript {input_file} and generating critique to {output}...")
    
    try:
        transcript = Transcript(api_key)
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        critique = transcript.critique(content)
        
        with open(output, 'w', encoding='utf-8') as f:
            f.write(critique)
            
        click.echo(f"Podcast critique generated successfully. Output saved to {output}")
    except Exception as e:
        click.echo(f"Error generating podcast critique: {e}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    cli()