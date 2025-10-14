# 🔴 Redis Setup Guide for FoodieExpress
**Complete Installation & Configuration Guide**

Version: 1.0  
Date: October 14, 2025  
For: FoodieExpress v3.0 Architecture Upgrade

---

## 📋 Table of Contents

1. [What is Redis?](#what-is-redis)
2. [Why FoodieExpress Needs Redis](#why-foodieexpress-needs-redis)
3. [Installation Options](#installation-options)
   - [Option A: Docker (Recommended)](#option-a-docker-recommended)
   - [Option B: Windows Native](#option-b-windows-native)
   - [Option C: Cloud Redis](#option-c-cloud-redis)
4. [Configuration](#configuration)
5. [Verification](#verification)
6. [Production Setup](#production-setup)
7. [Troubleshooting](#troubleshooting)

---

## 🤔 What is Redis?

**Redis** (Remote Dictionary Server) is an open-source, in-memory data structure store used as:
- Database
- Cache
- Message broker
- Session store (← **Our use case**)

### Key Features:
- ⚡ **Lightning fast:** Sub-millisecond latency
- 💾 **Persistent:** Data survives restarts (unlike RAM)
- 📡 **Distributed:** Multiple servers can share data
- ⏰ **TTL support:** Automatic expiry of old data
- 🔒 **Reliable:** Battle-tested by millions of applications

### Popular Users:
- Twitter (session management)
- Instagram (feed caching)
- Uber (geolocation data)
- Stack Overflow (caching)

---

## 🎯 Why FoodieExpress Needs Redis

### The Problem (Before Redis)
```python
# Old approach: In-memory Python dictionary
chat_sessions = {}  # ❌ Problems:
                     # - Lost on restart
                     # - Can't scale to multiple servers
                     # - Memory leaks possible
                     # - No automatic cleanup
```

### The Solution (With Redis)
```python
# New approach: Redis-backed sessions
redis_client.setex(
    f"chat_session:{user_id}",
    ttl=3600,  # Auto-delete after 1 hour
    value=json.dumps(chat_history)
)
# ✅ Benefits:
# - Persists across restarts
# - Shared across multiple servers
# - Automatic cleanup via TTL
# - High performance
```

### Concrete Benefits for FoodieExpress:

| Feature | Without Redis | With Redis |
|---------|---------------|------------|
| **User Experience** | Conversations lost on restart | Conversations persist |
| **Scalability** | 1 server only | 10+ servers possible |
| **Memory Management** | Manual cleanup needed | Automatic TTL-based cleanup |
| **Performance** | 0.001ms (RAM) | 0.5ms (Redis) |
| **Reliability** | Data lost on crash | Data persists |

---

## 🚀 Installation Options

### ⭐ Option A: Docker (Recommended)

**Why Docker?**
- ✅ Easiest installation (one command)
- ✅ Isolated from system
- ✅ Easy to start/stop/remove
- ✅ Same setup on Windows/Mac/Linux

#### Prerequisites:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed

#### Installation Steps:

```powershell
# 1. Pull Redis image (latest stable version)
docker pull redis:7-alpine

# 2. Run Redis container
docker run -d `
  --name foodie-redis `
  -p 6379:6379 `
  --restart unless-stopped `
  redis:7-alpine

# Expected output:
# abc123def456... (container ID)
```

#### What this does:
- `-d` = Run in background (detached mode)
- `--name foodie-redis` = Give it a friendly name
- `-p 6379:6379` = Map Redis port to localhost
- `--restart unless-stopped` = Auto-restart on reboot
- `redis:7-alpine` = Use Alpine Linux (lightweight)

#### Verify installation:
```powershell
# Check if running
docker ps | Select-String "redis"

# Expected output:
# abc123  redis:7-alpine  "docker-entrypoint.s…"  Up 2 minutes  0.0.0.0:6379->6379/tcp  foodie-redis

# Test Redis connectivity
docker exec -it foodie-redis redis-cli PING

# Expected output:
# PONG
```

#### Management Commands:
```powershell
# Start (if stopped)
docker start foodie-redis

# Stop
docker stop foodie-redis

# Restart
docker restart foodie-redis

# View logs
docker logs foodie-redis

# Connect to Redis CLI
docker exec -it foodie-redis redis-cli

# Remove container (if needed)
docker rm -f foodie-redis
```

---

### Option B: Windows Native

**When to use:** You don't want Docker or need maximum performance

#### Download Redis for Windows:

**Option B1: Redis Official Build (via WSL2)**
1. Install WSL2: `wsl --install`
2. Open Ubuntu terminal
3. Install Redis:
   ```bash
   sudo apt update
   sudo apt install redis-server
   sudo service redis-server start
   ```

**Option B2: Memurai (Windows-native fork)**
1. Download from [Memurai.com](https://www.memurai.com/)
2. Run installer (default settings)
3. Service starts automatically

#### Configuration:
```powershell
# Edit redis.conf (if using WSL)
sudo nano /etc/redis/redis.conf

# Key settings:
bind 127.0.0.1            # Only localhost
port 6379                 # Default port
maxmemory 256mb           # Memory limit
maxmemory-policy allkeys-lru  # Eviction policy
```

#### Verify installation:
```powershell
# Windows PowerShell
redis-cli PING

# Expected: PONG
```

---

### Option C: Cloud Redis

**When to use:** Production deployment or you want managed service

#### Recommended Providers:

1. **Redis Cloud (Official)**
   - Free tier: 30MB
   - Website: https://redis.com/try-free/
   - Setup time: 5 minutes
   
   ```env
   # Your .env configuration
   REDIS_HOST=redis-12345.c1.us-east-1-1.ec2.cloud.redislabs.com
   REDIS_PORT=12345
   REDIS_PASSWORD=your-password-here
   ```

2. **AWS ElastiCache**
   - Integrated with AWS
   - Auto-scaling available
   - Production-grade

3. **Azure Cache for Redis**
   - Integrated with Azure
   - Enterprise support
   - High availability

4. **DigitalOcean Managed Redis**
   - Simple pricing
   - Good performance
   - Easy setup

#### Cloud Setup Example (Redis Cloud):
```powershell
# 1. Sign up at https://redis.com/try-free/
# 2. Create new database
# 3. Copy connection details
# 4. Update .env:

REDIS_ENABLED=true
REDIS_HOST=your-instance.redis.cloud.redislabs.com
REDIS_PORT=12345
REDIS_PASSWORD=your-secure-password
REDIS_DB=0
```

---

## ⚙️ Configuration

### FoodieExpress Configuration

#### 1. Update `food_chatbot_agent/.env`:
```env
# ============================================
# REDIS CONFIGURATION (NEW in v3.0)
# ============================================

# Enable Redis session storage
REDIS_ENABLED=true

# Connection settings
REDIS_HOST=localhost        # Use 'localhost' for Docker/local
REDIS_PORT=6379             # Default Redis port
REDIS_DB=0                  # Database index (0-15)
REDIS_PASSWORD=             # Leave empty for local (no password)

# Session management
SESSION_TTL=3600            # Chat session expiry: 1 hour (3600 seconds)
PENDING_ORDER_TTL=600       # Pending order expiry: 10 minutes (600 seconds)

# Development mode (fallback to in-memory if Redis fails)
# Set to 'false' in production to fail fast on Redis errors
REDIS_FALLBACK_ENABLED=true
```

#### 2. Install Python Redis Client:
```powershell
cd food_chatbot_agent
pip install redis==5.0.1
```

#### 3. Verify configuration:
```powershell
# Start Flask agent
python agent.py

# Expected startup message:
# ✅ Redis connected: localhost:6379 (DB 0)
# 🤖 FoodieExpress AI Agent v3.0
# 🚀 Starting Flask server with Waitress...
```

---

### Redis Server Configuration

#### Basic redis.conf (for Docker):

Create `redis.conf` for custom settings:

```conf
# Network
bind 127.0.0.1              # Only localhost (security)
port 6379                   # Standard port
protected-mode yes          # Require password in production

# Memory
maxmemory 256mb             # Limit memory usage
maxmemory-policy allkeys-lru  # Evict least recently used keys

# Persistence
save 900 1                  # Save after 15 min if ≥1 key changed
save 300 10                 # Save after 5 min if ≥10 keys changed
save 60 10000               # Save after 1 min if ≥10000 keys changed

appendonly yes              # Enable AOF (Append-Only File)
appendfsync everysec        # Sync every second (balance speed/safety)

# Logging
loglevel notice
logfile /var/log/redis/redis.log
```

#### Use custom config with Docker:

```powershell
# 1. Create redis.conf file (above content)
# 2. Run Docker with custom config:

docker run -d `
  --name foodie-redis `
  -p 6379:6379 `
  -v ${PWD}/redis.conf:/usr/local/etc/redis/redis.conf `
  redis:7-alpine redis-server /usr/local/etc/redis/redis.conf
```

---

## ✅ Verification

### Test 1: Basic Connectivity
```powershell
# Connect to Redis CLI
docker exec -it foodie-redis redis-cli

# Run commands:
127.0.0.1:6379> PING
PONG

127.0.0.1:6379> SET test "Hello Redis"
OK

127.0.0.1:6379> GET test
"Hello Redis"

127.0.0.1:6379> DEL test
(integer) 1

127.0.0.1:6379> EXIT
```

### Test 2: TTL (Time-To-Live)
```powershell
docker exec -it foodie-redis redis-cli

127.0.0.1:6379> SETEX mykey 10 "expires in 10 seconds"
OK

127.0.0.1:6379> TTL mykey
(integer) 8  # Seconds remaining

# Wait 10 seconds...

127.0.0.1:6379> GET mykey
(nil)  # Key expired and was deleted
```

### Test 3: FoodieExpress Integration
```powershell
# Start Flask agent
cd food_chatbot_agent
python agent.py

# In another terminal, send test message
curl -X POST http://localhost:5000/chat `
  -H "Content-Type: application/json" `
  -d '{"user_id": "test123", "message": "list restaurants"}'

# Check Redis for session:
docker exec -it foodie-redis redis-cli

127.0.0.1:6379> KEYS chat_session:*
1) "chat_session:test123"

127.0.0.1:6379> TTL chat_session:test123
(integer) 3598  # ~1 hour remaining

127.0.0.1:6379> GET chat_session:test123
# Shows JSON conversation history
```

### Test 4: Session Persistence (Critical Test)
```powershell
# 1. Start chat session
curl -X POST http://localhost:5000/chat `
  -d '{"user_id":"persist-test","message":"list restaurants"}'

# 2. Restart Flask agent (Ctrl+C, then python agent.py)

# 3. Continue conversation (should remember context)
curl -X POST http://localhost:5000/chat `
  -d '{"user_id":"persist-test","message":"show first one"}'

# ✅ Success: AI remembers the restaurant list from before restart
```

---

## 🏭 Production Setup

### Security Hardening

#### 1. Enable Password Authentication
```powershell
# Generate strong password
$password = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
Write-Host "Redis Password: $password"

# Set password in Redis
docker exec -it foodie-redis redis-cli CONFIG SET requirepass "$password"

# Update .env
REDIS_PASSWORD=$password
```

#### 2. Restrict Network Access
```conf
# redis.conf
bind 127.0.0.1 10.0.1.5  # Only specific IPs
protected-mode yes
```

#### 3. Disable Dangerous Commands
```conf
# redis.conf
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

### High Availability Setup

#### Option 1: Redis Sentinel (Automatic Failover)
```powershell
# sentinel.conf
sentinel monitor foodie-master 127.0.0.1 6379 2
sentinel down-after-milliseconds foodie-master 5000
sentinel parallel-syncs foodie-master 1
sentinel failover-timeout foodie-master 10000

# Start sentinel
docker run -d --name redis-sentinel `
  -p 26379:26379 `
  -v ${PWD}/sentinel.conf:/etc/redis/sentinel.conf `
  redis:7-alpine redis-sentinel /etc/redis/sentinel.conf
```

#### Option 2: Redis Cluster (Horizontal Scaling)
```powershell
# Create 6-node cluster (3 masters, 3 replicas)
docker-compose up -d  # See docker-compose.yml below
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  redis-node-1:
    image: redis:7-alpine
    command: redis-server --cluster-enabled yes --cluster-config-file nodes.conf
    ports:
      - "7000:6379"
  
  redis-node-2:
    image: redis:7-alpine
    command: redis-server --cluster-enabled yes --cluster-config-file nodes.conf
    ports:
      - "7001:6379"
  
  # ... (nodes 3-6)

  redis-cluster-create:
    image: redis:7-alpine
    depends_on:
      - redis-node-1
      - redis-node-2
    command: >
      redis-cli --cluster create
      redis-node-1:6379
      redis-node-2:6379
      --cluster-replicas 1
```

### Monitoring

#### 1. Built-in Redis Monitoring
```powershell
# Real-time stats
docker exec -it foodie-redis redis-cli INFO

# Monitor commands
docker exec -it foodie-redis redis-cli MONITOR

# Slow log
docker exec -it foodie-redis redis-cli SLOWLOG GET 10
```

#### 2. Redis Commander (Web UI)
```powershell
docker run -d `
  --name redis-commander `
  -p 8081:8081 `
  -e REDIS_HOSTS=local:foodie-redis:6379 `
  --link foodie-redis:foodie-redis `
  rediscommander/redis-commander

# Access: http://localhost:8081
```

### Backup Strategy

#### Automated Backups
```powershell
# Create backup script: backup-redis.ps1
$date = Get-Date -Format "yyyyMMdd-HHmmss"
$backup_dir = "C:\Backups\Redis"

# Trigger Redis save
docker exec foodie-redis redis-cli BGSAVE

# Wait for save to complete
Start-Sleep -Seconds 5

# Copy RDB file
docker cp foodie-redis:/data/dump.rdb "$backup_dir\dump-$date.rdb"

Write-Host "✅ Backup created: dump-$date.rdb"

# Schedule: Run daily at 2 AM
# Task Scheduler → Create Task → Run backup-redis.ps1
```

---

## 🐛 Troubleshooting

### Issue: "Redis connection refused"

**Symptoms:**
```
❌ Redis connection error: Error 111 connecting to localhost:6379
```

**Solutions:**
1. Check if Redis is running:
   ```powershell
   docker ps | Select-String "redis"
   ```
   
2. Start Redis if stopped:
   ```powershell
   docker start foodie-redis
   ```

3. Verify port is not blocked:
   ```powershell
   Test-NetConnection -ComputerName localhost -Port 6379
   ```

---

### Issue: "Authentication failed"

**Symptoms:**
```
NOAUTH Authentication required
```

**Solutions:**
1. Check if password is set:
   ```powershell
   docker exec -it foodie-redis redis-cli CONFIG GET requirepass
   ```

2. Update .env with correct password:
   ```env
   REDIS_PASSWORD=your-actual-password
   ```

3. Test with password:
   ```powershell
   docker exec -it foodie-redis redis-cli -a your-password PING
   ```

---

### Issue: "Out of memory"

**Symptoms:**
```
OOM command not allowed when used memory > 'maxmemory'
```

**Solutions:**
1. Check memory usage:
   ```powershell
   docker exec -it foodie-redis redis-cli INFO MEMORY
   ```

2. Increase maxmemory:
   ```powershell
   docker exec -it foodie-redis redis-cli CONFIG SET maxmemory 512mb
   ```

3. Set eviction policy:
   ```powershell
   docker exec -it foodie-redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
   ```

---

### Issue: "Slow performance"

**Symptoms:**
- Chat responses taking > 5 seconds
- Redis queries timing out

**Solutions:**
1. Check slow log:
   ```powershell
   docker exec -it foodie-redis redis-cli SLOWLOG GET 10
   ```

2. Monitor commands:
   ```powershell
   docker exec -it foodie-redis redis-cli MONITOR
   # Look for expensive operations (KEYS *, etc.)
   ```

3. Optimize keys:
   ```powershell
   # Instead of KEYS * (slow)
   # Use SCAN (fast)
   docker exec -it foodie-redis redis-cli SCAN 0 MATCH chat_session:*
   ```

---

## 📚 Additional Resources

### Official Documentation
- [Redis.io](https://redis.io/) - Official website
- [Redis Commands](https://redis.io/commands/) - Complete command reference
- [Redis Data Types](https://redis.io/docs/data-types/) - Strings, Lists, Sets, etc.
- [Redis Persistence](https://redis.io/docs/management/persistence/) - RDB vs AOF

### Python Redis Client
- [redis-py GitHub](https://github.com/redis/redis-py) - Python client docs
- [redis-py Commands](https://redis-py.readthedocs.io/) - API reference

### Community
- [Redis Discord](https://discord.gg/redis) - Official community
- [r/redis](https://reddit.com/r/redis) - Reddit community
- [Stack Overflow](https://stackoverflow.com/questions/tagged/redis) - Q&A

### Tools
- [Redis Commander](https://github.com/joeferner/redis-commander) - Web UI
- [RedisInsight](https://redis.com/redis-enterprise/redis-insight/) - Official GUI
- [redis-cli](https://redis.io/docs/ui/cli/) - Command-line interface

---

## ✅ Completion Checklist

- [ ] Redis installed (Docker/Native/Cloud)
- [ ] Redis running on port 6379
- [ ] Connectivity tested (`PING` → `PONG`)
- [ ] TTL tested (keys expire correctly)
- [ ] FoodieExpress agent connects successfully
- [ ] Session persistence verified (survives restart)
- [ ] `.env` configured with Redis settings
- [ ] Password set (production only)
- [ ] Backup strategy configured (production only)
- [ ] Monitoring setup (production only)

---

## 🎉 Next Steps

1. ✅ Redis installed and verified
2. → Read [ARCHITECTURE_UPGRADE_COMPLETE.md](./ARCHITECTURE_UPGRADE_COMPLETE.md)
3. → Deploy upgraded agent.py (v3.0)
4. → Test complete system
5. → Deploy to production! 🚀

---

**Document Version:** 1.0  
**Last Updated:** October 14, 2025  
**Maintained By:** FoodieExpress DevOps Team  
**Support:** redis-support@foodieexpress.com
