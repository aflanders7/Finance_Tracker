CREATE TABLE Expenses (
    ID INT(10) NOT NULL AUTO_INCREMENT,
    Name VARCHAR(45) NOT NULL,
    Amount DECIMAL(6,2) NOT NULL,
    Category VARCHAR(45) NOT NULL,
    Description Varchar(90),
    Day DATE,
    PRIMARY KEY (ID)
);

INSERT INTO Expenses (Name, Amount, Category, Description, Day)
VALUES ('Lunch', 52, 'Food', 'Fancy restaurant', '2023-10-13');
