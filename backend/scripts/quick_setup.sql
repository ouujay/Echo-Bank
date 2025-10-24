-- Quick setup script to insert test data
-- PIN for test user is: 1234

-- Insert test user
INSERT INTO users (account_number, full_name, email, phone, pin_hash, balance, daily_limit, is_active)
VALUES ('0123456789', 'Test User', 'test@echobank.com', '+2348012345678',
        '$2b$12$2ocHity4eVeFN.eXS6n8zONrnSfOJngXDx3QeJ3bmGrm12DXUWbfm',
        100000.00, 50000.00, true);

-- Insert test recipients
INSERT INTO recipients (user_id, name, account_number, bank_name, bank_code, is_favorite)
VALUES
    (1, 'John Okafor', '0111111111', 'Zenith Bank', '057', false),
    (1, 'John Adeyemi', '0222222222', 'GTBank', '058', false),
    (1, 'Mary Johnson', '0333333333', 'Access Bank', '044', false),
    (1, 'David Brown', '0444444444', 'First Bank', '011', false);

-- Verify inserts
SELECT 'User created:' as info, account_number, full_name, balance FROM users;
SELECT 'Recipients created:' as info, name, bank_name FROM recipients;
