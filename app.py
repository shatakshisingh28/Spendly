from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)

FILE_NAME = "expenses.csv"

# Create CSV file if it doesn't exist
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Category", "Amount"])


@app.route("/")
def home():

    expenses = []

    with open(FILE_NAME, "r") as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            expenses.append(row)

    return render_template(
        "index.html",
        expenses=expenses
    )


@app.route("/add", methods=["GET", "POST"])
def add_expense():

    if request.method == "POST":

        date = request.form["date"]
        category = request.form["category"]
        amount = request.form["amount"]

        with open(FILE_NAME, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([date, category, amount])

        return redirect("/")

    return render_template("add.html")


@app.route("/report")
def report():

    total = 0

    category_summary = {}

    with open(FILE_NAME, "r") as file:

        reader = csv.reader(file)

        next(reader)

        for row in reader:

            category = row[1]
            amount = float(row[2])

            total += amount

            if category in category_summary:
                category_summary[category] += amount
            else:
                category_summary[category] = amount

    return render_template(
        "report.html",
        total=total,
        summary=category_summary
    )


if __name__ == "__main__":
    app.run(debug=True)