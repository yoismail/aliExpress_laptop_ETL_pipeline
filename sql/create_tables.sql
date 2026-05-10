
CREATE TABLE IF NOT EXISTS laptops (
    -- Primary Key
    laptop_id SERIAL PRIMARY KEY,

    -- Product Details
    product_name VARCHAR(500) NOT NULL,
    product_price NUMERIC(10, 2) NOT NULL,
    was_price NUMERIC(10, 2) DEFAULT 0.00,

    -- Discount Details
    discount_amount NUMERIC(10, 2) DEFAULT 0.00,
    discount_percentage NUMERIC(5, 1) DEFAULT 0.0,

    -- Boolean Flags
    is_on_sale BOOLEAN  DEFAULT FALSE,
    is_free_shipping BOOLEAN  DEFAULT FALSE,
    is_top_seller BOOLEAN  DEFAULT FALSE,

    -- Categorisation
    price_band VARCHAR(20) CHECK (price_band IN ('Budget', 'Mid-Range','Upper-Mid','Premium', 'Luxury')),

    -- Metadata
    scraped_at TIMESTAMPTZ DEFAULT NOW() 
);