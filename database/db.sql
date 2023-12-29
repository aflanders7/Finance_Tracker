CREATE TABLE Expenses (
    ID INT NOT NULL PRIMARY KEY,
    Name VARCHAR(45) NOT NULL,
    Amount DECIMAL(6,2) NOT NULL,
    Category VARCHAR(45) NOT NULL,
    Description Varchar(90),
    Day DATE
);

INSERT INTO Expenses (Name, Amount, Category, Description, Day)
VALUES ('Lunch', 52, 'Food', 'Fancy restaurant', '2023-10-13');

SELECT SUM(Amount), Day FROM Expenses WHERE Day BETWEEN '2023-10-01' AND '2023-11-05' GROUP BY Day;