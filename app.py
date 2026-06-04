from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

FILE_NAME = "expenses.csv"

if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Category", "Amount", "Note"])


def read_expenses():
    expenses = []
    with open(FILE_NAME, "r") as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            row["id"] = i
            expenses.append(row)
    return expenses


def write_expenses(expenses):
    with open(FILE_NAME, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Date", "Category", "Amount", "Note"])
        writer.writeheader()
        for e in expenses:
            writer.writerow({k: v for k, v in e.items() if k != "id"})


@app.route("/")
def home():
    expenses = read_expenses()
    category_filter = request.args.get("category", "")
    month_filter = request.args.get("month", "")

    filtered = expenses
    if category_filter:
        filtered = [e for e in filtered if e.get("Category", "") == category_filter]
    if month_filter:
        filtered = [e for e in filtered if e.get("Date", "").startswith(month_filter)]

    all_categories = sorted(set(e.get("Category", "") for e in expenses if e.get("Category")))
    all_months = sorted(set(e.get("Date", "")[:7] for e in expenses if e.get("Date")), reverse=True)

    total = sum(float(e.get("Amount", 0)) for e in filtered)

    return render_template("index.html",
        expenses=filtered,
        all_categories=all_categories,
        all_months=all_months,
        category_filter=category_filter,
        month_filter=month_filter,
        total=total
    )


@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        expenses = read_expenses()
        new = {
            "Date": request.form["date"],
            "Category": request.form["category"],
            "Amount": request.form["amount"],
            "Note": request.form.get("note", "")
        }
        expenses.append(new)
        write_expenses(expenses)
        return redirect(url_for("home"))
    from datetime import date
    return render_template("add.html", today=date.today().isoformat())


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    expenses = read_expenses()
    expenses = [e for e in expenses if e["id"] != expense_id]
    write_expenses(expenses)
    return redirect(url_for("home"))


@app.route("/report")
def report():
    expenses = read_expenses()
    total = 0
    category_summary = {}
    monthly_summary = {}

    for e in expenses:
        try:
            amount = float(e.get("Amount", 0))
        except ValueError:
            continue
        category = e.get("Category", "Other")
        month = e.get("Date", "")[:7]
        total += amount
        category_summary[category] = category_summary.get(category, 0) + amount
        monthly_summary[month] = monthly_summary.get(month, 0) + amount

    category_summary = dict(sorted(category_summary.items(), key=lambda x: -x[1]))
    monthly_summary = dict(sorted(monthly_summary.items()))

    return render_template("report.html",
        total=total,
        summary=category_summary,
        monthly=monthly_summary
    )


if __name__ == "__main__":
    app.run(debug=True)
