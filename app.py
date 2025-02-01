from flask import Flask, render_template, jsonify, request
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Home Page Route
@app.route("/")
def index():
    return render_template("index.html")

# Book Listing Route
@app.route("/books")
def books():
    books = load_books_xml()  # Load books from the XML file
    return render_template("book_list.html", books=books)

# Function to Load Books from XML
def load_books_xml():
    """Load all books from books.xml"""
    try:
        tree = ET.parse("books.xml")
        root = tree.getroot()
        books = []
        for book in root.findall("book"):
            books.append({
                "id": book.get("id"),  # Load ID as it is
                "title": book.find("title").text,
                "author": book.find("author").text,
                "year": book.find("year").text,
            })

        return books
    except FileNotFoundError:

        return []


# Add New Book Route (JSON API)
@app.route("/book/add", methods=["POST"])
def add_book_json():
    try:
        new_book = request.json  # Get new book from JSON
        tree = ET.parse("books.xml")
        root = tree.getroot()

        # Check for duplicate ID
        if root.find(f"./book[@id='{new_book['id']}']") is not None:
            return jsonify({"error": f"Book with ID {new_book['id']} already exists"}), 400

        # Add new book
        book = ET.Element("book", id=new_book["id"])
        ET.SubElement(book, "title").text = new_book["title"]
        ET.SubElement(book, "author").text = new_book["author"]
        ET.SubElement(book, "year").text = new_book["year"]

        root.append(book)
        tree.write("books.xml")
        return jsonify({"message": f"Book with ID {new_book['id']} has been added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add New Book via UI Route
@app.route("/add_book", methods=["GET", "POST"])
def add_book_ui():
    if request.method == "POST":
        new_book = {
            "id": request.form["id"],
            "title": request.form["title"],
            "author": request.form["author"],
            "year": request.form["year"],
        }
        try:
            tree = ET.parse("books.xml")
            root = tree.getroot()

            # Add new book
            book = ET.Element("book", id=new_book["id"])
            ET.SubElement(book, "title").text = new_book["title"]
            ET.SubElement(book, "author").text = new_book["author"]
            ET.SubElement(book, "year").text = new_book["year"]

            root.append(book)
            tree.write("books.xml")
            return render_template("success.html", message="Book added successfully!")
        except Exception as e:
            return render_template("error.html", message=str(e))
    return render_template("add_book.html")

# Delete Book Route
@app.route("/delete_book", methods=["GET", "POST"])
def delete_book_ui():
    if request.method == "POST":
        book_id = request.form["id"]
        try:
            tree = ET.parse("books.xml")
            root = tree.getroot()

            # Find and delete the book
            book_to_delete = root.find(f".//book[@id='{book_id}']")
            if book_to_delete is not None:
                root.remove(book_to_delete)
                tree.write("books.xml")
                return render_template("success.html", message="Book deleted successfully!")
            else:
                return render_template("error.html", message="Book not found!")
        except Exception as e:
            return render_template("error.html", message=str(e))
    return render_template("delete_book.html")

# Fetch Single Book Route
@app.route("/get_book", methods=["GET", "POST"])
def get_book_ui():
    if request.method == "POST":
        book_id = request.form["id"]
        try:
            books = load_books_xml()
            # Compare ID as string for accuracy
            book = next((b for b in books if str(b["id"]) == str(book_id)), None)
            if book:
                return render_template("book_detail.html", book=book)
            else:
                return render_template("error.html", message="Book not found!")
        except Exception as e:
            return render_template("error.html", message=str(e))
    return render_template("get_book.html")


if __name__ == '__main__':
    app.run(debug=True)
