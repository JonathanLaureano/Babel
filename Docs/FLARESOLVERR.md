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

### Security Considerations

**CRITICAL SECURITY WARNING**: FlareSolverr is a powerful service that can be exploited if not properly secured. Implement ALL recommended protections before deploying to production.

#### ⚠️ DO NOT Expose Port 8191 Publicly

**NEVER expose FlareSolverr's port 8191 to the public internet**. This service:
- Has no built-in authentication
- Can be used as an open proxy for bypassing Cloudflare
- Could enable SSRF attacks against your internal infrastructure
- May be abused for resource exhaustion attacks

**Recommended deployment**:
- ✅ Keep FlareSolverr in a private Docker network (see Network Isolation below)
- ✅ Only allow access from your Django application
- ✅ Do NOT port forward 8191 on your firewall/router
- ✅ Use internal Docker networking instead of exposing ports to host
- ❌ NEVER use `-p 8191:8191` in production (only for local development)

#### 🔒 SSRF Protection (REQUIRED for Production)

FlareSolverr can be exploited for SSRF (Server-Side Request Forgery) attacks if not properly secured. Implement the following protections:

#### 1. Domain Whitelist (REQUIRED for Production)

Configure `SCRAPER_ALLOWED_DOMAINS` via environment variable to limit which domains can be scraped:

**Environment Variable** (Recommended):
```bash
# .env file
# Comma-separated list of allowed domains (no spaces)
SCRAPER_ALLOWED_DOMAINS=ridibooks.com,otherdomain.com

# Or for single domain
SCRAPER_ALLOWED_DOMAINS=books.com

# Disable whitelist (NOT recommended for production)
SCRAPER_ALLOWED_DOMAINS=
```

**Django Settings** (Advanced):
```python
# settings.py - automatically configured from environment variable
# The setting parses the comma-separated SCRAPER_ALLOWED_DOMAINS env var
# You can override this if needed:
SCRAPER_ALLOWED_DOMAINS = [
    'book.com',
    'ridibooks.com',
]
```

**Benefits of Environment Variable Configuration**:
- ✅ No code changes required to update domains
- ✅ Different domains per environment (dev/staging/prod)
- ✅ Easy to update via CI/CD or container orchestration
- ✅ No redeployment needed for domain changes
- ✅ Secrets management integration (AWS Secrets Manager, Vault, etc.)

**Why this is critical**: Without a whitelist, attackers could potentially use your server to:
- Scan internal networks
- Access cloud metadata endpoints (AWS, GCP, Azure)
- Probe internal services
- Bypass firewall restrictions

#### 2. Network Isolation (REQUIRED for Production)

Run FlareSolverr in an isolated network with restricted access:

**Docker Compose Example with Network Isolation**:
```yaml
services:
  flaresolverr:
    image: ghcr.io/flaresolverr/flaresolverr:latest
    container_name: flaresolverr
    restart: unless-stopped
    networks:
      - scraper-network
    # DO NOT expose port 8191 to host in production
    # Only Django should access FlareSolverr via Docker network
    
  django:
    # Your Django service
    environment:
      - FLARESOLVERR_URL=http://flaresolverr:8191/v1
      - SCRAPER_ALLOWED_DOMAINS=ridibooks.com
    depends_on:
      - flaresolverr
    networks:
      - scraper-network
      - default  # For external access

networks:
  scraper-network:
    internal: true  # Prevents external access
  default:
    # External network for Django
```

#### 3. Firewall Rules (RECOMMENDED)

Configure firewall rules to prevent FlareSolverr from accessing internal networks:

**Using iptables** (on Docker host):
```bash
# Block FlareSolverr from accessing private IP ranges
iptables -I DOCKER-USER -s <flaresolverr_container_ip> -d 10.0.0.0/8 -j DROP
iptables -I DOCKER-USER -s <flaresolverr_container_ip> -d 172.16.0.0/12 -j DROP
iptables -I DOCKER-USER -s <flaresolverr_container_ip> -d 192.168.0.0/16 -j DROP
iptables -I DOCKER-USER -s <flaresolverr_container_ip> -d 127.0.0.0/8 -j DROP
iptables -I DOCKER-USER -s <flaresolverr_container_ip> -d 169.254.0.0/16 -j DROP
```

