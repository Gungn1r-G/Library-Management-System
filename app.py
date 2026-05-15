from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError

BASE_DIR = Path(__file__).resolve().parent

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-change-before-production"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR / 'library.db'}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_data()

    register_routes(app)
    return app


class Member(db.Model):
    __tablename__ = "members"

    member_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    join_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    loans = db.relationship("Loan", back_populates="member", cascade="save-update, merge")


class Book(db.Model):
    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    published_date = db.Column(db.Date)
    isbn = db.Column(db.String(20), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    loans = db.relationship("Loan", back_populates="book", cascade="save-update, merge")

    @property
    def is_available(self):
        return not any(loan.status == "Borrowed" for loan in self.loans)


class Loan(db.Model):
    __tablename__ = "loans"

    loan_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("members.member_id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"), nullable=False)
    loan_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    status = db.Column(db.String(20), nullable=False, default="Borrowed")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    member = db.relationship("Member", back_populates="loans")
    book = db.relationship("Book", back_populates="loans")

    @property
    def late_days(self):
        comparison_date = self.return_date or date.today()
        return max((comparison_date - self.due_date).days, 0)


def parse_date(value, field_name, required=True):
    if not value:
        if required:
            raise ValueError(f"{field_name} is required.")
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format.") from exc


def require_text(value, field_name):
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required.")
    return cleaned


def seed_data():
    if Member.query.first():
        return
    members = [
        Member(full_name="Alice Johnson", email="alice@example.com", phone="111-111-1111", join_date=date(2024, 1, 1)),
        Member(full_name="Bob Smith", email="bob@example.com", phone="222-222-2222", join_date=date(2024, 2, 1)),
        Member(full_name="Carol White", email="carol@example.com", phone="333-333-3333", join_date=date(2024, 3, 1)),
        Member(full_name="David Brown", email="david@example.com", phone="444-444-4444", join_date=date(2024, 4, 1)),
        Member(full_name="Emma Davis", email="emma@example.com", phone="555-555-5555", join_date=date(2024, 5, 1)),
    ]
    books = [
        Book(title="Database Basics", author="John Miller", genre="Education", published_date=date(2020, 1, 1), isbn="978-0000000001"),
        Book(title="Python Programming", author="Sarah Lee", genre="Programming", published_date=date(2021, 1, 1), isbn="978-0000000002"),
        Book(title="Data Structures", author="Mike Chen", genre="Technology", published_date=date(2019, 1, 1), isbn="978-0000000003"),
        Book(title="Web Development", author="Nina Patel", genre="Programming", published_date=date(2022, 1, 1), isbn="978-0000000004"),
        Book(title="SQL Fundamentals", author="Chris Green", genre="Education", published_date=date(2023, 1, 1), isbn="978-0000000005"),
    ]
    db.session.add_all(members + books)
    db.session.commit()
    loans = [
        Loan(member_id=1, book_id=1, loan_date=date(2024, 6, 1), due_date=date(2024, 6, 10), return_date=date(2024, 6, 9), status="Returned"),
        Loan(member_id=2, book_id=2, loan_date=date(2024, 6, 2), due_date=date(2024, 6, 12), status="Borrowed"),
        Loan(member_id=3, book_id=3, loan_date=date(2024, 6, 3), due_date=date(2024, 6, 13), return_date=date(2024, 6, 15), status="Returned"),
        Loan(member_id=5, book_id=5, loan_date=date(2024, 6, 5), due_date=date(2024, 6, 20), status="Borrowed"),
    ]
    db.session.add_all(loans)
    db.session.commit()


