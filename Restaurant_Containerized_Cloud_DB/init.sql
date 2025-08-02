-- Restaurant Menu System v3.0 - Database Initialization Script
-- This script initializes the PostgreSQL database with required extensions and initial data

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create database user (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'restaurant_user') THEN
        CREATE USER restaurant_user WITH PASSWORD 'secure_password_123';
    END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE restaurant_db TO restaurant_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO restaurant_user;

-- Create initial categories
INSERT INTO categories (name, description, is_active, created_at) VALUES
('Appetizers', 'Start your meal with our delicious appetizers', true, NOW()),
('Main Course', 'Our signature main dishes', true, NOW()),
('Desserts', 'Sweet endings to your meal', true, NOW()),
('Beverages', 'Refreshing drinks and beverages', true, NOW()),
('Salads', 'Fresh and healthy salad options', true, NOW())
ON CONFLICT DO NOTHING;

-- Create sample delivery drivers
INSERT INTO delivery_drivers (name, phone, email, vehicle_number, is_available, current_location, rating, created_at) VALUES
('John Smith', '+1234567890', 'john.smith@delivery.com', 'DL-001', true, 'Downtown', 4.5, NOW()),
('Sarah Johnson', '+1234567891', 'sarah.johnson@delivery.com', 'DL-002', true, 'Uptown', 4.8, NOW()),
('Mike Wilson', '+1234567892', 'mike.wilson@delivery.com', 'DL-003', true, 'Midtown', 4.2, NOW())
ON CONFLICT DO NOTHING;

-- Create sample restaurants
INSERT INTO restaurants (name, description, address, phone, email, cuisine_type, rating, is_active, delivery_fee, minimum_order, created_at) VALUES
('Pizza Palace', 'Authentic Italian pizza and pasta', '123 Main St, Downtown', '+1234567890', 'info@pizzapalace.com', 'Italian', 4.5, true, 3.50, 15.00, NOW()),
('Burger House', 'Gourmet burgers and fries', '456 Oak Ave, Uptown', '+1234567891', 'info@burgerhouse.com', 'American', 4.3, true, 2.50, 12.00, NOW()),
('Sushi Express', 'Fresh sushi and Japanese cuisine', '789 Pine St, Midtown', '+1234567892', 'info@sushiexpress.com', 'Japanese', 4.7, true, 4.00, 20.00, NOW()),
('Taco Fiesta', 'Authentic Mexican tacos and burritos', '321 Elm St, Downtown', '+1234567893', 'info@tacofiesta.com', 'Mexican', 4.4, true, 2.00, 10.00, NOW()),
('Green Garden', 'Healthy vegetarian and vegan options', '654 Maple Dr, Uptown', '+1234567894', 'info@greengarden.com', 'Vegetarian', 4.6, true, 3.00, 18.00, NOW())
ON CONFLICT DO NOTHING;

-- Create sample menu items for Pizza Palace
INSERT INTO menu_items (name, description, price, image_url, is_available, preparation_time, calories, restaurant_id, category_id, created_at) VALUES
('Margherita Pizza', 'Classic tomato sauce with mozzarella cheese', 18.99, 'https://example.com/margherita.jpg', true, 20, 850, 1, 2, NOW()),
('Pepperoni Pizza', 'Spicy pepperoni with melted cheese', 22.99, 'https://example.com/pepperoni.jpg', true, 25, 950, 1, 2, NOW()),
('Garlic Bread', 'Fresh garlic bread with herbs', 6.99, 'https://example.com/garlic-bread.jpg', true, 10, 250, 1, 1, NOW()),
('Caesar Salad', 'Fresh romaine lettuce with caesar dressing', 12.99, 'https://example.com/caesar-salad.jpg', true, 15, 320, 1, 5, NOW()),
('Tiramisu', 'Classic Italian dessert', 8.99, 'https://example.com/tiramisu.jpg', true, 5, 450, 1, 3, NOW())
ON CONFLICT DO NOTHING;

-- Create sample menu items for Burger House
INSERT INTO menu_items (name, description, price, image_url, is_available, preparation_time, calories, restaurant_id, category_id, created_at) VALUES
('Classic Burger', 'Beef patty with lettuce, tomato, and cheese', 14.99, 'https://example.com/classic-burger.jpg', true, 15, 650, 2, 2, NOW()),
('Bacon Cheeseburger', 'Beef patty with bacon and cheese', 17.99, 'https://example.com/bacon-burger.jpg', true, 18, 750, 2, 2, NOW()),
('French Fries', 'Crispy golden fries', 4.99, 'https://example.com/fries.jpg', true, 8, 350, 2, 1, NOW()),
('Onion Rings', 'Crispy onion rings', 5.99, 'https://example.com/onion-rings.jpg', true, 10, 280, 2, 1, NOW()),
('Chocolate Shake', 'Rich chocolate milkshake', 6.99, 'https://example.com/chocolate-shake.jpg', true, 5, 420, 2, 4, NOW())
ON CONFLICT DO NOTHING;

-- Create sample menu items for Sushi Express
INSERT INTO menu_items (name, description, price, image_url, is_available, preparation_time, calories, restaurant_id, category_id, created_at) VALUES
('California Roll', 'Crab, avocado, and cucumber', 12.99, 'https://example.com/california-roll.jpg', true, 12, 280, 3, 2, NOW()),
('Salmon Nigiri', 'Fresh salmon over rice', 8.99, 'https://example.com/salmon-nigiri.jpg', true, 8, 180, 3, 2, NOW()),
('Miso Soup', 'Traditional Japanese soup', 4.99, 'https://example.com/miso-soup.jpg', true, 5, 120, 3, 1, NOW()),
('Edamame', 'Steamed soybeans with salt', 5.99, 'https://example.com/edamame.jpg', true, 3, 150, 3, 1, NOW()),
('Green Tea Ice Cream', 'Refreshing green tea dessert', 6.99, 'https://example.com/green-tea-ice-cream.jpg', true, 2, 200, 3, 3, NOW())
ON CONFLICT DO NOTHING;

-- Create sample users
INSERT INTO users (email, username, hashed_password, full_name, phone, is_active, is_superuser, created_at) VALUES
('admin@restaurant.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8e', 'System Administrator', '+1234567890', true, true, NOW()),
('john.doe@example.com', 'johndoe', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8e', 'John Doe', '+1234567891', true, false, NOW()),
('jane.smith@example.com', 'janesmith', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8e', 'Jane Smith', '+1234567892', true, false, NOW())
ON CONFLICT DO NOTHING;

-- Update sequences to avoid conflicts
SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories));
SELECT setval('restaurants_id_seq', (SELECT MAX(id) FROM restaurants));
SELECT setval('menu_items_id_seq', (SELECT MAX(id) FROM menu_items));
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('delivery_drivers_id_seq', (SELECT MAX(id) FROM delivery_drivers));

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_restaurant_id ON orders(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_menu_items_restaurant_id ON menu_items(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_menu_items_category_id ON menu_items(category_id);
CREATE INDEX IF NOT EXISTS idx_reviews_restaurant_id ON reviews(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_delivery_drivers_available ON delivery_drivers(is_available);

-- Grant permissions to restaurant_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO restaurant_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO restaurant_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO restaurant_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO restaurant_user; 