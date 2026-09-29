FROM python:3.13-slim-bookworm
ARG TARGETARCH
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl zstd gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*
RUN case "$TARGETARCH" in amd64) platform=linux;; arm64) platform=linux_aarch64;; *) exit 1;; esac \
    && curl -fL "https://github.com/leanprover/lean4/releases/download/v4.34.0/lean-4.34.0-$platform.tar.zst" -o /tmp/lean.tar.zst \
    && mkdir /opt/lean && tar --zstd -xf /tmp/lean.tar.zst --strip-components=1 -C /opt/lean \
    && rm /tmp/lean.tar.zst
ENV PATH="/opt/lean/bin:${PATH}"
