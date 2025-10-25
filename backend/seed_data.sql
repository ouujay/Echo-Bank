-- Seed data for Demo Bank
-- Connect to demo_bank database
\c demo_bank;

-- Test User 1: John Doe
-- Password: password123
-- PIN: 1234
INSERT INTO bank_users (email, phone, full_name, bvn, password_hash, pin_hash, is_verified)
VALUES (
    'john@demo.com',
    '+2348012345678',
    'John Doe',
    '12345678901',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEg1u.',  -- password123
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',  -- 1234
    TRUE
);

-- Test User 2: Sarah Bello
-- Password: password123
-- PIN: 5678
INSERT INTO bank_users (email, phone, full_name, bvn, password_hash, pin_hash, is_verified)
VALUES (
    'sarah@demo.com',
    '+2348087654321',
    'Sarah Bello',
    '10987654321',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEg1u.',  -- password123
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  -- 5678
    TRUE
);

-- Create accounts for John Doe
INSERT INTO bank_accounts (user_id, account_number, account_name, account_type, balance)
VALUES
(1, '0123456789', 'John Doe', 'savings', 100000.00),
(1, '0123456790', 'John Doe Current', 'current', 50000.00);

-- Create account for Sarah Bello
INSERT INTO bank_accounts (user_id, account_number, account_name, account_type, balance)
VALUES (2, '0987654321', 'Sarah Bello', 'savings', 75000.00);

-- Add Sarah as a recipient for John
INSERT INTO bank_recipients (user_id, recipient_name, account_number, bank_name, bank_code, is_favorite, is_verified)
VALUES (
    1,
    'Sarah Bello',
    '0987654321',
    'Demo Bank',
    '999',  -- Demo bank code
    TRUE,
    TRUE
);

-- Add test recipient for John (external bank)
INSERT INTO bank_recipients (user_id, recipient_name, account_number, bank_name, bank_code, is_favorite, is_verified)
VALUES (
    1,
    'Mary Johnson',
    '0111222333',
    'GTBank',
    '058',
    FALSE,
    FALSE
);

-- Create a sample completed transaction
INSERT INTO bank_transactions (
    account_id,
    transaction_ref,
    transaction_type,
    amount,
    fee,
    recipient_id,
    recipient_account,
    recipient_name,
    recipient_bank_name,
    status,
    narration,
    initiated_via,
    completed_at
)
VALUES (
    1,
    'TXN' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '001',
    'transfer',
    5000.00,
    10.00,
    1,
    '0987654321',
    'Sarah Bello',
    'Demo Bank',
    'completed',
    'Lunch money',
    'app',
    NOW() - INTERVAL '2 days'
);

-- Create a sample credit transaction
INSERT INTO bank_transactions (
    account_id,
    transaction_ref,
    transaction_type,
    amount,
    status,
    narration,
    initiated_via,
    completed_at
)
VALUES (
    1,
    'TXN' || TO_CHAR(NOW(), 'YYYYMMDDHH24MISS') || '002',
    'credit',
    20000.00,
    'completed',
    'Salary payment',
    'app',
    NOW() - INTERVAL '5 days'
);

SELECT 'Seed data inserted successfully!' AS message;
SELECT 'Test Users:' AS info;
SELECT email, phone, full_name FROM bank_users;
SELECT 'Test Accounts:' AS info;
SELECT account_number, account_name, balance FROM bank_accounts;
