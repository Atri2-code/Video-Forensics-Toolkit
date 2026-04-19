# video-forensics-toolkit (Digital Forensics)

> Forensic integrity analysis for video files — metadata extraction, tampering detection, and structured case reporting.

Analyses video files for common indicators of manipulation: metadata stripping, container/codec mismatches, bitrate anomalies, and re-encoding traces. Produces a structured Markdown report suitable for forensic case documentation.

---

## Quick start

```bash
git clone https://github.com/YOUR_USERNAME/video-forensics-toolkit.git
cd video-forensics-toolkit

# Install ffmpeg for full metadata extraction (recommended)
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg

python src/analyze.py --input evidence.mp4 --output reports/
```

No Python dependencies beyond the standard library. ffprobe (bundled with ffmpeg) is used when available and gracefully falls back otherwise.

---

## What it detects

| Indicator | Severity | Description |
|-----------|----------|-------------|
| Missing creation timestamp | Medium | Common after metadata stripping or re-mux |
| Absent or unknown encoder tag | Medium | Typical after transcoding |
| Zero or corrupt duration | High | Container header damage or incomplete file |
| Abnormally low bitrate | Medium | Heavy re-compression or partial file |
| Container/codec mismatch | High | e.g. VP9 inside an MP4 wrapper — indicates re-wrap |
| Multiple video streams | Medium | Non-standard; warrants investigation |

---

## Sample report output

```markdown
# Forensic Video Analysis Report
*Generated: 2025-03-12 14:22:01 UTC*

## File Information
| Field        | Value                    |
|--------------|--------------------------|
| Filename     | evidence_clip.mp4        |
| Duration     | 00:04:32                 |
| File size    | 87.3 MB                  |
| Encoder      | Not present              |

## Integrity Assessment
**Integrity Score: 55/100**
> 2 medium-severity anomalies found. Manual review recommended.

### 🟡 MEDIUM — Metadata
No creation_time tag found. May indicate metadata stripping or re-mux.

### 🔴 HIGH — Container/Codec Mismatch
Codec "vp9" is unusual for container "mp4". Possible re-wrap.
```

---

## Project structure

```
video-forensics-toolkit/
├── src/
│   ├── analyze.py      # CLI entry point
│   ├── extractor.py    # Video metadata extraction (ffprobe + fallback)
│   ├── analyzer.py     # Forensic integrity analysis logic
│   └── reporter.py     # Markdown report generator
├── tests/
│   └── test_analyzer.py
├── reports/            # Generated reports (gitignored)
└── README.md
```

---

## Running tests

```bash
python tests/test_analyzer.py
```

---

## Skills demonstrated

| Engineering competency | Implementation |
|---|---|
| Media processing | ffprobe integration, container/codec parsing |
| Digital forensics | Tampering indicator detection, integrity scoring |
| Python | Dataclasses, subprocess, CLI, zero external deps |
| Test automation | Unit tests covering all severity tiers |
| Documentation | Structured case-ready Markdown reports |

---

## Roadmap

- [ ] Frame-level hash verification (detect frame insertion/deletion)
- [ ] Audio/video sync drift detection
- [ ] Batch analysis across evidence folders
- [ ] JSON output for integration with case management systems
- [ ] Azure Blob Storage input support

---

## Disclaimer

Reports are generated automatically and should be reviewed by a qualified forensic analyst. Findings indicate anomalies worthy of investigation, not definitive proof of tampering.

---

## License

MIT
