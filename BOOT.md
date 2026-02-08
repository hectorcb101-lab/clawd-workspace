# BOOT.md — Gateway Startup

On gateway restart, run these checks silently:

1. `atlas-daemon status` — start if not running
2. Check for pending `atlas-mod` modifications
3. Verify email notification daemon: `sudo systemctl is-active email-notify-daemon`

If anything is down, fix it. Don't message Finn unless something critical is broken.
