-- Pricing Analysis

-- What is the average laptop price by price band?
SELECT price_band, ROUND(AVG(product_price), 2) AS avg_price
FROM laptops
GROUP BY price_band
ORDER BY avg_price;

-- What are the top 10 most expensive laptops?
SELECT product_name, product_price
FROM laptops
ORDER BY product_price DESC
LIMIT 10;

-- What are the top 10 cheapest laptops?
SELECT product_name, product_price
FROM laptops
ORDER BY product_price ASC
LIMIT 10;


-- Discount Analysis

-- Which laptops have the highest discount percentage?
SELECT product_name, product_price, was_price, discount_percentage
FROM laptops
WHERE is_on_sale = TRUE
ORDER BY discount_percentage DESC
LIMIT 10;

-- What is the average discount percentage per price band?
SELECT price_band, ROUND(AVG(discount_percentage), 1) AS avg_discount
FROM laptops
WHERE is_on_sale = TRUE
GROUP BY price_band
ORDER BY avg_discount DESC;

-- How many laptops are currently on sale?
SELECT
    COUNT(*) FILTER (WHERE is_on_sale = TRUE)  AS on_sale,
    COUNT(*) FILTER (WHERE is_on_sale = FALSE) AS full_price,
    COUNT(*)                                   AS total
FROM laptops;


-- Shipping Analysis

-- What percentage of laptops offer free shipping?
SELECT
    ROUND(COUNT(*) FILTER (WHERE is_free_shipping = TRUE) * 100.0 / COUNT(*), 1) AS free_shipping_pct
FROM laptops;

-- Do free shipping laptops tend to cost more or less?
SELECT
    is_free_shipping,
    ROUND(AVG(product_price), 2) AS avg_price,
    COUNT(*) AS total
FROM laptops
GROUP BY is_free_shipping;


-- Top Seller Analysis

-- How many top sellers are in each price band?
SELECT price_band, COUNT(*) AS top_sellers
FROM laptops
WHERE is_top_seller = TRUE
GROUP BY price_band
ORDER BY top_sellers DESC;

-- Are top sellers more likely to be on sale?
SELECT
    is_top_seller,
    ROUND(AVG(discount_percentage), 1) AS avg_discount,
    COUNT(*) AS total
FROM laptops
GROUP BY is_top_seller;


-- Value Analysis

-- Best value laptops — high discount, low price, free shipping
SELECT product_name, product_price, discount_percentage
FROM laptops
WHERE is_free_shipping = TRUE
AND is_on_sale = TRUE
AND price_band IN ('Budget', 'Mid-Range')
ORDER BY discount_percentage DESC
LIMIT 10;

-- What price band has the most laptops?
SELECT price_band, COUNT(*) AS total
FROM laptops
GROUP BY price_band
ORDER BY total DESC;