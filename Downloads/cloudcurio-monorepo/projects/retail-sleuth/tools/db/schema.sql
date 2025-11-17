CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS retailers (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    name text NOT NULL,
    slug text UNIQUE NOT NULL,
    base_url text NOT NULL,
    robots_txt_url text,
    strategy text NOT NULL DEFAULT 'rest',
    rate_limit_per_minute integer NOT NULL DEFAULT 30,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS items (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    retailer_id uuid NOT NULL REFERENCES retailers(id),
    sku text,
    name text NOT NULL,
    category text,
    image_url text,
    raw_metadata jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS item_prices (
    id bigserial PRIMARY KEY,
    item_id uuid NOT NULL REFERENCES items(id),
    retailer_id uuid NOT NULL REFERENCES retailers(id),
    price numeric(12,2) NOT NULL,
    currency char(3) NOT NULL,
    availability text,
    collected_at timestamptz NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_item_prices_item_time
    ON item_prices (item_id, collected_at DESC);

CREATE TABLE IF NOT EXISTS crawl_jobs (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    retailer_id uuid NOT NULL REFERENCES retailers(id),
    status text NOT NULL,
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    error_message text
);
