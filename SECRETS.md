# Secrets Management Strategy

## Overview

KCardSwap uses different secrets management approaches for different environments:

- **Local Development**: `.env` file (git-ignored)
- **CI/CD**: GitHub Secrets
- **Production**: Cloud Secret Manager (GCP Secret Manager)

## Local Development

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update the values in `.env` with your local configuration:
   ```bash
   DATABASE_URL=postgresql://kcardswap:kcardswap@localhost:5432/kcardswap
   GCS_BUCKET=your-dev-bucket
   JWT_SECRET=your-local-secret-key-min-32-chars
   ```

3. **NEVER commit `.env` to version control** - it's already in `.gitignore`

## Required Secrets

### Backend Service

| Secret | Description | Example |
|--------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/dbname` |
| `GCS_BUCKET` | Google Cloud Storage bucket name | `kcardswap-dev` |
| `JWT_SECRET` | Secret key for JWT signing (min 32 chars) | Generate with `openssl rand -base64 32` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID (Phase 1) | `xxx.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret (Phase 1) | `GOCSPX-xxx` |

### Future Secrets (Phase 2+)

| Secret | Description | Phase |
|--------|-------------|-------|
| `FCM_SERVER_KEY` | Firebase Cloud Messaging key | Phase 5 (CHAT) |
| `GCP_SERVICE_ACCOUNT_KEY` | Service account for GCS | Phase 2 (CARD) |

## CI/CD (GitHub Actions)

Secrets are stored in GitHub repository settings:

1. Go to repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `DATABASE_URL` (test database)
   - `JWT_SECRET` (test secret)
   - `GCS_BUCKET` (test bucket)

### GitHub Actions Usage

```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  JWT_SECRET: ${{ secrets.JWT_SECRET }}
```

## Production Environment

**For production deployments, use GCP Secret Manager:**

### Setup

1. Enable Secret Manager API:
   ```bash
   gcloud services enable secretmanager.googleapis.com
   ```

2. Create secrets:
   ```bash
   echo -n "your-secret-value" | gcloud secrets create JWT_SECRET --data-file=-
   ```

3. Grant service account access:
   ```bash
   gcloud secrets add-iam-policy-binding JWT_SECRET \
     --member="serviceAccount:your-service-account@project.iam.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

### Application Access

In production, the backend will fetch secrets from Secret Manager:

```python
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

## Security Best Practices

1. **Rotate secrets regularly** (every 90 days minimum)
2. **Use strong, random secrets** (min 32 characters for JWT)
3. **Never log secrets** or expose them in error messages
4. **Limit secret access** to only required services
5. **Audit secret access** regularly in production
6. **Use different secrets** for each environment

## Secret Generation

### JWT Secret
```bash
openssl rand -base64 32
```

### Database Password
```bash
openssl rand -base64 24
```

### API Keys
Use provider's dashboard (Google Cloud Console, etc.)

## Troubleshooting

### Local Development

- If `.env` is not loaded: Ensure docker-compose is reading it correctly
- If secrets are exposed: Run `git secrets --scan` to check

### CI/CD

- If secrets are missing: Check GitHub repository settings
- If secrets fail: Verify secret names match workflow references

### Production

- If Secret Manager fails: Check IAM permissions
- If secrets are not found: Verify secret exists and version is latest

## Emergency Response

If a secret is compromised:

1. **Immediately rotate** the secret
2. **Revoke access** from the compromised key
3. **Audit logs** to identify unauthorized access
4. **Update all environments** with new secret
5. **Document the incident** for future reference
