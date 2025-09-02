-- PostgreSQL Schema Migration from MySQL
-- Generated automatically

-- Table: ai_inference_log
CREATE TABLE IF NOT EXISTS ai_inference_log (
id SERIAL PRIMARY KEY,
request_id VARCHAR(100) NOT NULL,
model_name VARCHAR(100) NOT NULL,
model_version VARCHAR(50),
input_data TEXT,
output_data TEXT,
inference_time_ms INTEGER,
confidence_score NUMERIC(5,4),
error_message TEXT,
is_successful BOOLEAN,
endpoint VARCHAR(255),
user_id VARCHAR(100),
session_id VARCHAR(100),
created_at TIMESTAMP,
cpu_usage NUMERIC(5,2),
memory_usage NUMERIC(10,2),
gpu_usage NUMERIC(5,2)
);

-- Table: ai_inference_logs
CREATE TABLE IF NOT EXISTS ai_inference_logs (
id SERIAL PRIMARY KEY,
inference_id VARCHAR(36) NOT NULL,
symbol VARCHAR(20) NOT NULL,
model_version VARCHAR(20) NOT NULL,
model_source VARCHAR(50) NOT NULL,
inference_start_time TIMESTAMP NOT NULL,
inference_end_time TIMESTAMP NOT NULL,
inference_duration_seconds REAL NOT NULL,
dataset_id VARCHAR(100),
environment VARCHAR(20),
error TEXT,
score INTEGER,
sentiment VARCHAR(20),
confidence INTEGER,
created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP
);

-- Table: alembic_version
CREATE TABLE IF NOT EXISTS alembic_version (
version_num VARCHAR(32) NOT NULL
);

-- Table: asset_details
CREATE TABLE IF NOT EXISTS asset_details (
id SERIAL PRIMARY KEY,
asset_code VARCHAR(50) NOT NULL,
description TEXT,
features TEXT,
specifications TEXT,
sector VARCHAR(100),
industry VARCHAR(100),
pe_ratio REAL,
pb_ratio REAL,
dividend_yield REAL,
beta REAL,
category VARCHAR(100),
subcategory VARCHAR(100),
tags TEXT,
source VARCHAR(100),
last_updated TIMESTAMP,
created_at TIMESTAMP NOT NULL,
updated_at TIMESTAMP NOT NULL
);

-- Table: asset_images
CREATE TABLE IF NOT EXISTS asset_images (
id SERIAL PRIMARY KEY,
asset_code VARCHAR(50) NOT NULL,
image_type enum('MAIN','THUMBNAIL','GALLERY','LOGO','CHART','GRAPH') NOT NULL,
url VARCHAR(512) NOT NULL,
alt_text TEXT,
width INTEGER,
height INTEGER,
title VARCHAR(255),
description TEXT,
source VARCHAR(100),
created_at TIMESTAMP NOT NULL,
updated_at TIMESTAMP NOT NULL
);

-- Table: asset_metrics
CREATE TABLE IF NOT EXISTS asset_metrics (
id SERIAL PRIMARY KEY,
asset_code VARCHAR(50) NOT NULL,
metric_type enum('SALES_RANK','POPULARITY_RANK','TRENDING_RANK','MARKET_CAP','VOLUME','PER','PBR','ROE','ROA','DEBT_RATIO','CIRCULATING_SUPPLY','MAX_SUPPLY','TOTAL_SUPPLY','RSI','MACD','BOLLINGER_BANDS','RATING','REVIEW_COUNT','RETURN_RATE') NOT NULL,
value REAL NOT NULL,
unit VARCHAR(50),
timestamp TIMESTAMP NOT NULL,
category VARCHAR(100),
description TEXT,
source VARCHAR(100),
confidence REAL
);

-- Table: asset_prices
CREATE TABLE IF NOT EXISTS asset_prices (
id SERIAL PRIMARY KEY,
asset_code VARCHAR(50) NOT NULL,
price_type enum('SPOT','CLOSE','OPEN','HIGH','LOW','BID','ASK','KEEPA_AMAZON','KEEPA_NEW','KEEPA_USED','KEEPA_COLLECTIBLE','KEEPA_REFURBISHED','KEEPA_LIGHTNING_DEAL','KEEPA_WAREHOUSE','BUYBOX','LIST_PRICE','SUGGESTED') NOT NULL,
price REAL NOT NULL,
currency VARCHAR(10),
timestamp TIMESTAMP NOT NULL,
volume REAL,
additional_value REAL,
source VARCHAR(100),
confidence REAL
);

