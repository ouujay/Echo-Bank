-- Demo Bank Database Schema
-- Drop existing database and create fresh
DROP DATABASE IF EXISTS demo_bank;
CREATE DATABASE demo_bank;

-- Connect to demo_bank database
\c demo_bank;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: bank_users
CREATE TABLE bank_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    bvn VARCHAR(11),  -- Bank Verification Number (Nigerian ID)
    password_hash VARCHAR(255) NOT NULL,
    pin_hash VARCHAR(255) NOT NULL,  -- 4-digit transaction PIN
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    pin_attempts INTEGER DEFAULT 0,
    pin_locked_until TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for bank_users
CREATE INDEX idx_bank_users_email ON bank_users(email);
CREATE INDEX idx_bank_users_phone ON bank_users(phone);

-- Table: bank_accounts
CREATE TABLE bank_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES bank_users(id) ON DELETE CASCADE,
    account_number VARCHAR(10) UNIQUE NOT NULL,  -- NUBAN format
    account_name VARCHAR(255) NOT NULL,  -- Account holder name
    account_type VARCHAR(20) DEFAULT 'savings',  -- savings, current
    balance NUMERIC(15, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'NGN',
    daily_transfer_limit NUMERIC(15, 2) DEFAULT 50000.00,  -- ₦50,000
    monthly_transfer_limit NUMERIC(15, 2) DEFAULT 500000.00,  -- ₦500,000
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for bank_accounts
CREATE INDEX idx_bank_accounts_user_id ON bank_accounts(user_id);
CREATE UNIQUE INDEX idx_bank_accounts_number ON bank_accounts(account_number);

-- Table: bank_recipients
CREATE TABLE bank_recipients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES bank_users(id) ON DELETE CASCADE,
    recipient_name VARCHAR(255) NOT NULL,
    account_number VARCHAR(10) NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    bank_code VARCHAR(10) NOT NULL,  -- Nigerian bank code (e.g., 058 for GTBank)
    paystack_recipient_code VARCHAR(100),  -- Paystack transfer recipient code
    is_favorite BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,  -- Verified via Paystack name enquiry
    last_transfer_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for bank_recipients
CREATE INDEX idx_bank_recipients_user_id ON bank_recipients(user_id);
CREATE INDEX idx_bank_recipients_favorite ON bank_recipients(user_id, is_favorite);

-- Table: bank_transactions
CREATE TABLE bank_transactions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES bank_accounts(id),
    transaction_ref VARCHAR(50) UNIQUE NOT NULL,  -- Internal reference
    transaction_type VARCHAR(20) NOT NULL,  -- debit, credit, transfer
    amount NUMERIC(15, 2) NOT NULL,
    fee NUMERIC(10, 2) DEFAULT 0.00,  -- Transfer fee
    currency VARCHAR(3) DEFAULT 'NGN',

    -- For transfers
    recipient_id INTEGER REFERENCES bank_recipients(id),
    recipient_account VARCHAR(10),
    recipient_name VARCHAR(255),
    recipient_bank_name VARCHAR(100),
    recipient_bank_code VARCHAR(10),

    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending',  -- pending_pin, pending_confirmation, processing, completed, failed, cancelled
    narration TEXT,

    -- Paystack integration
    paystack_transfer_code VARCHAR(100),  -- Paystack transfer reference
    paystack_transfer_id VARCHAR(100),
    paystack_status VARCHAR(50),

    -- Timestamps
    initiated_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    failed_at TIMESTAMP NULL,

    -- Failure tracking
    failure_reason TEXT,

    -- Voice/session tracking
    session_id VARCHAR(100),  -- Links to EchoBank session
    initiated_via VARCHAR(20) DEFAULT 'app',  -- app, voice, ussd, web

    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for bank_transactions
CREATE INDEX idx_bank_transactions_account_id ON bank_transactions(account_id);
CREATE INDEX idx_bank_transactions_status ON bank_transactions(status);
CREATE INDEX idx_bank_transactions_ref ON bank_transactions(transaction_ref);
CREATE INDEX idx_bank_transactions_paystack ON bank_transactions(paystack_transfer_code);
CREATE INDEX idx_bank_transactions_date ON bank_transactions(created_at DESC);

-- Table: paystack_transfers
CREATE TABLE paystack_transfers (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES bank_transactions(id),
    transfer_code VARCHAR(100) UNIQUE NOT NULL,  -- Paystack transfer code
    transfer_id VARCHAR(100),  -- Paystack transfer ID
    recipient_code VARCHAR(100),  -- Paystack recipient code
    amount NUMERIC(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    status VARCHAR(50),  -- pending, success, failed, reversed
    reason TEXT,  -- Transfer description

    -- Paystack response data
    paystack_response JSONB,  -- Full Paystack API response

    -- Webhook tracking
    webhook_received BOOLEAN DEFAULT FALSE,
    webhook_at TIMESTAMP NULL,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for paystack_transfers
CREATE INDEX idx_paystack_transfers_transaction_id ON paystack_transfers(transaction_id);
CREATE UNIQUE INDEX idx_paystack_transfers_code ON paystack_transfers(transfer_code);

-- Table: daily_transfer_limits
CREATE TABLE daily_transfer_limits (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES bank_accounts(id),
    transfer_date DATE NOT NULL,
    total_amount NUMERIC(15, 2) DEFAULT 0.00,
    transfer_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),

    UNIQUE(account_id, transfer_date)
);

-- Indexes for daily_transfer_limits
CREATE INDEX idx_daily_limits_account_date ON daily_transfer_limits(account_id, transfer_date);

-- Table: auth_tokens
CREATE TABLE auth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES bank_users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    device_id VARCHAR(255),
    device_name VARCHAR(255),
    ip_address VARCHAR(50),
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for auth_tokens
CREATE INDEX idx_auth_tokens_user_id ON auth_tokens(user_id);
CREATE INDEX idx_auth_tokens_token ON auth_tokens(token_hash);
CREATE INDEX idx_auth_tokens_expires ON auth_tokens(expires_at);

-- Success message
SELECT 'Demo Bank database schema created successfully!' AS message;
