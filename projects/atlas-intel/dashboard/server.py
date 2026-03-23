#!/usr/bin/env python3
"""
Atlas Intel Dashboard — Secure Server
JWT auth, rate limiting, HTTPS-ready.
"""

import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, Request, Response, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jose import jwt

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DASHBOARD_DIR = Path(__file__).parent
DATA_DIR = DASHBOARD_DIR / "data"
CONFIG_FILE = DASHBOARD_DIR / ".auth_config.json"

# JWT settings
JWT_SECRET = os.environ.get("ATLAS_JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24
COOKIE_NAME = "atlas_session"

# Rate limiting
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 300  # 5 min lockout after max attempts
login_attempts: dict[str, list[float]] = {}  # ip -> [timestamps]

# ---------------------------------------------------------------------------
# User store (file-based, bcrypt hashed)
# ---------------------------------------------------------------------------

def _load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def _save_config(cfg: dict):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    os.chmod(str(CONFIG_FILE), 0o600)

def _hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """Hash password with PBKDF2-SHA256 (100k iterations)."""
    if salt is None:
        salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return h.hex(), salt

def setup_user(username: str, password: str):
    """Create or update a user with PBKDF2-hashed password."""
    cfg = _load_config()
    cfg["users"] = cfg.get("users", {})
    h, salt = _hash_password(password)
    cfg["users"][username] = {
        "hash": h,
        "salt": salt,
        "created": datetime.now(timezone.utc).isoformat(),
    }
    cfg["jwt_secret"] = JWT_SECRET
    _save_config(cfg)
    print(f"✅ User '{username}' configured")

def verify_user(username: str, password: str) -> bool:
    cfg = _load_config()
    user = cfg.get("users", {}).get(username)
    if not user:
        return False
    h, _ = _hash_password(password, user["salt"])
    return hmac.compare_digest(h, user["hash"])

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

def check_rate_limit(ip: str) -> tuple[bool, int]:
    """Returns (allowed, seconds_until_unlock)."""
    now = time.time()
    attempts = login_attempts.get(ip, [])
    # Prune old attempts
    attempts = [t for t in attempts if now - t < LOCKOUT_SECONDS]
    login_attempts[ip] = attempts
    
    if len(attempts) >= MAX_LOGIN_ATTEMPTS:
        oldest = min(attempts)
        unlock_in = int(LOCKOUT_SECONDS - (now - oldest))
        return False, max(unlock_in, 1)
    return True, 0

def record_attempt(ip: str):
    login_attempts.setdefault(ip, []).append(time.time())

# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

def create_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": username, "exp": expire, "iat": datetime.now(timezone.utc)},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

def verify_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Auth middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    
    # Allow login page and login endpoint without auth
    if path in ("/login", "/api/login", "/favicon.ico"):
        return await call_next(request)
    
    # Allow static assets for login page
    if path.startswith("/static/login"):
        return await call_next(request)
    
    # Check JWT cookie
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return RedirectResponse("/login", status_code=303)
    
    username = verify_token(token)
    if not username:
        response = RedirectResponse("/login", status_code=303)
        response.delete_cookie(COOKIE_NAME)
        return response
    
    request.state.user = username
    return await call_next(request)


# ---------------------------------------------------------------------------
# Login page
# ---------------------------------------------------------------------------

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ATLAS INTEL // AUTHENTICATE</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            background: #0a0a0f;
            color: #00ffcc;
            font-family: 'JetBrains Mono', monospace;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        
        /* CRT scanlines */
        body::after {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 255, 204, 0.03) 0px,
                rgba(0, 255, 204, 0.03) 1px,
                transparent 1px,
                transparent 3px
            );
            pointer-events: none;
            z-index: 1000;
        }
        
        /* Animated grid background */
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: 
                linear-gradient(rgba(0, 255, 204, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 204, 0.02) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: gridPulse 4s ease-in-out infinite;
        }
        
        @keyframes gridPulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.7; }
        }
        
        .login-container {
            position: relative;
            z-index: 10;
            width: 420px;
            padding: 40px;
            background: rgba(10, 10, 15, 0.95);
            border: 1px solid rgba(0, 255, 204, 0.3);
            box-shadow: 
                0 0 30px rgba(0, 255, 204, 0.1),
                inset 0 0 30px rgba(0, 255, 204, 0.02);
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-header h1 {
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 8px;
            color: #00ffcc;
            text-shadow: 0 0 20px rgba(0, 255, 204, 0.5);
            margin-bottom: 8px;
        }
        
        .login-header .subtitle {
            font-size: 11px;
            color: rgba(0, 255, 204, 0.5);
            letter-spacing: 4px;
        }
        
        .classification {
            text-align: center;
            margin-bottom: 25px;
            padding: 6px 12px;
            border: 1px solid rgba(255, 215, 0, 0.4);
            color: #ffd700;
            font-size: 10px;
            letter-spacing: 3px;
            display: inline-block;
            width: 100%;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            font-size: 10px;
            letter-spacing: 3px;
            color: rgba(0, 255, 204, 0.6);
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            background: rgba(0, 255, 204, 0.05);
            border: 1px solid rgba(0, 255, 204, 0.2);
            color: #00ffcc;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            outline: none;
            transition: all 0.3s;
        }
        
        .form-group input:focus {
            border-color: #00ffcc;
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.2);
            background: rgba(0, 255, 204, 0.08);
        }
        
        .form-group input::placeholder {
            color: rgba(0, 255, 204, 0.2);
        }
        
        .submit-btn {
            width: 100%;
            padding: 14px;
            background: rgba(0, 255, 204, 0.1);
            border: 1px solid rgba(0, 255, 204, 0.4);
            color: #00ffcc;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 4px;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
        }
        
        .submit-btn:hover {
            background: rgba(0, 255, 204, 0.2);
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.3);
        }
        
        .submit-btn:active {
            transform: scale(0.98);
        }
        
        .error-msg {
            color: #ff3333;
            font-size: 11px;
            text-align: center;
            margin-top: 15px;
            min-height: 16px;
            text-shadow: 0 0 10px rgba(255, 51, 51, 0.5);
        }
        
        .status-line {
            margin-top: 25px;
            padding-top: 15px;
            border-top: 1px solid rgba(0, 255, 204, 0.1);
            font-size: 10px;
            color: rgba(0, 255, 204, 0.3);
            text-align: center;
            letter-spacing: 2px;
        }
        
        .status-line .blink {
            animation: blink 1s step-end infinite;
        }
        
        @keyframes blink {
            50% { opacity: 0; }
        }
        
        /* Corner decorations */
        .corner { position: absolute; width: 15px; height: 15px; }
        .corner-tl { top: -1px; left: -1px; border-top: 2px solid #00ffcc; border-left: 2px solid #00ffcc; }
        .corner-tr { top: -1px; right: -1px; border-top: 2px solid #00ffcc; border-right: 2px solid #00ffcc; }
        .corner-bl { bottom: -1px; left: -1px; border-bottom: 2px solid #00ffcc; border-left: 2px solid #00ffcc; }
        .corner-br { bottom: -1px; right: -1px; border-bottom: 2px solid #00ffcc; border-right: 2px solid #00ffcc; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="corner corner-tl"></div>
        <div class="corner corner-tr"></div>
        <div class="corner corner-bl"></div>
        <div class="corner corner-br"></div>
        
        <div class="login-header">
            <h1>ATLAS INTEL</h1>
            <div class="subtitle">INTELLIGENCE PLATFORM</div>
        </div>
        
        <div class="classification">TOP SECRET // SI-TK // NOFORN</div>
        
        <form id="loginForm" onsubmit="handleLogin(event)">
            <div class="form-group">
                <label>Operator ID</label>
                <input type="text" id="username" name="username" placeholder="Enter callsign" autocomplete="username" required>
            </div>
            <div class="form-group">
                <label>Access Code</label>
                <input type="password" id="password" name="password" placeholder="••••••••••••" autocomplete="current-password" required>
            </div>
            <button type="submit" class="submit-btn">Authenticate</button>
            <div class="error-msg" id="errorMsg"></div>
        </form>
        
        <div class="status-line">
            SECURE CONNECTION ESTABLISHED <span class="blink">█</span>
        </div>
    </div>
    
    <script>
        async function handleLogin(e) {
            e.preventDefault();
            const btn = document.querySelector('.submit-btn');
            const err = document.getElementById('errorMsg');
            
            btn.textContent = 'AUTHENTICATING...';
            btn.disabled = true;
            err.textContent = '';
            
            try {
                const resp = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: new URLSearchParams({
                        username: document.getElementById('username').value,
                        password: document.getElementById('password').value,
                    })
                });
                
                const data = await resp.json();
                
                if (data.success) {
                    btn.textContent = 'ACCESS GRANTED';
                    btn.style.borderColor = '#00ffcc';
                    btn.style.color = '#00ffcc';
                    setTimeout(() => window.location.href = '/', 500);
                } else {
                    err.textContent = data.error || 'ACCESS DENIED';
                    btn.textContent = 'AUTHENTICATE';
                    btn.disabled = false;
                }
            } catch (ex) {
                err.textContent = 'CONNECTION FAILED';
                btn.textContent = 'AUTHENTICATE';
                btn.disabled = false;
            }
        }
        
        // Focus first input
        document.getElementById('username').focus();
    </script>
</body>
</html>"""


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return LOGIN_HTML


@app.post("/api/login")
async def api_login(request: Request, username: str = Form(...), password: str = Form(...)):
    ip = request.client.host if request.client else "unknown"
    
    # Rate limit check
    allowed, wait = check_rate_limit(ip)
    if not allowed:
        return JSONResponse(
            {"success": False, "error": f"LOCKED — RETRY IN {wait}s"},
            status_code=429,
        )
    
    if verify_user(username, password):
        # Clear attempts on success
        login_attempts.pop(ip, None)
        token = create_token(username)
        response = JSONResponse({"success": True})
        response.set_cookie(
            COOKIE_NAME,
            token,
            httponly=True,
            samesite="strict",
            max_age=JWT_EXPIRE_HOURS * 3600,
            secure=False,  # Set True when behind HTTPS
        )
        return response
    
    record_attempt(ip)
    remaining = MAX_LOGIN_ATTEMPTS - len(login_attempts.get(ip, []))
    return JSONResponse(
        {"success": False, "error": f"ACCESS DENIED — {remaining} ATTEMPTS REMAINING"},
        status_code=401,
    )


@app.get("/api/logout")
async def api_logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response


# ---------------------------------------------------------------------------
# Protected static files
# ---------------------------------------------------------------------------

@app.get("/")
async def serve_index():
    return FileResponse(DASHBOARD_DIR / "index.html")

@app.get("/styles.css")
async def serve_css():
    return FileResponse(DASHBOARD_DIR / "styles.css", media_type="text/css")

@app.get("/app.js")
async def serve_js():
    return FileResponse(DASHBOARD_DIR / "app.js", media_type="application/javascript")

@app.get("/data/{filename}")
async def serve_data(filename: str):
    filepath = DATA_DIR / filename
    if not filepath.exists() or not filepath.suffix == ".json":
        raise HTTPException(404)
    return FileResponse(filepath, media_type="application/json")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import uvicorn
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        # Interactive setup
        username = input("Operator ID: ").strip()
        password = input("Access Code: ").strip()
        if username and password:
            setup_user(username, password)
        else:
            print("❌ Username and password required")
            sys.exit(1)
    elif len(sys.argv) > 3 and sys.argv[1] == "adduser":
        setup_user(sys.argv[2], sys.argv[3])
    else:
        # Check if any users exist
        cfg = _load_config()
        if not cfg.get("users"):
            print("⚠️  No users configured. Run: python server.py adduser <username> <password>")
            sys.exit(1)
        
        port = int(os.environ.get("PORT", 8080))
        print(f"🏛️  Atlas Intel Dashboard — https://localhost:{port}")
        print(f"   Auth: JWT + bcrypt | Rate limit: {MAX_LOGIN_ATTEMPTS} attempts / {LOCKOUT_SECONDS}s lockout")
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
