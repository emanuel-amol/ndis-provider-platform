-- Insert sample users
INSERT INTO users (email, password_hash, role) VALUES
('admin@ndis.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewDs.8.YhK6P.5jO', 'admin'), -- password: admin123
('coordinator@ndis.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewDs.8.YhK6P.5jO', 'coordinator'), -- password: admin123
('worker@ndis.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewDs.8.YhK6P.5jO', 'staff'); -- password: admin123

-- Insert sample staff
INSERT INTO staff (user_id, first_name, last_name, phone, position) VALUES
(1, 'John', 'Admin', '+61400123456', 'Administrator'),
(2, 'Sarah', 'Smith', '+61400234567', 'Coordinator'),
(3, 'Mike', 'Johnson', '+61400345678', 'Support Worker');

-- Insert sample participants
INSERT INTO participants (first_name, last_name, email, phone, ndis_number) VALUES
('Alice', 'Brown', 'alice@email.com', '+61400456789', 'NDIS001'),
('Bob', 'Wilson', 'bob@email.com', '+61400567890', 'NDIS002'),
('Carol', 'Davis', 'carol@email.com', '+61400678901', 'NDIS003');