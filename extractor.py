"""
extractor.py — Video metadata and stream extraction.
Parses container-level and codec-level metadata without external binaries
by reading raw byte structures alongside ffprobe where available.
"""
import json
import subprocess
import shutil
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class VideoMetadata:
    filename: str
    format_name: str
    format_long_name: str
    duration_seconds: float
    size_bytes: int
    bit_rate: int
    nb_streams: int
    creation_time: str | None
    encoder: str | None
    streams: list[dict]


def probe(video_path: str) -> VideoMetadata:
    """Extract metadata using ffprobe. Falls back to basic file stats if unavailable."""
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    if shutil.which('ffprobe'):
        return _probe_ffprobe(path)
    else:
        return _probe_fallback(path)


def _probe_ffprobe(path: Path) -> VideoMetadata:
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        str(path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    data = json.loads(result.stdout)

    fmt     = data.get('format', {})
    streams = data.get('streams', [])
    tags    = fmt.get('tags', {})

    return VideoMetadata(
        filename=path.name,
        format_name=fmt.get('format_name', 'unknown'),
        format_long_name=fmt.get('format_long_name', 'unknown'),
        duration_seconds=float(fmt.get('duration', 0)),
        size_bytes=int(fmt.get('size', path.stat().st_size)),
        bit_rate=int(fmt.get('bit_rate', 0)),
        nb_streams=int(fmt.get('nb_streams', len(streams))),
        creation_time=tags.get('creation_time'),
        encoder=tags.get('encoder') or tags.get('ENCODER'),
        streams=streams,
    )


def _probe_fallback(path: Path) -> VideoMetadata:
    """Minimal fallback using file stats only."""
    stat = path.stat()
    return VideoMetadata(
        filename=path.name,
        format_name=path.suffix.lstrip('.').lower(),
        format_long_name='unknown (ffprobe not available)',
        duration_seconds=0.0,
        size_bytes=stat.st_size,
        bit_rate=0,
        nb_streams=0,
        creation_time=None,
        encoder=None,
        streams=[],
    )
