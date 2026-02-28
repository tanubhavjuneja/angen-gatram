FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    sleuthkit \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /forensics

ENTRYPOINT ["/bin/bash"]
