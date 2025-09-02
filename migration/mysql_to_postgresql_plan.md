# MySQL to PostgreSQL Migration Plan
## Miraikakaku Database Migration Strategy

### 📊 Current State Analysis
- **Source**: Cloud SQL MySQL 8.4 (us-central1)
- **Data Volume**: 432,170 records across 63 tables
- **Key Tables**: 
  - stock_predictions: 261,524 records
  - stock_price_history: 158,450 records  
  - stock_master: 9,648 records
  - financial_news: 1,510 records

### 🎯 Migration Strategy

#### Phase 1: PostgreSQL Instance Setup
1. **Create Cloud SQL PostgreSQL Instance**
   - Version: PostgreSQL 15
   - Region: us-central1 (same as current MySQL)
   - Tier: db-custom-2-8192 (match current specs)
   - Storage: SSD with auto-increase

#### Phase 2: Schema Migration
1. **Export MySQL Schema**
   - Generate DDL for all tables
   - Identify MySQL-specific syntax
   - Map data types to PostgreSQL equivalents

2. **PostgreSQL Schema Adaptation**
   - Convert AUTO_INCREMENT → SERIAL/SEQUENCE
   - Update MySQL functions to PostgreSQL equivalents
   - Adjust indexing strategies
   - Handle charset/collation differences

#### Phase 3: Data Migration
1. **Batch Data Export from MySQL**
   - Use mysqldump with --no-create-info for data only
   - Split large tables into chunks
   - Export in CSV format for PostgreSQL import

2. **PostgreSQL Data Import**
   - Use COPY command for bulk insert
   - Validate record counts
   - Verify data integrity

#### Phase 4: Application Migration
1. **Update Connection Strings**
   - Change from PyMySQL to psycopg2
   - Update database URLs in all services
   - Modify environment variables

2. **Code Adaptation**
   - Update SQL syntax differences
   - Modify ORM configurations  
   - Test all database operations

#### Phase 5: Real Data Integration
1. **PostgreSQL-Compatible Data Collector**
   - Replace PyMySQL with psycopg2
   - Update batch jobs for PostgreSQL
   - Test Alpha Vantage integration

### 🔄 Migration Commands

#### 1. Create PostgreSQL Instance
```bash
gcloud sql instances create miraikakaku-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-8192 \
  --region=us-central1 \
  --storage-type=SSD \
  --storage-size=100GB \
  --storage-auto-increase
```

#### 2. Setup Database and User
```bash
# Create database
gcloud sql databases create miraikakaku --instance=miraikakaku-postgres

# Create user
gcloud sql users create miraikakaku-user \
  --instance=miraikakaku-postgres \
  --password=miraikakaku-secure-pass-2024
```

#### 3. Schema Export and Conversion
```bash
# Export MySQL schema
mysqldump -h 34.58.103.36 -u miraikakaku-user -p \
  --no-data --routines --triggers miraikakaku > mysql_schema.sql

# Convert to PostgreSQL (manual process)
```

#### 4. Data Migration
```bash
# Export data from MySQL
mysqldump -h 34.58.103.36 -u miraikakaku-user -p \
  --no-create-info --skip-triggers miraikakaku > mysql_data.sql

# Import to PostgreSQL (after conversion)
psql -h [POSTGRES_IP] -U miraikakaku-user -d miraikakaku -f postgres_data.sql
```

### 📋 Data Type Mapping

| MySQL Type | PostgreSQL Type | Notes |
|------------|-----------------|-------|
| INT AUTO_INCREMENT | SERIAL | Primary key sequences |
| VARCHAR(n) | VARCHAR(n) | Direct mapping |
| TEXT | TEXT | Direct mapping |
| DATETIME | TIMESTAMP | Timezone considerations |
| DECIMAL(p,s) | NUMERIC(p,s) | Direct mapping |
| TINYINT(1) | BOOLEAN | Boolean conversion |
| JSON | JSONB | Use JSONB for better performance |

### ⚠️ Potential Issues

1. **Character Set/Collation**
   - MySQL: utf8mb4_unicode_ci
   - PostgreSQL: UTF8 with specific collation

2. **SQL Syntax Differences**
   - LIMIT/OFFSET syntax
   - Date/time functions
   - String concatenation (|| vs CONCAT)

3. **Application Code Changes**
   - PyMySQL → psycopg2
   - Connection pooling
   - Transaction handling

### 📊 Migration Timeline

- **Phase 1 (Setup)**: 1 hour
- **Phase 2 (Schema)**: 2-3 hours  
- **Phase 3 (Data)**: 1-2 hours
- **Phase 4 (Applications)**: 3-4 hours
- **Phase 5 (Testing)**: 2 hours

**Total Estimated Time**: 8-12 hours

### 🔄 Rollback Strategy

1. Keep MySQL instance running during migration
2. Maintain dual-write capability during testing
3. Switch traffic gradually
4. Full rollback available within 24 hours

### ✅ Success Criteria

1. All 432,170 records migrated successfully
2. Application functionality 100% preserved
3. Real data collection working with PostgreSQL
4. Performance equal or better than MySQL
5. Zero data loss during migration