-- Table: asset_reviews
CREATE TABLE IF NOT EXISTS asset_reviews (
id SERIAL PRIMARY KEY,
asset_code VARCHAR(50) NOT NULL,
reviewer_id VARCHAR(100),
reviewer_name VARCHAR(255),
rating REAL,
title VARCHAR(255),
content TEXT,
helpful_votes INTEGER,
total_votes INTEGER,
verified_purchase VARCHAR(10),
review_date TIMESTAMP,
created_at TIMESTAMP NOT NULL,
updated_at TIMESTAMP NOT NULL
);

-- Table: asset_statistics
CREATE TABLE IF NOT EXISTS asset_statistics (
id SERIAL PRIMARY KEY,
asset_code VARCHAR(50) NOT NULL,
total_reviews INTEGER,
average_rating REAL,
rating_distribution TEXT,
price_min REAL,
price_max REAL,
price_avg REAL,
price_volatility REAL,
monthly_sold INTEGER,
total_sold INTEGER,
return_rate REAL,
market_cap REAL,
volume_24h REAL,
pe_ratio REAL,
dividend_yield REAL,
last_calculated TIMESTAMP,
data_source VARCHAR(100),
created_at TIMESTAMP NOT NULL,
updated_at TIMESTAMP NOT NULL
);

-- Table: assets
CREATE TABLE IF NOT EXISTS assets (
id SERIAL PRIMARY KEY,
asset_code VARCHAR(50) NOT NULL,
asset_type VARCHAR(20) NOT NULL,
provider VARCHAR(50) NOT NULL,
name VARCHAR(512),
title VARCHAR(512),
description TEXT,
issuer VARCHAR(255),
brand VARCHAR(255),
manufacturer VARCHAR(255),
created_at TIMESTAMP NOT NULL,
updated_at TIMESTAMP NOT NULL,
product_type INTEGER,
domain_id INTEGER,
tracking_since INTEGER,
listed_since INTEGER,
last_update INTEGER,
last_rating_update INTEGER,
last_price_change INTEGER,
last_ebay_update INTEGER,
last_stock_update INTEGER,
currency VARCHAR(10),
market_cap REAL,
volume_24h REAL,
circulating_supply REAL,
max_supply REAL,
current_price REAL,
previous_close REAL,
price_change REAL,
price_change_percent REAL,
buybox_price REAL,
average_rating REAL,
review_count INTEGER,
monthly_sold INTEGER,
return_rate INTEGER,
competitive_price_threshold INTEGER,
suggested_lower_price INTEGER,
variable_closing_fee INTEGER,
referral_fee_percentage REAL,
package_height INTEGER,
package_length INTEGER,
package_width INTEGER,
package_weight INTEGER,
package_quantity INTEGER,
item_height INTEGER,
item_length INTEGER,
item_width INTEGER,
item_weight INTEGER,
number_of_items INTEGER,
number_of_pages INTEGER,
publication_date INTEGER,
release_date INTEGER,
availability_amazon INTEGER,
availability_amazon_delay_min INTEGER,
availability_amazon_delay_max INTEGER,
buy_box_eligible_offer_count_new_fba INTEGER,
buy_box_eligible_offer_count_new_fbm INTEGER,
buy_box_eligible_offer_count_used_fba INTEGER,
buy_box_eligible_offer_count_used_fbm INTEGER,
buy_box_eligible_offer_count_collectible_fba INTEGER,
buy_box_eligible_offer_count_collectible_fbm INTEGER,
buy_box_eligible_offer_count_refurbished_fba INTEGER,
buy_box_eligible_offer_count_refurbished_fbm INTEGER,
brand_store_name VARCHAR(255),
brand_store_url VARCHAR(512),
brand_store_url_name VARCHAR(255),
website_display_group VARCHAR(255),
website_display_group_name VARCHAR(255),
sales_rank_display_group VARCHAR(255),
product_group VARCHAR(255),
product_type_field VARCHAR(255),
part_number VARCHAR(255),
binding VARCHAR(255),
color VARCHAR(255),
size VARCHAR(255),
model VARCHAR(255),
coupon_one_time_discount INTEGER,
coupon_sns_discount INTEGER,
rental_details VARCHAR(512),
rental_seller_id VARCHAR(255),
new_price_is_map BOOLEAN,
is_eligible_for_trade_in BOOLEAN,
is_eligible_for_super_saver_shipping BOOLEAN,
is_redirect_asin BOOLEAN,
is_sns BOOLEAN,
is_adult_product BOOLEAN,
is_heat_sensitive BOOLEAN,
is_merch_on_demand BOOLEAN,
is_haul BOOLEAN,
launchpad BOOLEAN,
is_redirect_asin_flag BOOLEAN,
is_sns_flag BOOLEAN,
offers_successful BOOLEAN,
avg_volume REAL,
pe_ratio REAL,
forward_pe REAL,
price_to_book REAL,
dividend_yield REAL,
beta REAL,
fifty_two_week_high REAL,
fifty_two_week_low REAL,
fifty_day_average REAL,
two_hundred_day_average REAL,
company_name VARCHAR(512),
sector VARCHAR(255),
industry VARCHAR(255),
website VARCHAR(512),
business_summary TEXT,
employees INTEGER,
country VARCHAR(100),
exchange VARCHAR(50),
market_state VARCHAR(50),
quote_type VARCHAR(50),
pdr_latest_close REAL,
pdr_latest_open REAL,
pdr_latest_high REAL,
pdr_latest_low REAL,
pdr_latest_volume INTEGER,
pdr_data_points INTEGER,
pdr_date_range_start VARCHAR(20),
pdr_date_range_end VARCHAR(20),
data_sources JSONB,
last_data_update TIMESTAMP,
data_source_errors JSONB
);

