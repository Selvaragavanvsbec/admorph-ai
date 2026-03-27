CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    product VARCHAR(255) NOT NULL,
    audience VARCHAR(255) NOT NULL,
    goal VARCHAR(255) NOT NULL,
    platform VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ad_variants (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    headline VARCHAR(255) NOT NULL,
    cta VARCHAR(128) NOT NULL,
    layout VARCHAR(64) NOT NULL,
    visual_theme VARCHAR(128) NOT NULL,
    score FLOAT NOT NULL,
    image_path TEXT
);
