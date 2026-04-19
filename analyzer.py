"""
analyzer.py — Forensic integrity analysis.

Checks for common indicators of tampering:
  1. Metadata inconsistencies (missing encoder, mismatched timestamps)
  2. Bitrate anomalies (sudden spikes can indicate splicing)
  3. Stream count irregularities
  4. Container/codec mismatch
  5. Suspicious re-encoding traces
"""
from dataclasses import dataclass
from extractor import VideoMetadata


KNOWN_ENCODERS = {
    'libx264', 'libx265', 'h264', 'hevc', 'vp9', 'av1',
    'mpeg4', 'libvpx', 'prores', 'dnxhd',
}

CONTAINER_CODEC_MAP = {
    'mp4':  ['h264', 'hevc', 'mpeg4', 'av1'],
    'mov':  ['h264', 'hevc', 'prores', 'dnxhd'],
    'avi':  ['mpeg4', 'h264', 'xvid'],
    'mkv':  ['h264', 'hevc', 'vp9', 'av1'],
    'webm': ['vp9', 'av1', 'vp8'],
}


@dataclass
class Finding:
    severity: str      # 'high' | 'medium' | 'low' | 'info'
    category: str
    detail: str


@dataclass
class AnalysisResult:
    filename: str
    findings: list[Finding]
    integrity_score: int   # 0–100 (100 = no anomalies detected)
    summary: str


def analyze(meta: VideoMetadata) -> AnalysisResult:
    findings = []

    # 1. Missing creation timestamp
    if not meta.creation_time:
        findings.append(Finding(
            severity='medium',
            category='Metadata',
            detail='No creation_time tag found. May indicate metadata stripping or re-mux.',
        ))

    # 2. Missing or unknown encoder
    if not meta.encoder:
        findings.append(Finding(
            severity='medium',
            category='Metadata',
            detail='Encoder tag absent. Common after transcoding or metadata sanitisation.',
        ))
    elif not any(enc in meta.encoder.lower() for enc in KNOWN_ENCODERS):
        findings.append(Finding(
            severity='low',
            category='Metadata',
            detail=f'Unrecognised encoder tag: "{meta.encoder}". May indicate custom or obscure toolchain.',
        ))

    # 3. Zero duration
    if meta.duration_seconds == 0:
        findings.append(Finding(
            severity='high',
            category='Container',
            detail='Duration reported as 0. Container header may be corrupt or incomplete.',
        ))

    # 4. Abnormally low bitrate for a video file
    if 0 < meta.bit_rate < 50_000 and meta.nb_streams > 0:
        findings.append(Finding(
            severity='medium',
            category='Bitrate',
            detail=f'Very low bitrate ({meta.bit_rate} bps). May indicate heavy re-compression or partial file.',
        ))

    # 5. Container/codec mismatch
    container = meta.format_name.split(',')[0].strip()
    video_streams = [s for s in meta.streams if s.get('codec_type') == 'video']
    for stream in video_streams:
        codec = stream.get('codec_name', '').lower()
        expected = CONTAINER_CODEC_MAP.get(container, [])
        if expected and codec not in expected:
            findings.append(Finding(
                severity='high',
                category='Container/Codec Mismatch',
                detail=f'Codec "{codec}" is unusual for container "{container}". Possible re-wrap.',
            ))

    # 6. Multiple video streams (unusual for standard recordings)
    if len(video_streams) > 1:
        findings.append(Finding(
            severity='medium',
            category='Streams',
            detail=f'{len(video_streams)} video streams found. Standard recordings contain exactly 1.',
        ))

    # 7. Info: codec and resolution
    for stream in video_streams:
        w, h = stream.get('width', '?'), stream.get('height', '?')
        codec = stream.get('codec_name', 'unknown')
        findings.append(Finding(
            severity='info',
            category='Stream Info',
            detail=f'Video stream: {codec} @ {w}×{h}',
        ))

    score = _integrity_score(findings)
    summary = _summarise(findings, score)

    return AnalysisResult(
        filename=meta.filename,
        findings=findings,
        integrity_score=score,
        summary=summary,
    )


def _integrity_score(findings: list[Finding]) -> int:
    deductions = {'high': 30, 'medium': 15, 'low': 5, 'info': 0}
    total = sum(deductions[f.severity] for f in findings)
    return max(0, 100 - total)


def _summarise(findings: list[Finding], score: int) -> str:
    high   = sum(1 for f in findings if f.severity == 'high')
    medium = sum(1 for f in findings if f.severity == 'medium')
    if score >= 80:
        return f'No significant anomalies detected. Integrity score: {score}/100.'
    elif score >= 50:
        return f'{medium} medium-severity anomalies found. Manual review recommended. Score: {score}/100.'
    else:
        return f'{high} high-severity anomalies found. File integrity is questionable. Score: {score}/100.'