-- Table: financial_news
CREATE TABLE IF NOT EXISTS financial_news (
id SERIAL PRIMARY KEY,
title VARCHAR(500) NOT NULL,
summary TEXT,
content TEXT,
category VARCHAR(50),
published_at TIMESTAMP,
source_url VARCHAR(500),
sentiment_score NUMERIC(3,2),
impact_score NUMERIC(3,2),
source VARCHAR(100),
created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP
);

-- Table: model_accuracy_evaluation
CREATE TABLE IF NOT EXISTS model_accuracy_evaluation (
id SERIAL PRIMARY KEY,
model_type VARCHAR(50),
symbol VARCHAR(20),
mae REAL,
prediction_count INTEGER,
avg_confidence REAL,
median_error REAL,
std_error REAL,
min_error REAL,
max_error REAL,
evaluation_date TIMESTAMP,
created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP
);

-- Table: model_performance
CREATE TABLE IF NOT EXISTS model_performance (
id SERIAL PRIMARY KEY,
model_type VARCHAR(50) NOT NULL,
model_version VARCHAR(20) NOT NULL,
mae REAL,
mse REAL,
rmse REAL,
accuracy REAL,
evaluation_start_date TIMESTAMP NOT NULL,
evaluation_end_date TIMESTAMP NOT NULL,
symbols_count INTEGER NOT NULL,
is_active BOOLEAN NOT NULL,
created_at TIMESTAMP NOT NULL,
updated_at TIMESTAMP NOT NULL
);

-- Table: prediction_history
CREATE TABLE IF NOT EXISTS prediction_history (
id SERIAL PRIMARY KEY,
symbol VARCHAR(20) NOT NULL,
date TIMESTAMP NOT NULL,
actual_price REAL,
actual_change REAL,
actual_change_percent REAL,
predicted_price_1d REAL,
predicted_price_7d REAL,
predicted_price_30d REAL,
accuracy_1d REAL,
accuracy_7d REAL,
accuracy_30d REAL,
created_at TIMESTAMP NOT NULL,
updated_at TIMESTAMP NOT NULL
);

-- Table: product_aplus_content
CREATE TABLE IF NOT EXISTS product_aplus_content (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
from_manufacturer BOOLEAN NOT NULL
);

-- Table: product_aplus_images
CREATE TABLE IF NOT EXISTS product_aplus_images (
id SERIAL PRIMARY KEY,
aplus_module_id INTEGER NOT NULL,
image_url VARCHAR(255),
image_alt_text VARCHAR(255)
);

-- Table: product_aplus_modules
CREATE TABLE IF NOT EXISTS product_aplus_modules (
id SERIAL PRIMARY KEY,
aplus_id INTEGER NOT NULL
);

