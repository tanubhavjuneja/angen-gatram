# Docker-based TSK (The Sleuth Kit)

This directory contains Docker configuration for running The Sleuth Kit tools for forensic analysis of disk images.

## Setup

1. Build and start the container:
```bash
cd docker/tsk
docker-compose up -d
```

2. Copy your disk image to the images folder:
```bash
cp /path/to/image.E01 docker/tsk/images/
```

3. Run TSK commands:
```bash
docker exec tsk-forensics mmls -i ewf /forensics/images/image.E01
docker exec tsk-forensics fls -i ewf -o 63 /forensics/images/image.E01
```

## Available Tools

- mmls - Partition layout
- fls - File listing
- icat - File content extraction
- mmcat - Partition content extraction
- istat - File/Directory statistics
- blkls - Data unit listing

## Usage from Python

```python
from imageProcessor.agents.tsk_docker import analyze_timestamp_integrity_docker

result = analyze_timestamp_integrity_docker("image.E01")
print(result)
```
