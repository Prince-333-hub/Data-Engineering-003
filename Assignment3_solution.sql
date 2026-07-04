CREATE DATABASE IF NOT EXISTS superstore_analysis;
USE superstore_analysis;
SELECT * FROM superstore_raw LIMIT 5;
CREATE TABLE IF NOT EXISTS customers AS
SELECT DISTINCT 
    `Customer ID` AS customer_id, 
    `Customer Name` AS customer_name, 
    `Segment` AS segment
FROM superstore_raw;
CREATE TABLE IF NOT EXISTS products AS
SELECT DISTINCT 
    `Product ID` AS product_id, 
    `Category` AS category, 
    `Sub-Category` AS sub_category, 
    `Product Name` AS product_name
FROM superstore_raw;
CREATE TABLE IF NOT EXISTS orders AS
SELECT DISTINCT 
    `Order ID` AS order_id, 
    `Customer ID` AS customer_id, 
    `Product ID` AS product_id, 
    STR_TO_DATE(`Order Date`, '%m/%d/%Y') AS order_date,
    `Sales` AS sales, 
    `Quantity` AS quantity
FROM superstore_raw;
SELECT order_id, customer_id, sales 
FROM orders 
WHERE sales > (SELECT AVG(sales) FROM orders);
WITH CustomerSales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, cs.total_sales
FROM CustomerSales cs
JOIN customers c ON cs.customer_id = c.customer_id;
WITH CustomerRankingCTE AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT 
    c.customer_name, 
    cr.total_sales,
    RANK() OVER (ORDER BY cr.total_sales DESC) AS sales_rank,
    ROW_NUMBER() OVER (ORDER BY cr.total_sales DESC) AS row_num
FROM CustomerRankingCTE cr
JOIN customers c ON cr.customer_id = c.customer_id;
SELECT customer_id, COUNT(DISTINCT order_id) AS total_orders
FROM orders
GROUP BY customer_id
HAVING total_orders = 1;