-- Table: product_aplus_text
CREATE TABLE IF NOT EXISTS product_aplus_text (
id SERIAL PRIMARY KEY,
aplus_module_id INTEGER NOT NULL,
text_content TEXT
);

-- Table: product_aplus_videos
CREATE TABLE IF NOT EXISTS product_aplus_videos (
id SERIAL PRIMARY KEY,
aplus_module_id INTEGER NOT NULL,
video_url VARCHAR(255)
);

-- Table: product_buy_box_seller_history
CREATE TABLE IF NOT EXISTS product_buy_box_seller_history (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
keepa_time INTEGER,
seller_id VARCHAR(255)
);

-- Table: product_buy_box_used_history
CREATE TABLE IF NOT EXISTS product_buy_box_used_history (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
keepa_time INTEGER,
price INTEGER
);

-- Table: product_contributors
CREATE TABLE IF NOT EXISTS product_contributors (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
contributor_name VARCHAR(255) NOT NULL,
contributor_role VARCHAR(255)
);

-- Table: product_coupon_history
CREATE TABLE IF NOT EXISTS product_coupon_history (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
keepa_time INTEGER,
one_time_discount INTEGER,
sns_discount INTEGER
);

-- Table: product_csv_history
CREATE TABLE IF NOT EXISTS product_csv_history (
id SERIAL PRIMARY KEY,
product_asin VARCHAR(255) NOT NULL,
history_type enum('AMAZON','NEW','USED','SALES','LISTPRICE','COLLECTIBLE','REFURBISHED','NEW_FBM_SHIPPING','LIGHTNING_DEAL','WAREHOUSE','NEW_FBA','COUNT_NEW','COUNT_USED','COUNT_REFURBISHED','COUNT_COLLECTIBLE','EXTRA_INFO_UPDATES','RATING','COUNT_REVIEWS','BUY_BOX_SHIPPING','USED_NEW_SHIPPING','USED_VERY_GOOD_SHIPPING','USED_GOOD_SHIPPING','USED_ACCEPTABLE_SHIPPING','COLLECTIBLE_NEW_SHIPPING','COLLECTIBLE_VERY_GOOD_SHIPPING','COLLECTIBLE_GOOD_SHIPPING','COLLECTIBLE_ACCEPTABLE_SHIPPING','REFURBISHED_SHIPPING','EBAY_NEW_SHIPPING','EBAY_USED_SHIPPING','TRADE_IN','RENTAL','BUY_BOX_USED_SHIPPING','PRIME_EXCL') NOT NULL,
keepa_time INTEGER NOT NULL,
value INTEGER NOT NULL,
additional_value INTEGER
);

-- Table: product_details
CREATE TABLE IF NOT EXISTS product_details (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
title VARCHAR(512),
brand VARCHAR(255),
manufacturer VARCHAR(255),
description TEXT,
last_updated TIMESTAMP,
scent VARCHAR(255),
active_ingredients VARCHAR(512),
special_ingredients VARCHAR(512),
item_form VARCHAR(255),
item_type_keyword VARCHAR(255),
recommended_uses_for_product VARCHAR(512),
pattern VARCHAR(255),
safety_warning TEXT,
product_benefit TEXT,
target_audience_keyword VARCHAR(255),
style VARCHAR(255),
included_components VARCHAR(512),
material VARCHAR(255),
ingredients TEXT,
audience_rating VARCHAR(50),
url_slug VARCHAR(512),
formats TEXT,
languages TEXT,
specific_uses TEXT,
unit_count VARCHAR(255),
aplus_content TEXT,
related_asins TEXT,
sales_rank_reference TEXT
);

-- Table: product_ebay_listings
CREATE TABLE IF NOT EXISTS product_ebay_listings (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
ebay_listing_id BIGINT NOT NULL,
condition_type VARCHAR(50) NOT NULL
);

-- Table: product_fba_fees
CREATE TABLE IF NOT EXISTS product_fba_fees (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
last_update INTEGER,
pick_and_pack_fee INTEGER
);

-- Table: product_features
CREATE TABLE IF NOT EXISTS product_features (
id SERIAL PRIMARY KEY,
product_details_id INTEGER NOT NULL,
name VARCHAR(255) NOT NULL,
value VARCHAR(512)
);

-- Table: product_formats
CREATE TABLE IF NOT EXISTS product_formats (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
related_product_asin VARCHAR(255),
format_type VARCHAR(255)
);

