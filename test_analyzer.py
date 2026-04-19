"""
test_analyzer.py — Unit tests for forensic analysis logic.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from extractor import VideoMetadata
from analyzer  import analyze, Finding


def make_meta(**overrides):
    defaults = dict(
        filename='test.mp4',
        format_name='mp4',
        format_long_name='QuickTime / MOV',
        duration_seconds=120.0,
        size_bytes=15_000_000,
        bit_rate=1_000_000,
        nb_streams=2,
        creation_time='2024-01-15T10:30:00Z',
        encoder='libx264',
        streams=[{'codec_type': 'video', 'codec_name': 'h264', 'width': 1920, 'height': 1080}],
    )
    return VideoMetadata(**{**defaults, **overrides})


def test_clean_file_scores_high():
    result = analyze(make_meta())
    assert result.integrity_score >= 80, f"Expected >= 80, got {result.integrity_score}"
    print(f"  PASS  clean file scores {result.integrity_score}/100")


def test_missing_creation_time_flagged():
    result = analyze(make_meta(creation_time=None))
    categories = [f.category for f in result.findings]
    assert 'Metadata' in categories
    print(f"  PASS  missing creation_time flagged")


def test_missing_encoder_flagged():
    result = analyze(make_meta(encoder=None))
    assert any(f.category == 'Metadata' and 'Encoder' in f.detail for f in result.findings)
    print(f"  PASS  missing encoder flagged")


def test_zero_duration_high_severity():
    result = analyze(make_meta(duration_seconds=0))
    high_findings = [f for f in result.findings if f.severity == 'high']
    assert len(high_findings) > 0
    print(f"  PASS  zero duration flagged as high severity")


def test_codec_mismatch_flagged():
    streams = [{'codec_type': 'video', 'codec_name': 'vp9', 'width': 1280, 'height': 720}]
    result = analyze(make_meta(format_name='mp4', streams=streams))
    assert any(f.category == 'Container/Codec Mismatch' for f in result.findings)
    print(f"  PASS  codec mismatch (vp9 in mp4) flagged")


if __name__ == '__main__':
    print('\nRunning tests...\n')
    test_clean_file_scores_high()
    test_missing_creation_time_flagged()
    test_missing_encoder_flagged()
    test_zero_duration_high_severity()
    test_codec_mismatch_flagged()
    print('\nAll tests passed.\n')
