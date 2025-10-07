CREATE DATABASE IF NOT EXISTS puny CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE puny;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL UNIQUE,
  reset_token VARCHAR(64) NULL
);

INSERT INTO users(email) VALUES
  ('victim@gmail.com');

