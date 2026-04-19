import mysql.connector
from werkzeug.security import generate_password_hash


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="cinema",
    database="transport_management"
)
cursor = db.cursor()

name = "paul"
pw = "paul123"
hashed = generate_password_hash(pw)

cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", (name, hashed, "admin"))
db.commit()
print("Admin creat cu succes!")