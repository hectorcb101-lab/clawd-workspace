# Gmail Push Notifications

Real-time email notifications using Google Pub/Sub.

## Architecture
```
Gmail → Pub/Sub → Webhook (localhost) → Clawdbot notification
```

## Setup Required
1. Google Cloud project with Pub/Sub API enabled
2. Pub/Sub topic for Gmail notifications
3. Gmail watch() configured to push to topic
4. Webhook server to receive and process notifications