-- Table: product_frequently_bought_together
CREATE TABLE IF NOT EXISTS product_frequently_bought_together (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
related_product_asin VARCHAR(255) NOT NULL
);

-- Table: product_hazardous_materials
CREATE TABLE IF NOT EXISTS product_hazardous_materials (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
raw_material_data TEXT
);

-- Table: product_identifiers
CREATE TABLE IF NOT EXISTS product_identifiers (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
identifier_type VARCHAR(50) NOT NULL,
identifier_value VARCHAR(255) NOT NULL
);

-- Table: product_images
CREATE TABLE IF NOT EXISTS product_images (
id SERIAL PRIMARY KEY,
asin VARCHAR(255) NOT NULL,
large_url VARCHAR(255),
large_height INTEGER,
large_width INTEGER,
medium_url VARCHAR(255),
medium_height INTEGER,
medium_width INTEGER
);

-- Table: product_languages
CREATE TABLE IF NOT EXISTS product_languages (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
language_name VARCHAR(255) NOT NULL,
language_type VARCHAR(255)
);

-- Table: product_live_offer_orders
CREATE TABLE IF NOT EXISTS product_live_offer_orders (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
ordered_asin VARCHAR(255),
order_index INTEGER
);

-- Table: product_monthly_sold_history
CREATE TABLE IF NOT EXISTS product_monthly_sold_history (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
keepa_time INTEGER,
sold_count INTEGER
);

-- Table: product_offers
CREATE TABLE IF NOT EXISTS product_offers (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
offer_id VARCHAR(255) NOT NULL,
seller_id INTEGER,
is_fba BOOLEAN,
is_new BOOLEAN,
price INTEGER,
shipping INTEGER,
total_price INTEGER,
created_at TIMESTAMP NOT NULL,
updated_at TIMESTAMP NOT NULL
);

-- Table: product_parent_asin_history
CREATE TABLE IF NOT EXISTS product_parent_asin_history (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
keepa_time INTEGER NOT NULL,
parent_asin VARCHAR(255) NOT NULL
);

-- Table: product_predictions
CREATE TABLE IF NOT EXISTS product_predictions (
id SERIAL PRIMARY KEY,
product_asin VARCHAR(255) NOT NULL,
prediction_type VARCHAR(50) NOT NULL,
predicted_value REAL NOT NULL,
created_at TIMESTAMP
);

-- Table: product_prices
CREATE TABLE IF NOT EXISTS product_prices (
id SERIAL PRIMARY KEY,
product_asin VARCHAR(255) NOT NULL,
history_type enum('AMAZON','NEW','USED','SALES','LISTPRICE','COLLECTIBLE','REFURBISHED','NEW_FBM_SHIPPING','LIGHTNING_DEAL','WAREHOUSE','NEW_FBA','COUNT_NEW','COUNT_USED','COUNT_REFURBISHED','COUNT_COLLECTIBLE','EXTRA_INFO_UPDATES','RATING','COUNT_REVIEWS','BUY_BOX_SHIPPING','USED_NEW_SHIPPING','USED_VERY_GOOD_SHIPPING','USED_GOOD_SHIPPING','USED_ACCEPTABLE_SHIPPING','COLLECTIBLE_NEW_SHIPPING','COLLECTIBLE_VERY_GOOD_SHIPPING','COLLECTIBLE_GOOD_SHIPPING','COLLECTIBLE_ACCEPTABLE_SHIPPING','REFURBISHED_SHIPPING','EBAY_NEW_SHIPPING','EBAY_USED_SHIPPING','TRADE_IN','RENTAL','BUY_BOX_USED_SHIPPING','PRIME_EXCL') NOT NULL,
time TIMESTAMP NOT NULL,
price INTEGER NOT NULL,
additional_value INTEGER
);

-- Table: product_promotions
CREATE TABLE IF NOT EXISTS product_promotions (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
type VARCHAR(255),
amount INTEGER,
discount_percent INTEGER,
sns_bulk_discount_percent INTEGER
);

-- Table: product_rental_price_history
CREATE TABLE IF NOT EXISTS product_rental_price_history (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
keepa_time INTEGER,
price INTEGER
);

-- Table: product_reviews
CREATE TABLE IF NOT EXISTS product_reviews (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
review_id VARCHAR(255) NOT NULL,
rating INTEGER,
title VARCHAR(255),
text TEXT,
review_time TIMESTAMP
);

