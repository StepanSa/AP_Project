CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(128),
    firstName VARCHAR(32),
    lastName VARCHAR(32),
    email VARCHAR(32),
    password VARCHAR(32),
    phone VARCHAR(32),
    birthDate DATE,
    userStatus ENUM('0', '1') DEFAULT '1'
);


CREATE TABLE ticket (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128),
    ticketStatus ENUM('free', 'booked', 'sold') DEFAULT 'free',
    price INT
);

CREATE TABLE transaction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticketId INT,
    userId INT,
    FOREIGN KEY(ticketId) REFERENCES ticket(id),
    FOREIGN KEY(userId) REFERENCES user(id),
    transactionStatus ENUM('placed', 'approved', 'denied') DEFAULT 'placed'
);

-- mysql -u root -p ap_project
-- source B:/Projects/AP_Project/lab6/create_tables.sql