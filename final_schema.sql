PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS members;

CREATE TABLE members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL CHECK (length(trim(full_name)) > 0),
    email TEXT NOT NULL UNIQUE CHECK (length(trim(email)) > 0 AND instr(email, '@') > 1),
    phone TEXT,
    join_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    author TEXT NOT NULL CHECK (length(trim(author)) > 0),
    genre TEXT NOT NULL CHECK (length(trim(genre)) > 0),
    published_date DATE,
    isbn TEXT NOT NULL UNIQUE CHECK (length(trim(isbn)) > 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    loan_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    status TEXT NOT NULL CHECK (status IN ('Borrowed', 'Returned')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(member_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CHECK (due_date >= loan_date),
    CHECK (return_date IS NULL OR return_date >= loan_date)
);

CREATE INDEX idx_loans_member_id ON loans(member_id);
CREATE INDEX idx_loans_book_id ON loans(book_id);
CREATE INDEX idx_loans_status ON loans(status);

INSERT INTO members (full_name, email, phone, join_date) VALUES
('Alice Johnson','alice@example.com','111-111-1111','2024-01-01'),
('Bob Smith','bob@example.com','222-222-2222','2024-02-01'),
('Carol White','carol@example.com','333-333-3333','2024-03-01'),
('David Brown','david@example.com','444-444-4444','2024-04-01'),
('Emma Davis','emma@example.com','555-555-5555','2024-05-01');

INSERT INTO books (title, author, genre, published_date, isbn) VALUES
('Database Basics','John Miller','Education','2020-01-01','978-0000000001'),
('Python Programming','Sarah Lee','Programming','2021-01-01','978-0000000002'),
('Data Structures','Mike Chen','Technology','2019-01-01','978-0000000003'),
('Web Development','Nina Patel','Programming','2022-01-01','978-0000000004'),
('SQL Fundamentals','Chris Green','Education','2023-01-01','978-0000000005');

INSERT INTO loans (member_id, book_id, loan_date, due_date, return_date, status) VALUES
(1,1,'2024-06-01','2024-06-10','2024-06-09','Returned'),
(2,2,'2024-06-02','2024-06-12',NULL,'Borrowed'),
(3,3,'2024-06-03','2024-06-13','2024-06-15','Returned'),
(5,5,'2024-06-05','2024-06-20',NULL,'Borrowed');
