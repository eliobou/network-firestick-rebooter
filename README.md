# network-firestick-rebooter

Minimal Flask HTTP server to reboot an Amazon Firestick via ADB, triggered from an iOS Shortcut over VPN.

```
iPhone (iOS Shortcuts) → VPN → Raspberry Pi :8765 → Flask → ADB → Firestick 192.168.1.99:5555
```

## Prerequisites

- Raspberry Pi with Docker
- ADB enabled on the Firestick (`Settings > Developer Options > ADB Debugging`)
- VPN to reach the Pi from the iPhone

## Deploy

### 1. Build

```bash
docker build -t network-firestick-rebooter .
```

### 2. Generate and persist the ADB key

```bash
docker run -d --name network-firestick-rebooter --network host network-firestick-rebooter
curl http://localhost:8765/reboot
docker exec network-firestick-rebooter cat /root/.android/adbkey > /home/pi/adbkey
docker exec network-firestick-rebooter cat /root/.android/adbkey.pub > /home/pi/adbkey.pub
docker rm -f network-firestick-rebooter
```

### 3. Authorize the Pi on the Firestick

Run the command below, then **accept the popup on the Firestick** (check "Always allow"):

```bash
docker run --rm --network host \
  -v /home/pi/adbkey:/root/.android/adbkey \
  -v /home/pi/adbkey.pub:/root/.android/adbkey.pub \
  network-firestick-rebooter adb connect 192.168.1.99:5555
```

### 4. Run

```bash
docker run -d \
  --name network-firestick-rebooter \
  --restart always \
  --network host \
  -v /home/pi/adbkey:/root/.android/adbkey \
  -v /home/pi/adbkey.pub:/root/.android/adbkey.pub \
  network-firestick-rebooter
```

### 5. Enable Docker on boot

```bash
sudo systemctl enable docker
```

## API

```
GET /reboot
```

```bash
curl http://192.168.1.23:8765/reboot
# {"success": true, "message": "Reboot triggered successfully"}
```

## iOS Shortcut

1. New shortcut → **Get contents of URL**
2. URL: `http://192.168.1.23:8765/reboot` — Method: **GET**
3. Must have local network access on the iPhone (eg: VPN)

## Configuration

Edit in `app.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `FIRESTICK_IP` | `192.168.1.99` | Firestick IP |
| `FIRESTICK_PORT` | `5555` | ADB port |
| `port` | `8765` | Flask listen port |