def register_routes(app):
    @app.route("/")
    def dashboard():
        total_books = Book.query.count()
        total_members = Member.query.count()
        active_loans = Loan.query.filter_by(status="Borrowed").count()
        returned_loans = Loan.query.filter(Loan.return_date.isnot(None)).all()
        avg_late_days = round(sum(loan.late_days for loan in returned_loans) / len(returned_loans), 2) if returned_loans else 0
        books_by_genre = db.session.query(Book.genre, func.count(Book.book_id)).group_by(Book.genre).all()
        recent_loans = Loan.query.order_by(Loan.loan_date.desc()).limit(5).all()
        return render_template("dashboard.html", total_books=total_books, total_members=total_members,
                               active_loans=active_loans, avg_late_days=avg_late_days,
                               books_by_genre=books_by_genre, recent_loans=recent_loans)

    @app.route("/members")
    def members():
        return render_template("members.html", members=Member.query.order_by(Member.full_name).all())

    @app.route("/members/new", methods=["GET", "POST"])
    def new_member():
        if request.method == "POST":
            try:
                member = Member(
                    full_name=require_text(request.form.get("full_name"), "Full name"),
                    email=require_text(request.form.get("email"), "Email"),
                    phone=(request.form.get("phone") or "").strip(),
                    join_date=parse_date(request.form.get("join_date"), "Join date"),
                )
                db.session.add(member)
                db.session.commit()
                flash("Member created.", "success")
                return redirect(url_for("members"))
            except (ValueError, IntegrityError) as exc:
                db.session.rollback()
                flash(str(exc.orig) if isinstance(exc, IntegrityError) else str(exc), "danger")
        return render_template("member_form.html", member=None)

    @app.route("/members/<int:member_id>/edit", methods=["GET", "POST"])
    def edit_member(member_id):
        member = Member.query.get_or_404(member_id)
        if request.method == "POST":
            try:
                member.full_name = require_text(request.form.get("full_name"), "Full name")
                member.email = require_text(request.form.get("email"), "Email")
                member.phone = (request.form.get("phone") or "").strip()
                member.join_date = parse_date(request.form.get("join_date"), "Join date")
                db.session.commit()
                flash("Member updated.", "success")
                return redirect(url_for("members"))
            except (ValueError, IntegrityError) as exc:
                db.session.rollback()
                flash(str(exc.orig) if isinstance(exc, IntegrityError) else str(exc), "danger")
        return render_template("member_form.html", member=member)

    @app.route("/members/<int:member_id>/delete", methods=["POST"])
    def delete_member(member_id):
        member = Member.query.get_or_404(member_id)
        if member.loans:
            flash("Cannot delete a member with loan history.", "danger")
        else:
            db.session.delete(member)
            db.session.commit()
            flash("Member deleted.", "success")
        return redirect(url_for("members"))

    @app.route("/members/<int:member_id>")
    def member_detail(member_id):
        member = Member.query.get_or_404(member_id)
        return render_template("member_detail.html", member=member)

    @app.route("/books")
    def books():
        return render_template("books.html", books=Book.query.order_by(Book.title).all())

    @app.route("/books/new", methods=["GET", "POST"])
    def new_book():
        if request.method == "POST":
            try:
                book = Book(
                    title=require_text(request.form.get("title"), "Title"),
                    author=require_text(request.form.get("author"), "Author"),
                    genre=require_text(request.form.get("genre"), "Genre"),
                    published_date=parse_date(request.form.get("published_date"), "Published date", required=False),
                    isbn=require_text(request.form.get("isbn"), "ISBN"),
                )
                db.session.add(book)
                db.session.commit()
                flash("Book created.", "success")
                return redirect(url_for("books"))
            except (ValueError, IntegrityError) as exc:
                db.session.rollback()
                flash(str(exc.orig) if isinstance(exc, IntegrityError) else str(exc), "danger")
        return render_template("book_form.html", book=None)

    @app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
    def edit_book(book_id):
        book = Book.query.get_or_404(book_id)
        if request.method == "POST":
            try:
                book.title = require_text(request.form.get("title"), "Title")
                book.author = require_text(request.form.get("author"), "Author")
                book.genre = require_text(request.form.get("genre"), "Genre")
                book.published_date = parse_date(request.form.get("published_date"), "Published date", required=False)
                book.isbn = require_text(request.form.get("isbn"), "ISBN")
                db.session.commit()
                flash("Book updated.", "success")
                return redirect(url_for("books"))
            except (ValueError, IntegrityError) as exc:
                db.session.rollback()
                flash(str(exc.orig) if isinstance(exc, IntegrityError) else str(exc), "danger")
        return render_template("book_form.html", book=book)

    @app.route("/books/<int:book_id>/delete", methods=["POST"])
    def delete_book(book_id):
        book = Book.query.get_or_404(book_id)
        if book.loans:
            flash("Cannot delete a book with loan history.", "danger")
        else:
            db.session.delete(book)
            db.session.commit()
            flash("Book deleted.", "success")
        return redirect(url_for("books"))

    @app.route("/books/<int:book_id>")
    def book_detail(book_id):
        book = Book.query.get_or_404(book_id)
        return render_template("book_detail.html", book=book)

    @app.route("/loans")
    def loans():
        return render_template("loans.html", loans=Loan.query.order_by(Loan.loan_date.desc()).all())

    @app.route("/loans/new", methods=["GET", "POST"])
    def new_loan():
        members = Member.query.order_by(Member.full_name).all()
        books = Book.query.order_by(Book.title).all()
        if request.method == "POST":
            try:
                member_id = int(request.form.get("member_id"))
                book_id = int(request.form.get("book_id"))
                loan_date = parse_date(request.form.get("loan_date"), "Loan date")
                due_date = parse_date(request.form.get("due_date"), "Due date")
                if due_date < loan_date:
                    raise ValueError("Due date cannot be before loan date.")

                with db.session.begin_nested():
                    active = Loan.query.filter_by(book_id=book_id, status="Borrowed").first()
                    if active:
                        raise ValueError("This book is already borrowed.")
                    db.session.add(Loan(member_id=member_id, book_id=book_id, loan_date=loan_date, due_date=due_date, status="Borrowed"))
                db.session.commit()
                flash("Loan created using transaction logic.", "success")
                return redirect(url_for("loans"))
            except (ValueError, TypeError) as exc:
                db.session.rollback()
                flash(str(exc), "danger")
        return render_template("loan_form.html", members=members, books=books)

    @app.route("/loans/<int:loan_id>/return", methods=["POST"])
    def return_loan(loan_id):
        loan = Loan.query.get_or_404(loan_id)
        if loan.status == "Returned":
            flash("Loan is already returned.", "warning")
        else:
            loan.return_date = date.today()
            loan.status = "Returned"
            db.session.commit()
            flash("Book returned.", "success")
        return redirect(url_for("loans"))

    @app.route("/loans/<int:loan_id>/delete", methods=["POST"])
    def delete_loan(loan_id):
        loan = Loan.query.get_or_404(loan_id)
        db.session.delete(loan)
        db.session.commit()
        flash("Loan deleted.", "success")
        return redirect(url_for("loans"))


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
