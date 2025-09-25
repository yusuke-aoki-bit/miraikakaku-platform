# Configuration Management

This directory contains standardized configuration files for the MiraiKakaku system.

## Directory Structure

```
config/
├── templates/          # Template configuration files
│   ├── batch.env.template
│   ├── api.env.template
│   └── frontend.env.template
├── batch/             # Batch processing configurations
│   └── batch-config.yaml.template
├── api/               # API server configurations
│   └── api-config.yaml.template
└── README.md          # This file
```

## Security Guidelines

1. **Never commit actual credentials** - Use templates with placeholder values
2. **Use environment variables** - All sensitive data should come from environment
3. **Template naming convention** - All template files end with `.template`
4. **Local overrides** - Create local copies without `.template` extension

## Usage

1. Copy template files to create your local configuration:
   ```bash
   cp config/templates/api.env.template miraikakakuapi/.env
   cp config/templates/batch.env.template miraikakakubatch/.env
   ```

2. Replace placeholder values with your actual configuration

3. Ensure your `.env` files are listed in `.gitignore`