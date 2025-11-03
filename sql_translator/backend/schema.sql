-- SQL Schema for a simplified SAP B1-like database
-- This helps the AI understand the context for generating SQL queries.

DROP TABLE IF EXISTS INV1;
DROP TABLE IF EXISTS OINV;
DROP TABLE IF EXISTS OCRD;

-- OCRD: Business Partner Master Data (simplified for customers)
CREATE TABLE OCRD (
    CardCode TEXT PRIMARY KEY,   -- Customer Code
    CardName TEXT NOT NULL,      -- Customer Name
    Country TEXT,
    City TEXT
);

-- OINV: A/R Invoice Header
CREATE TABLE OINV (
    DocEntry INTEGER PRIMARY KEY AUTOINCREMENT, -- Invoice unique ID
    DocNum INT NOT NULL,                     -- Invoice Number
    CardCode TEXT NOT NULL,                  -- Customer Code
    DocDate DATE,
    DocTotal DECIMAL(10, 2),                 -- Total invoice amount
    FOREIGN KEY (CardCode) REFERENCES OCRD(CardCode)
);

-- INV1: A/R Invoice Lines (items in the invoice)
CREATE TABLE INV1 (
    DocEntry INTEGER,
    LineNum INTEGER,
    ItemCode TEXT,
    Description TEXT,
    Quantity INTEGER,
    Price DECIMAL(10, 2),
    PRIMARY KEY (DocEntry, LineNum),
    FOREIGN KEY (DocEntry) REFERENCES OINV(DocEntry)
);

-- --- Sample Data ---

-- Customers (OCRD)
INSERT INTO OCRD (CardCode, CardName, Country, City) VALUES
('C001', 'Microchips Inc.', 'USA', 'San Jose'),
('C002', 'PC Systems', 'Mexico', 'Guadalajara'),
('C003', 'Innovate Tech', 'USA', 'Austin');

-- Invoices (OINV)
INSERT INTO OINV (DocNum, CardCode, DocDate, DocTotal) VALUES
(101, 'C001', '2023-10-15', 1500.00),
(102, 'C002', '2023-10-20', 850.50),
(103, 'C001', '2023-11-01', 320.00),
(104, 'C003', '2023-11-05', 2400.00);

-- Invoice Lines (INV1)
-- Invoice 101
INSERT INTO INV1 (DocEntry, LineNum, ItemCode, Description, Quantity, Price) VALUES
(1, 1, 'CPU-01', 'Intel Core i9 Processor', 2, 750.00);
-- Invoice 102
INSERT INTO INV1 (DocEntry, LineNum, ItemCode, Description, Quantity, Price) VALUES
(2, 1, 'RAM-16', '16GB DDR4 RAM Module', 5, 170.10);
-- Invoice 103
INSERT INTO INV1 (DocEntry, LineNum, ItemCode, Description, Quantity, Price) VALUES
(3, 1, 'SSD-01', '1TB NVMe SSD', 2, 160.00);
-- Invoice 104
INSERT INTO INV1 (DocEntry, LineNum, ItemCode, Description, Quantity, Price) VALUES
(4, 1, 'GPU-01', 'NVIDIA RTX 4080', 1, 1200.00),
(4, 2, 'PSU-01', '850W Power Supply', 1, 1200.00);
