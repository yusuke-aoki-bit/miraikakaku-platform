# GitHub Secrets Setup Guide

## Required GitHub Repository Secrets

To enable the CI/CD pipeline, set up the following secrets in your GitHub repository:

### Navigation
1. Go to your GitHub repository
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Production Secrets

#### 1. GCP_PROJECT_ID
```
Your Google Cloud Project ID (e.g., pricewise-huqkr)
```

#### 2. GCP_SA_KEY
```
Your Google Cloud Service Account JSON key (entire JSON content)
```

#### 3. SLACK_WEBHOOK_URL
```
https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

#### 4. DATABASE_URL
```
postgresql://username:password@host:port/database
```

#### 5. JWT_SECRET_KEY
```
A strong, randomly generated JWT secret key
```

### Environment-Specific Secrets

#### Staging Environment
Set up environment-specific secrets under **Environments**:

1. Go to **Settings** → **Environments**
2. Create environment: `staging`
3. Add required reviewers (optional)
4. Add environment-specific secrets

#### Production Environment
1. Create environment: `production`
2. **Enable required reviewers** (recommended for production)
3. Add production-specific secrets

## Environment Variables for Each Service

### API Service Secrets
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db
DB_HOST=your-db-host
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_NAME=your-db-name

# Authentication
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256

# External APIs
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
YAHOO_FINANCE_API_KEY=your-yahoo-key

# Google Cloud
VERTEX_AI_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1
```

### Batch Service Secrets
```bash
# Database (same as API)
DATABASE_URL=postgresql://user:pass@host:port/db

# Google Cloud
GCP_PROJECT_ID=your-project-id
CLOUD_SQL_CONNECTION_NAME=project:region:instance

# External APIs
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
```

### Frontend Service Secrets
```bash
# API URLs
NEXT_PUBLIC_API_URL=https://your-api-url.com
```

## Security Best Practices

### 1. Secret Rotation
- Rotate secrets regularly (quarterly recommended)
- Use different secrets for different environments
- Monitor secret usage in GitHub Actions logs

### 2. Access Control
- Use environment protection rules
- Require approvals for production deployments
- Limit secret access to specific branches

### 3. Secret Management
- Never log secrets in GitHub Actions
- Use masked secrets in workflows
- Store secrets in external systems (AWS Secrets Manager, GCP Secret Manager) when possible

## Testing the Setup

### 1. Validate Secrets
Run this workflow to validate your secrets setup:

```yaml
name: Validate Secrets
on: workflow_dispatch

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Check GCP Project ID
        run: echo "GCP Project: ${{ secrets.GCP_PROJECT_ID }}"

      - name: Validate GCP Service Account
        run: |
          echo "${{ secrets.GCP_SA_KEY }}" | base64 -d | jq .project_id
```

### 2. Test Deployment Pipeline
1. Create a test branch
2. Make a small change
3. Create a Pull Request
4. Verify CI pipeline runs successfully
5. Merge to trigger deployment

## Troubleshooting

### Common Issues

#### 1. "Secret not found" error
- Check secret name spelling
- Ensure secret is set at repository level (not organization)
- Verify environment name matches workflow

#### 2. GCP Authentication Error
- Validate service account JSON format
- Check service account permissions
- Ensure project ID matches

#### 3. Database Connection Error
- Verify connection string format
- Check firewall rules
- Validate credentials

### Debug Commands

```bash
# Test GCP authentication
gcloud auth activate-service-account --key-file=<(echo "$GCP_SA_KEY")
gcloud projects list

# Test database connection
psql "$DATABASE_URL" -c "SELECT 1"

# Validate JWT secret
python -c "import jwt; print('JWT secret is valid')" || echo "JWT library not available"
```

## Next Steps

After setting up secrets:

1. **Test the CI pipeline** with a small PR
2. **Verify staging deployment** works correctly
3. **Test production deployment** with manual approval
4. **Set up monitoring** for pipeline failures
5. **Configure notification channels** for deployment status

## Support

If you encounter issues:
1. Check GitHub Actions logs for error details
2. Verify all secrets are correctly formatted
3. Test individual components (GCP auth, DB connection, etc.)
4. Review this guide for missing steps