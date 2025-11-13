# FlareSolverr Setup

The scraper requires FlareSolverr to bypass Cloudflare protection on Korean novel websites.

## Configuration

FlareSolverr URL is configured via environment variable:

1. **Copy `.env.example` to `.env`** (if you haven't already):
   ```bash
   cp .env.example .env
   ```

2. **Set the FlareSolverr URL** in your `.env` file:
   ```bash
   # For local development
   FLARESOLVERR_URL=http://localhost:8191/v1
   
   # For Docker Compose (when both services are in the same network)
   FLARESOLVERR_URL=http://flaresolverr:8191/v1
   
   # For remote FlareSolverr instance
   FLARESOLVERR_URL=http://your-server:8191/v1
   ```

Default: `http://localhost:8191/v1` (if not specified)

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

### "Cannot connect to FlareSolverr" error
1. **Check if FlareSolverr is running**:
   ```bash
   docker ps | grep flaresolverr
   ```

2. **If not running, start it**:
   ```bash
   docker start flaresolverr
   # Or create new container if it doesn't exist
   docker run -d --name=flaresolverr -p 8191:8191 ghcr.io/flaresolverr/flaresolverr:latest
   ```

3. **Verify the URL in your `.env` file matches the running instance**

### FlareSolverr not responding
```bash
docker restart flaresolverr
```

### Port 8191 already in use
Change the port mapping:
```bash
docker run -d --name=flaresolverr -p 8192:8191 ghcr.io/flaresolverr/flaresolverr:latest
```
Then update `FLARESOLVERR_URL` in your `.env` file:
```bash
FLARESOLVERR_URL=http://localhost:8192/v1
```

### Docker not running
```bash
open -a Docker  # macOS
```

## Production Deployment

### Docker Compose

Add FlareSolverr to your `docker-compose.yml`:

```yaml
services:
  flaresolverr:
    image: ghcr.io/flaresolverr/flaresolverr:latest
    container_name: flaresolverr
    ports:
      - "8191:8191"
    restart: unless-stopped
  
  django:
    # Your Django service configuration
    environment:
      - FLARESOLVERR_URL=http://flaresolverr:8191/v1
    depends_on:
      - flaresolverr
```

**Note**: When services are in the same Docker network, use the service name (`flaresolverr`) as the hostname instead of `localhost`.

### Environment Variables

Make sure your production environment has `FLARESOLVERR_URL` configured:

```bash
# Example for production
export FLARESOLVERR_URL=http://flaresolverr:8191/v1
```
