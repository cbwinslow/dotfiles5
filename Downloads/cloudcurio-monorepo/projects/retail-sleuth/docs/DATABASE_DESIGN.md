# DATABASE DESIGN

## retailers

- id (uuid, pk)
- name (text)
- slug (text, unique)
- base_url (text)
- robots_txt_url (text, nullable)
- strategy (text) -- 'rest' | 'html' | 'mixed'
- rate_limit_per_minute (int)
- created_at (timestamptz)
- updated_at (timestamptz)

## items

- id (uuid, pk)
- retailer_id (uuid, fk -> retailers.id)
- sku (text)
- name (text)
- category (text)
- image_url (text)
- raw_metadata (jsonb)
- created_at (timestamptz)
- updated_at (timestamptz)

## item_prices

- id (bigserial, pk)
- item_id (uuid, fk -> items.id)
- retailer_id (uuid, fk -> retailers.id)
- price (numeric(12,2))
- currency (char(3))
- availability (text)
- collected_at (timestamptz indexed)

## crawl_jobs

- id (uuid, pk)
- retailer_id (uuid, fk)
- status (text) -- 'pending' | 'running' | 'success' | 'failed'
- started_at (timestamptz)
- finished_at (timestamptz)
- error_message (text)
