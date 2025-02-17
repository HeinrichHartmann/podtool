#!/usr/bin/env python3

import click
import subprocess
import os
from pathlib import Path
from podtool.transcript import Transcript

VERSION = "1.0.0"

@click.group()
def cli():
    """Podtool - Audio processing and transcript refinement utility"""
    pass

@cli.command()
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

@cli.command()
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

@cli.command()
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

if __name__ == '__main__':
    cli()