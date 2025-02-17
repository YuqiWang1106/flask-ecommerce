DROP TABLE IF EXISTS Authentication;
DROP TABLE IF EXISTS Shopping_cart;


CREATE TABLE IF NOT EXISTS Authentication (
    UserID TEXT PRIMARY KEY,
    PasswordHash TEXT NOT NULL,
    SessionID TEXT
);

CREATE TABLE IF NOT EXISTS Shopping_cart (
    ShopperID TEXT PRIMARY KEY,
    ProductID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL DEFAULT 1,
    AddedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- Adds a new employee whose ID is 999999, first and last names are "WEB"
-- This employee is used to represent the web application itself
INSERT OR IGNORE INTO Employees (EmployeeID, LastName, FirstName)
VALUES (999999, "WEB", "WEB");
