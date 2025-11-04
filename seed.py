import sqlite3

conn = sqlite3.connect('ticket_system/backend/tickets.db')
cursor = conn.cursor()

cursor.execute("INSERT INTO users (username, password, email, role, department_id) VALUES (?, ?, ?, ?, ?)", ('testadmin', 'testpass', 'testadmin@example.com', 'admin', 1))
cursor.execute("INSERT INTO tickets (title, description, created_by_id, department_id) VALUES (?, ?, ?, ?)", ('Test Ticket', 'This is a test ticket.', 2, 1))

conn.commit()
conn.close()
