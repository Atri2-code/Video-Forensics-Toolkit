#!/usr/bin/env python3
"""
analyze.py — CLI entry point.
Usage: python src/analyze.py --input VIDEO_FILE [--output reports/]
"""
import argparse, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extractor import probe
from analyzer  import analyze
from reporter  import generate


def main():
    p = argparse.ArgumentParser(description='Forensic video analysis toolkit')
    p.add_argument('--input',  required=True, help='Path to video file')
    p.add_argument('--output', default='reports/', help='Output directory for report')
    p.add_argument('--quiet',  action='store_true')
    a = p.parse_args()

    print(f'\n[video-forensics-toolkit]')
    print(f'Analysing: {a.input}\n')

    meta   = probe(a.input)
    result = analyze(meta)
    report = generate(meta, result)

    os.makedirs(a.output, exist_ok=True)
    stem      = Path(a.input).stem
    out_path  = Path(a.output) / f'{stem}_forensic_report.md'
    out_path.write_text(report)

    if not a.quiet:
        high   = sum(1 for f in result.findings if f.severity == 'high')
        medium = sum(1 for f in result.findings if f.severity == 'medium')
        low    = sum(1 for f in result.findings if f.severity == 'low')
        print(f'  Integrity score : {result.integrity_score}/100')
        print(f'  Findings        : {high} high  {medium} medium  {low} low')
        print(f'  Summary         : {result.summary}')
        print(f'\n  Report saved → {out_path}\n')


if __name__ == '__main__':
    main()
