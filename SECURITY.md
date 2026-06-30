# Security Policy

## Supported versions

BioKit 2.0 is currently in active development. Security fixes are applied to
the latest `main` branch only.

## Reporting a vulnerability

Please report security vulnerabilities **privately** by emailing the
maintainers. Do **not** open a public GitHub issue for security problems.

## What to include

- A description of the vulnerability and its impact
- Steps to reproduce (PoC if possible)
- Affected versions
- Suggested fix (optional)

We will acknowledge receipt within 48 hours and aim to publish a fix within
14 days for high-severity issues.

## Scope

BioKit processes untrusted biological data (FASTA/FASTQ/GFF3/PDB/etc.). The
following are explicitly **out of scope**:

- Denial-of-service attacks via extremely large input files (we recommend
  streaming I/O for >1 GB files)
- XML parsing of untrusted BLAST output — we use Python's `xml.etree.ElementTree`
  which is vulnerable to XXE. If you parse untrusted BLAST output, install
  `defusedxml` and patch `biokit.blast.parser.parse_blast_xml` to use it.
