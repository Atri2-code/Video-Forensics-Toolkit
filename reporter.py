"""
reporter.py — Forensic report generator.
Produces structured Markdown reports suitable for case documentation.
"""
from datetime import datetime, timezone
from extractor import VideoMetadata
from analyzer  import AnalysisResult

SEVERITY_LABEL = {'high': '🔴 HIGH', 'medium': '🟡 MEDIUM', 'low': '🔵 LOW', 'info': 'ℹ INFO'}


def generate(meta: VideoMetadata, result: AnalysisResult) -> str:
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    lines = [
        '# Forensic Video Analysis Report',
        f'*Generated: {now}*',
        '',
        '---',
        '',
        '## File Information',
        '',
        f'| Field | Value |',
        f'|-------|-------|',
        f'| Filename | `{meta.filename}` |',
        f'| Format | {meta.format_long_name} |',
        f'| Duration | {_fmt_duration(meta.duration_seconds)} |',
        f'| File size | {_fmt_size(meta.size_bytes)} |',
        f'| Bit rate | {meta.bit_rate:,} bps |',
        f'| Streams | {meta.nb_streams} |',
        f'| Creation time | {meta.creation_time or "Not present"} |',
        f'| Encoder | {meta.encoder or "Not present"} |',
        '',
        '---',
        '',
        '## Integrity Assessment',
        '',
        f'**Integrity Score: {result.integrity_score}/100**',
        '',
        f'> {result.summary}',
        '',
        '---',
        '',
        '## Findings',
        '',
    ]

    for finding in result.findings:
        lines += [
            f'### {SEVERITY_LABEL[finding.severity]} — {finding.category}',
            '',
            finding.detail,
            '',
        ]

    lines += [
        '---',
        '',
        '## Disclaimer',
        '',
        '_This report is generated automatically and should be reviewed by a qualified forensic analyst._',
        '_Findings indicate anomalies worthy of investigation, not definitive proof of tampering._',
    ]

    return '\n'.join(lines)


def _fmt_duration(seconds: float) -> str:
    if seconds == 0:
        return 'Unknown'
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f'{h:02d}:{m:02d}:{s:02d}'


def _fmt_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f'{size:.1f} {unit}'
        size /= 1024
    return f'{size:.1f} TB'
