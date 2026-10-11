# 🚀 NanDark Deployment Guide

## BotKeep.cloud (Recommended)

### Prerequisites
- GitHub account (لینک)
- BotKeep.cloud account (رایگان)

### Steps

1. **ورود به BotKeep.cloud**
   - https://botkeep.cloud
   - GitHub را connect کن

2. **New Project**
   - Select: `vAHiD55555/NanDark`
   - Branch: `master`

3. **Configuration**
   - **Runtime**: Python 3.10
   - **Port**: 8080
   - **Start Command**: `gunicorn server:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60`
   - **Keep Alive**: Enable
   - **Auto-restart**: Enable

4. **Environment Variables**
   ```
   PORT=8080
   DEBUG=False
   LOG_LEVEL=INFO
   ```

5. **Deploy**
   - Click "Deploy" button
   - Wait for build to complete
   - Check logs: `/logs`

### Health Endpoints

- **Root**: `GET /` → Status OK
- **Health**: `GET /health` → Liveness probe (برای keep-alive)
- **Status**: `GET /status` → Full observer output

### Monitoring

```bash
# Check if service is running
curl https://your-app.botkeep.cloud/health

# Get status
curl https://your-app.botkeep.cloud/status
```

### Troubleshooting

**Service goes to sleep?**
- Enable "Always On" in BotKeep settings
- Set up external health check (ping every 5 min)

**Port errors?**
- Make sure PORT is set to 8080 or use $PORT from environment

**Import errors?**
- Check `requirements.txt` is present
- Verify Python version matches

---

## Local Testing (Termux/Android)

```bash
# 1. Clone
git clone https://github.com/vAHiD55555/NanDark.git
cd NanDark

# 2. Install
pip install -r requirements.txt

# 3. Run
export PORT=8080
python server.py

# 4. Test
curl http://localhost:8080/health
```

---

## GitHub Actions CI/CD

✓ Workflow runs on every push to `master`
✓ Checks: flake8 linting
✓ Runs: `python main.py`

Check status: https://github.com/vAHiD55555/NanDark/actions