**Using Docker networks with egress filtering** (recommended):
```yaml
networks:
  scraper-network:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.enable_ip_masquerade: "false"
```

#### 4. Known Limitations

**DNS Rebinding / TOCTOU Vulnerability**:
- DNS resolution is checked when validating URLs
- DNS could change between validation and FlareSolverr's actual request
- An attacker could exploit this with fast-changing DNS records

**Example attack scenario**:
1. Attacker controls `malicious.com`
2. Initial DNS query: `malicious.com` → `1.2.3.4` (public IP, passes validation)
3. DNS TTL set to 1 second
4. DNS changes: `malicious.com` → `192.168.1.1` (private IP)
5. FlareSolverr makes request to private IP

**Mitigations**:
- ✅ Domain whitelist (primary defense) - only allow trusted domains
- ✅ Private IP blocking at validation time (reduces attack window)
- ✅ Network isolation prevents access even if validation bypassed
- ✅ Firewall rules provide additional layer
- ⚠️ Cannot completely eliminate DNS rebinding risk

**Best practice**: Combine ALL security layers (defense-in-depth).

#### 5. Trusted Networks Only

**FlareSolverr should ONLY be accessible from trusted services**:

**Trusted Access** (✅ Allowed):
- Your Django application (via Docker network or localhost)
- Internal monitoring/logging services
- Administrators via VPN/bastion host for debugging

**Untrusted Access** (❌ Forbidden):
- Public internet
- User devices
- Third-party services
- DMZ networks

**Network Architecture Example**:
```
[Internet] 
    ↓
[Reverse Proxy/Load Balancer] (Public)
    ↓
[Django Application] (Private Network)
    ↓
[FlareSolverr] (Isolated Private Network)
    ↓
[Target Websites Only] (Egress filtered)
```

**Verification**:
```bash
# From external network - should FAIL
curl http://your-server:8191/

# From Django container - should SUCCEED
docker exec django-container curl http://flaresolverr:8191/
```

#### 5. Resource Consumption & Rate Limiting (REQUIRED for Production)

**FlareSolverr is resource-intensive** because it runs headless Chrome browsers:

**Resource Concerns**:
- 🖥️ **High Memory Usage**: Each browser session can use 100-500MB of RAM
- ⚡ **CPU Intensive**: JavaScript execution and page rendering consume significant CPU
- ⏱️ **Slow Response Times**: Pages can take 5-30 seconds to fully load
- 🔄 **Session Accumulation**: Unclosed sessions can leak memory over time

**Production Recommendations**:

1. **Set Resource Limits** (Docker):
   ```yaml
   services:
     flaresolverr:
       image: ghcr.io/flaresolverr/flaresolverr:latest
       deploy:
         resources:
           limits:
             memory: 2G      # Limit memory usage
             cpus: '2.0'     # Limit CPU cores
           reservations:
             memory: 512M    # Minimum memory
             cpus: '0.5'     # Minimum CPU
   ```

2. **Configure FlareSolverr Environment Variables**:
   ```yaml
   services:
     flaresolverr:
       environment:
         - LOG_LEVEL=info
         - CAPTCHA_SOLVER=none
         - TZ=America/New_York
         # Limit concurrent sessions (default: no limit)
         - BROWSER_TIMEOUT=40000  # 40 seconds max per request
   ```

3. **Implement Rate Limiting** in Django:
   ```python
   # settings.py or middleware
   from django.core.cache import cache
   from django.http import HttpResponse
   
   def check_scraper_rate_limit(user_id):
       key = f'scraper_rate_limit:{user_id}'
       requests = cache.get(key, 0)
       if requests >= 10:  # Max 10 requests per hour
           return False
       cache.set(key, requests + 1, 3600)  # 1 hour timeout
       return True
   ```

4. **Monitor Resource Usage**:
   ```bash
   # Check FlareSolverr memory/CPU usage
   docker stats flaresolverr
   
   # Watch for memory leaks
   docker logs flaresolverr | grep -i "memory\|error\|crash"
   ```

