-- =====================================================
-- SMART VOTING SYSTEM DATABASE
-- =====================================================

DROP TABLE IF EXISTS votes CASCADE;
DROP TABLE IF EXISTS voters CASCADE;
DROP TABLE IF EXISTS candidates CASCADE;
DROP TABLE IF EXISTS verification_records CASCADE;
DROP TABLE IF EXISTS admins CASCADE;


-- =====================================================
-- 1. VOTERS TABLE
-- =====================================================

CREATE TABLE voters
(
    voter_id SERIAL PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(100) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL,

    voter_number VARCHAR(50) UNIQUE NOT NULL,

    dob DATE NOT NULL,

    aadhaar_number VARCHAR(12) NOT NULL,

    pan_number VARCHAR(10) NOT NULL,

    document_verified BOOLEAN DEFAULT FALSE,

    status VARCHAR(20) DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- 2. VERIFICATION MASTER DATA
-- =====================================================

CREATE TABLE verification_records
(
    verification_id SERIAL PRIMARY KEY,

    voter_number VARCHAR(50) UNIQUE NOT NULL,

    full_name VARCHAR(100) NOT NULL,

    dob DATE NOT NULL,

    aadhaar_number VARCHAR(12) UNIQUE NOT NULL,

    pan_number VARCHAR(10) UNIQUE NOT NULL,

    document_type VARCHAR(100)
        DEFAULT 'Aadhaar, PAN, Voter ID',

    verification_status VARCHAR(20)
        DEFAULT 'Verified'
);


-- =====================================================
-- 3. CANDIDATES TABLE
-- =====================================================

CREATE TABLE candidates
(
    candidate_id SERIAL PRIMARY KEY,

    candidate_name VARCHAR(100) NOT NULL,

    party_name VARCHAR(100) NOT NULL,

    symbol VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- 4. VOTES TABLE
-- ONE VOTER = ONE VOTE
-- =====================================================

CREATE TABLE votes
(
    vote_id SERIAL PRIMARY KEY,

    voter_id INTEGER NOT NULL
        REFERENCES voters(voter_id)
        ON DELETE CASCADE,

    candidate_id INTEGER NOT NULL
        REFERENCES candidates(candidate_id)
        ON DELETE CASCADE,

    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(voter_id)
);


-- =====================================================
-- 5. ADMINS TABLE
-- =====================================================

CREATE TABLE admins
(
    admin_id SERIAL PRIMARY KEY,

    username VARCHAR(50) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL
);


-- =====================================================
-- 6. ADMIN LOGIN
-- =====================================================

INSERT INTO admins
(username, password)
VALUES
('admin', 'admin123');


-- =====================================================
-- 7. VERIFICATION RECORDS
-- 10 DEMO USERS
-- =====================================================

INSERT INTO verification_records
(
    voter_number,
    full_name,
    dob,
    aadhaar_number,
    pan_number,
    document_type,
    verification_status
)
VALUES

(
    'VN002',
    'Harshada Nahire',
    '2007-04-25',
    '123456789012',
    'ABCDE1234F',
    'Aadhaar, PAN, Voter ID',
    'Verified'
),

(
    'VN003',
    'Rahul Patil',
    '2003-08-15',
    '234567890123',
    'BCDEF2345G',
    'Aadhaar, PAN, Voter ID',
    'Verified'
),

(
    'VN004',
    'Sneha Sharma',
    '2004-02-20',
    '345678901234',
    'CDEFG3456H',
    'Aadhaar, PAN, Voter ID',
    'Verified'
),

(
    'VN005',
    'Pooja Shinde',
    '2005-06-10',
    '456789012345',
    'DEFGH4567J',
    'Aadhaar, PAN, Voter ID',
    'Verified'
),

(
    'VN006',
    'Akash Jadhav',
    '2002-11-12',
    '567890123456',
    'EFGHI5678K',
    'Aadhaar, PAN, Voter ID',
    'Verified'
),

(
    'VN007',
    'Priya More',
    '2006-03-05',
    '678901234567',
    'FGHIJ6789L',
    'Aadhaar, PAN, Voter ID',
    'Verified'
),

(
    'VN008',
    'Rohit Pawar',
    '2003-09-18',
    '789012345678',
    'GHIJK7890M',
    'Aadhaar, PAN, Voter ID',
    'Verified'
),

(
    'VN009',
    'Neha Chavan',
    '2005-01-22',
    '890123456789',
    'HIJKL8901N',
    'Aadhaar, PAN, Voter ID',
    'Verified'
),

(
    'VN0010',
    'Sagar More',
    '2004-07-30',
    '901234567890',
    'IJKLM9012P',
    'Aadhaar, PAN, Voter ID',
    'Verified'
),

(
    'VN011',
    'Kiran Pawar',
    '2006-12-14',
    '012345678901',
    'JKLMN0123Q',
    'Aadhaar, PAN, Voter ID',
    'Verified'
);


-- =====================================================
-- 8. DEMO CANDIDATES
-- =====================================================

INSERT INTO candidates
(candidate_name, party_name, symbol)
VALUES

('Rahul Patil', 'ABC Party', '🌳'),

('Sneha Sharma', 'XYZ Party', '🌸'),

('Amit Deshmukh', 'PQR Party', '⭐');


-- =====================================================
-- 9. CHECK VERIFICATION RECORDS
-- =====================================================

SELECT *
FROM verification_records
ORDER BY verification_id;


-- =====================================================
-- 10. CHECK CANDIDATES
-- =====================================================

SELECT *
FROM candidates
ORDER BY candidate_id;


-- =====================================================
-- 11. CHECK ADMIN
-- =====================================================

SELECT *
FROM admins;
