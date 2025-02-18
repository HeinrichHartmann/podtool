# Podtool

Toolkit for editing podcasts.

# Installation

This is a simple python project, that can be run and installed locally.

```
# from git tree directory
python -m podtool
```

We are using nix and deliberately include compelex dependencies which the author finds handy (e.g. sox, audacity, ffmpeg).
```
nix run github:HeinrichHartmann/podtool
```

To install use:
```
nix profile install github:HeinrichHartmann/podtool
```

# Usage

```
❯ podtool
Usage: podtool [OPTIONS] COMMAND [ARGS]...

  Podtool - Audio processing and transcript refinement utility

Options:
  --help  Show this message and exit.

Commands:
  edit        Open audio file in Audacity for editing
  mix         Mix provided audio files into a joined audio file
  recode      Convert provided audio file to MP3 format with high quality...
  transcript  Transcript management commands

❯ podtool transcript
Usage: python -m podtool transcript [OPTIONS] COMMAND [ARGS]...

  Transcript management commands

Options:
  --help  Show this message and exit.

Commands:
  critique   Analyze the podcast transcript and provide detailed feedback...
  refine     Refine a transcript file by cleaning up formatting and...
  summarize  Summarize a transcript file

```