-- Table: product_sales_rank_history_entries
CREATE TABLE IF NOT EXISTS product_sales_rank_history_entries (
id SERIAL PRIMARY KEY,
product_sales_rank_id INTEGER NOT NULL,
keepa_time INTEGER NOT NULL,
time TIMESTAMP NOT NULL
);

-- Table: product_sales_rank_reference_history
CREATE TABLE IF NOT EXISTS product_sales_rank_reference_history (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
keepa_time INTEGER,
sales_rank INTEGER,
rank INTEGER,
category VARCHAR(255)
);

-- Table: product_sales_rank_references
CREATE TABLE IF NOT EXISTS product_sales_rank_references (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
sales_rank INTEGER,
rank INTEGER,
category VARCHAR(255)
);

-- Table: product_sales_ranks
CREATE TABLE IF NOT EXISTS product_sales_ranks (
id SERIAL PRIMARY KEY,
asin VARCHAR(255) NOT NULL,
category_id BIGINT NOT NULL,
rank INTEGER,
updated_at TIMESTAMP NOT NULL
);

-- Table: product_specific_uses
CREATE TABLE IF NOT EXISTS product_specific_uses (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
use_value VARCHAR(255) NOT NULL
);

-- Table: product_statistics
CREATE TABLE IF NOT EXISTS product_statistics (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
raw_stats_data TEXT
);

-- Table: product_unit_count
CREATE TABLE IF NOT EXISTS product_unit_count (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
unit_value REAL,
unit_type VARCHAR(255)
);

-- Table: product_variations
CREATE TABLE IF NOT EXISTS product_variations (
id SERIAL PRIMARY KEY,
parent_product_id INTEGER NOT NULL,
variation_product_id INTEGER NOT NULL
);

-- Table: product_videos
CREATE TABLE IF NOT EXISTS product_videos (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
title VARCHAR(255),
image VARCHAR(255),
duration INTEGER,
creator VARCHAR(255),
name VARCHAR(255),
url VARCHAR(255)
);

-- Table: products
CREATE TABLE IF NOT EXISTS products (
id SERIAL PRIMARY KEY,
asin VARCHAR(10) NOT NULL,
title VARCHAR(512),
brand VARCHAR(255),
manufacturer VARCHAR(255),
created_at TIMESTAMP NOT NULL,
updated_at TIMESTAMP NOT NULL,
product_type INTEGER,
domain_id INTEGER,
tracking_since INTEGER,
listed_since INTEGER,
last_update INTEGER,
last_rating_update INTEGER,
last_price_change INTEGER,
last_ebay_update INTEGER,
last_stock_update INTEGER,
brand_store_name VARCHAR(255),
brand_store_url VARCHAR(512),
brand_store_url_name VARCHAR(255),
website_display_group VARCHAR(255),
website_display_group_name VARCHAR(255),
sales_rank_display_group VARCHAR(255),
product_group VARCHAR(255),
product_type_field VARCHAR(255),
part_number VARCHAR(255),
buybox_price REAL,
average_rating REAL,
review_count INTEGER,
number_of_items INTEGER,
number_of_pages INTEGER,
publication_date INTEGER,
release_date INTEGER,
package_height INTEGER,
package_length INTEGER,
package_width INTEGER,
package_weight INTEGER,
availability_amazon INTEGER,
availability_amazon_delay_min INTEGER,
availability_amazon_delay_max INTEGER,
buy_box_eligible_offer_count_new_fba INTEGER,
buy_box_eligible_offer_count_new_fbm INTEGER,
buy_box_eligible_offer_count_used_fba INTEGER,
buy_box_eligible_offer_count_used_fbm INTEGER,
buy_box_eligible_offer_count_collectible_fba INTEGER,
buy_box_eligible_offer_count_collectible_fbm INTEGER,
buy_box_eligible_offer_count_refurbished_fba INTEGER,
buy_box_eligible_offer_count_refurbished_fbm INTEGER,
competitive_price_threshold INTEGER,
suggested_lower_price INTEGER,
return_rate INTEGER,
variable_closing_fee INTEGER,
referral_fee_percentage REAL,
binding VARCHAR(255),
color VARCHAR(255),
size VARCHAR(255),
model VARCHAR(255),
monthly_sold INTEGER,
coupon_one_time_discount INTEGER,
coupon_sns_discount INTEGER,
rental_details VARCHAR(512),
rental_seller_id VARCHAR(255),
package_quantity INTEGER,
item_height INTEGER,
item_length INTEGER,
item_width INTEGER,
item_weight INTEGER,
new_price_is_map BOOLEAN,
is_eligible_for_trade_in BOOLEAN,
is_eligible_for_super_saver_shipping BOOLEAN,
is_redirect_asin BOOLEAN,
is_sns BOOLEAN,
is_adult_product BOOLEAN,
is_heat_sensitive BOOLEAN,
is_merch_on_demand BOOLEAN,
is_haul BOOLEAN,
launchpad BOOLEAN
);

