# Production Deployment (GCE + Docker Compose)

This guide targets a single GCE VM deployment for:
- Web: https://leonardtechsolutions.com/projects/kcardswap
- API: https://leonardtechsolutions.com/projects/kcardswap/api/v1/...

## Prerequisites
- GCE VM with public IP
- Domain DNS A record pointing to the VM IP
- Firewall allows inbound TCP 80 and 443

## DNS
Create or update DNS A records:
- leonardtechsolutions.com -> <GCE_PUBLIC_IP>

## GCE VM setup
1) SSH into the VM
2) Clone the repo to /opt/kcardswap (or set REPO_DIR later)

## Environment variables
1) Copy example file:

```bash
cp .env.prod.example .env.prod
```

2) Edit .env.prod and set the required values:
- JWT_SECRET_KEY
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- NEXT_PUBLIC_GOOGLE_CLIENT_ID
- GCS_BUCKET_NAME

3) GCS credentials options
- Option A (recommended): Use VM Service Account with GCS permissions
  - Leave GCS_CREDENTIALS_PATH empty
- Option B: Use a key file
  - Place key on the VM, for example: /opt/secrets/gcp-sa.json
  - Update GCS_CREDENTIALS_PATH=/secrets/gcp-sa.json
  - Add a volume mount for backend in [docker-compose.prod.yml](docker-compose.prod.yml)

## Caddy routing
Caddy must route API and Web correctly:
- /projects/kcardswap/api -> backend
- /projects/kcardswap -> web

## Deploy
Run the helper script:

```bash
bash scripts/gce-deploy.sh
```

Or run manually:

```bash
make prod-up
```

## Update
After git pull:

```bash
make prod-up
```

## Stop

```bash
make prod-down
```

## Notes
- Database data persists in the db_data volume and is not removed by prod-up.
- If you run make prod-down -v, all volumes (including DB) are removed.
