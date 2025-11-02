-- Drop tables if they exist to start fresh
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS departments;

-- Table for departments
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Table for users (clients and IT staff)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL, -- In a real app, this should be hashed
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK(role IN ('client', 'it_staff')), -- 'client' or 'it_staff'
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments (id)
);

-- Table for tickets
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open', -- e.g., Open, In Progress, Closed
    priority TEXT NOT NULL DEFAULT 'Medium', -- e.g., Low, Medium, High
    category TEXT DEFAULT 'Uncategorized', -- To be set by Ollama AI
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER NOT NULL,
    assigned_to_id INTEGER,
    department_id INTEGER NOT NULL,
    FOREIGN KEY (created_by_id) REFERENCES users (id),
    FOREIGN KEY (assigned_to_id) REFERENCES users (id),
    FOREIGN KEY (department_id) REFERENCES departments (id)
);

-- Table for comments on tickets
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ticket_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (ticket_id) REFERENCES tickets (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert some initial data for testing
INSERT INTO departments (name) VALUES ('IT'), ('Human Resources'), ('Finance');
INSERT INTO users (username, password, email, role, department_id) VALUES
    ('admin', 'adminpass', 'admin@example.com', 'it_staff', 1),
    ('johndoe', 'userpass', 'john.doe@example.com', 'client', 2);