5. **Implement Health Checks**:
   ```yaml
   services:
     flaresolverr:
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8191/"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 40s
   ```

6. **Consider Multiple Instances** for high-traffic applications:
   - Use a load balancer to distribute requests
   - Deploy separate FlareSolverr instances per environment
   - Scale horizontally instead of vertically

**Abuse Prevention**:
- ⚠️ Without rate limiting, attackers could exhaust server resources
- ⚠️ Public exposure enables resource exhaustion DoS attacks
- ⚠️ Implement request quotas per user/API key
- ⚠️ Monitor for unusual patterns (rapid requests, failed requests)

#### 6. Monitoring (RECOMMENDED)

Monitor FlareSolverr logs for suspicious activity:

```bash
# View FlareSolverr logs
docker logs -f flaresolverr

# Watch for unusual patterns:
# - Requests to IP addresses (instead of domains)
# - High volume of requests
# - Requests to unexpected domains
# - DNS resolution failures
```

Set up alerts for:
- Requests to internal IP addresses
- Domains not in whitelist (if logging enabled)
- Unusual request volumes
- FlareSolverr errors or crashes

#### 7. Environment Variable Security

**Simple Configuration** (Built-in):
```bash
# .env file - automatically parsed by settings.py
SCRAPER_ALLOWED_DOMAINS=book.com,ridibooks.com

# FlareSolverr URL
FLARESOLVERR_URL=http://flaresolverr:8191/v1
```

**Advanced Configuration** (Custom validation):
```python
# Production settings.py - add custom validation if needed
from django.core.exceptions import ImproperlyConfigured

# Domain whitelist is already configured from environment variable
# Add validation to ensure it's set in production
if not SCRAPER_ALLOWED_DOMAINS and not DEBUG:
    raise ImproperlyConfigured(
        "SCRAPER_ALLOWED_DOMAINS must be set in production for security. "
        "Set it as comma-separated list: SCRAPER_ALLOWED_DOMAINS=domain1.com,domain2.com"
    )

# Log configuration for security audit
import logging
logger = logging.getLogger(__name__)
if SCRAPER_ALLOWED_DOMAINS:
    logger.info(f"Scraper domain whitelist enabled: {len(SCRAPER_ALLOWED_DOMAINS)} domains")
else:
    logger.warning("SECURITY WARNING: Scraper domain whitelist is DISABLED")
```

# REQUIRED: Secure FlareSolverr URL
FLARESOLVERR_URL = env('FLARESOLVERR_URL', default='http://flaresolverr:8191/v1')

### Docker Compose

Add FlareSolverr to your `docker-compose.yml`:

**Development (Local Testing)**:
```yaml
services:
  flaresolverr:
    image: ghcr.io/flaresolverr/flaresolverr:latest
    container_name: flaresolverr
    ports:
      - "8191:8191"  # OK for local development only
    restart: unless-stopped
  
  django:
    # Your Django service configuration
    environment:
      - FLARESOLVERR_URL=http://flaresolverr:8191/v1
    depends_on:
      - flaresolverr
```

**Production (Secure)**:
```yaml
services:
  flaresolverr:
    image: ghcr.io/flaresolverr/flaresolverr:latest
    container_name: flaresolverr
    # NO ports exposed - internal network only
    networks:
      - scraper-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
    environment:
      - LOG_LEVEL=info
      - BROWSER_TIMEOUT=40000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8191/"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  django:
    # Your Django service configuration
    environment:
      - FLARESOLVERR_URL=http://flaresolverr:8191/v1
      - SCRAPER_ALLOWED_DOMAINS=ridibooks.com,book.com
    depends_on:
      - flaresolverr
    networks:
      - scraper-network
      - default  # For external access

networks:
  scraper-network:
    internal: true  # Isolated network
  default:
    # External network for Django
```

**Note**: When services are in the same Docker network, use the service name (`flaresolverr`) as the hostname instead of `localhost`.

### Environment Variables

Make sure your production environment has `FLARESOLVERR_URL` configured:

```bash
# Example for production
export FLARESOLVERR_URL=http://flaresolverr:8191/v1
```
