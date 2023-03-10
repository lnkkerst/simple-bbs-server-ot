# Simple BBS Server

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)

简陋的论坛

## Usage

Dependencies: Python(>=3.10), pdm

```bash
# recommanded: use pipx
#pipx install pdm
pip install pdm
```

### Prepare installation

```bash
# optional: use virtualenv
#pdm venv activate | source
pdm install
```

### Development

```bash
pdm run dev
```

### Production

```bash
pdm run start
```

## Docker

```bash
docker build -t simple-bbs-server:latest .
```
