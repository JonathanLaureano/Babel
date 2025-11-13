# FlareSolverr Setup

The scraper requires FlareSolverr to bypass Cloudflare protection on Korean novel websites.

## Quick Start

1. **Start FlareSolverr (if not already running)**:
   ```bash
   docker run -d --name=flaresolverr -p 8191:8191 ghcr.io/flaresolverr/flaresolverr:latest
   ```

2. **Verify it's running**:
   ```bash
   docker ps
   curl http://localhost:8191/
   ```

## Management Commands

### Check if FlareSolverr is running:
```bash
docker ps | grep flaresolverr
```

### Stop FlareSolverr:
```bash
docker stop flaresolverr
```

### Start FlareSolverr (if already created):
```bash
docker start flaresolverr
```

### Remove FlareSolverr container:
```bash
docker rm -f flaresolverr
```

### View FlareSolverr logs:
```bash
docker logs flaresolverr
```

## How It Works

- FlareSolverr runs a headless Chrome browser that can bypass Cloudflare challenges
- The scraper (`translator/scraper.py`) sends requests to FlareSolverr via HTTP API
- FlareSolverr returns the fully rendered HTML after passing Cloudflare protection
- Sessions are maintained across requests for efficiency

## Troubleshooting

### FlareSolverr not responding
```bash
docker restart flaresolverr
```

### Port 8191 already in use
Change the port mapping:
```bash
docker run -d --name=flaresolverr -p 8192:8191 ghcr.io/flaresolverr/flaresolverr:latest
```
Then update `FLARESOLVERR_URL` in `translator/scraper.py` to `http://localhost:8192/v1`

### Docker not running
```bash
open -a Docker  # macOS
```

## Production Deployment

For production, add FlareSolverr to your docker-compose.yml:

```yaml
services:
  flaresolverr:
    image: ghcr.io/flaresolverr/flaresolverr:latest
    container_name: flaresolverr
    ports:
      - "8191:8191"
    restart: unless-stopped
```
