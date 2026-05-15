# Normalization Report

## Starting Schema
The original project database contained three tables:

```text
members(member_id, full_name, email, phone, join_date, created_at)
books(book_id, title, author, genre, published_date, isbn, created_at)
loans(loan_id, member_id, book_id, loan_date, due_date, return_date, status, created_at, late_days)
```

## Original Functional Dependencies

### members
```text
member_id -> full_name, email, phone, join_date, created_at
email -> member_id, full_name, phone, join_date, created_at
```

### books
```text
book_id -> title, author, genre, published_date, isbn, created_at
isbn -> book_id, title, author, genre, published_date, created_at
```

### loans
```text
loan_id -> member_id, book_id, loan_date, due_date, return_date, status, created_at, late_days
(member_id, book_id, loan_date) -> due_date, return_date, status
```

## Anomaly Identification

### members
The table mostly satisfies 3NF because all descriptive fields depend on the primary key. However, `email` should be unique because it identifies one member. Without a unique constraint, duplicate member records could be inserted for the same person.

### books
The table mostly satisfies 3NF because each book attribute depends on `book_id`. However, `isbn` is a candidate key and should be unique. Without a unique constraint, the same book edition could be inserted more than once.

### loans
The original `loans` table included `late_days`. This creates a derived-data dependency:

```text
due_date, return_date -> late_days
```

That means `late_days` depends on other non-key attributes, not only on the primary key. Storing it can cause update anomalies. For example, if `return_date` changes but `late_days` is not updated, the database becomes inconsistent. Therefore, `late_days` was removed from the stored schema and is calculated dynamically in application logic or SQL queries.

## Decomposition Steps

### Step 1: Members
Original:

```text
members(member_id, full_name, email, phone, join_date, created_at)
```

No decomposition needed. Add constraints:

```text
member_id PRIMARY KEY
email UNIQUE NOT NULL
full_name NOT NULL
join_date NOT NULL
created_at DEFAULT CURRENT_TIMESTAMP
```

Final:

```text
members(member_id, full_name, email, phone, join_date, created_at)
```

### Step 2: Books
Original:

```text
books(book_id, title, author, genre, published_date, isbn, created_at)
```

No decomposition needed. Add constraints:

```text
book_id PRIMARY KEY
isbn UNIQUE NOT NULL
title NOT NULL
author NOT NULL
genre NOT NULL
created_at DEFAULT CURRENT_TIMESTAMP
```

Final:

```text
books(book_id, title, author, genre, published_date, isbn, created_at)
```

### Step 3: Loans
Original:

```text
loans(loan_id, member_id, book_id, loan_date, due_date, return_date, status, created_at, late_days)
```

Remove the derived field:

```text
late_days = max(return_date - due_date, 0)
```

Final:

```text
loans(loan_id, member_id, book_id, loan_date, due_date, return_date, status, created_at)
```

Add referential and validation constraints:

```text
member_id REFERENCES members(member_id)
book_id REFERENCES books(book_id)
status CHECK ('Borrowed', 'Returned')
due_date >= loan_date
return_date IS NULL OR return_date >= loan_date
```

## Final Relational Schema

```text
members(
    member_id PK,
    full_name NOT NULL,
    email UNIQUE NOT NULL,
    phone,
    join_date NOT NULL,
    created_at DEFAULT CURRENT_TIMESTAMP
)

books(
    book_id PK,
    title NOT NULL,
    author NOT NULL,
    genre NOT NULL,
    published_date,
    isbn UNIQUE NOT NULL,
    created_at DEFAULT CURRENT_TIMESTAMP
)

loans(
    loan_id PK,
    member_id FK -> members.member_id,
    book_id FK -> books.book_id,
    loan_date NOT NULL,
    due_date NOT NULL,
    return_date,
    status CHECK ('Borrowed', 'Returned'),
    created_at DEFAULT CURRENT_TIMESTAMP
)
```

## 3NF Justification
Each table is in 3NF because:

1. Every table has a primary key.
2. Each non-key attribute depends on the key.
3. No non-key attribute depends on another non-key attribute.
4. Derived data, specifically `late_days`, is not stored and is calculated when needed.
5. Candidate keys such as `email` and `isbn` are enforced with unique constraints.