-- Table: sales_rank_categories
CREATE TABLE IF NOT EXISTS sales_rank_categories (
id SERIAL PRIMARY KEY,
category_id BIGINT NOT NULL,
category_path VARCHAR(255),
parent_category_id BIGINT,
is_root BOOLEAN NOT NULL
);

-- Table: sellers
CREATE TABLE IF NOT EXISTS sellers (
id SERIAL PRIMARY KEY,
seller_id VARCHAR(255),
seller_name VARCHAR(255),
is_authenticated_seller BOOLEAN
);

-- Table: stock_aliases
CREATE TABLE IF NOT EXISTS stock_aliases (
id SERIAL PRIMARY KEY,
symbol VARCHAR(20),
alias VARCHAR(100) NOT NULL,
alias_type enum('company_name','abbreviation','nickname'),
created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP
);

-- Table: stock_master
CREATE TABLE IF NOT EXISTS stock_master (
symbol VARCHAR(20) NOT NULL,
name VARCHAR(300),
exchange VARCHAR(100),
market VARCHAR(50),
sector VARCHAR(150),
industry VARCHAR(150),
country VARCHAR(100),
website VARCHAR(255),
description TEXT,
is_active BOOLEAN  DEFAULT 1,
created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,
currency VARCHAR(10)
);

-- Table: stock_prediction
CREATE TABLE IF NOT EXISTS stock_prediction (
symbol VARCHAR(32) NOT NULL,
predicted_value REAL,
predicted_at TIMESTAMP
);

-- Table: stock_predictions
CREATE TABLE IF NOT EXISTS stock_predictions (
id SERIAL PRIMARY KEY,
symbol VARCHAR(20) NOT NULL,
prediction_date TIMESTAMP NOT NULL,
created_at TIMESTAMP NOT NULL,
predicted_price REAL NOT NULL,
predicted_change REAL,
predicted_change_percent REAL,
confidence_score REAL,
model_type VARCHAR(50) NOT NULL,
model_version VARCHAR(20),
prediction_horizon INTEGER NOT NULL,
is_active BOOLEAN NOT NULL,
is_accurate BOOLEAN,
notes TEXT
);

-- Table: stock_price_history
CREATE TABLE IF NOT EXISTS stock_price_history (
id SERIAL PRIMARY KEY,
symbol VARCHAR(20) NOT NULL,
date TIMESTAMP NOT NULL,
open_price REAL,
high_price REAL,
low_price REAL,
close_price REAL NOT NULL,
volume INTEGER,
adjusted_close REAL,
data_source VARCHAR(50) NOT NULL DEFAULT yfinance,
is_valid BOOLEAN NOT NULL DEFAULT 1,
data_quality_score REAL,
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: stock_price_snapshots
CREATE TABLE IF NOT EXISTS stock_price_snapshots (
id SERIAL PRIMARY KEY,
symbol VARCHAR(20) NOT NULL,
timestamp TIMESTAMP NOT NULL,
current_price REAL NOT NULL,
price_change REAL,
price_change_percent REAL,
volume INTEGER,
data_source VARCHAR(50) NOT NULL DEFAULT yfinance,
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: stock_prices
CREATE TABLE IF NOT EXISTS stock_prices (
id SERIAL PRIMARY KEY,
symbol VARCHAR(20) NOT NULL,
date date NOT NULL,
open_price NUMERIC(10,2),
high_price NUMERIC(10,2),
low_price NUMERIC(10,2),
close_price NUMERIC(10,2),
volume BIGINT,
created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP
);

-- Table: variation_attributes
CREATE TABLE IF NOT EXISTS variation_attributes (
id SERIAL PRIMARY KEY,
product_id INTEGER NOT NULL,
dimension VARCHAR(255) NOT NULL,
value VARCHAR(255) NOT NULL
);
