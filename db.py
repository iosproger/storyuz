import sqlite3

# Create the park database and table
# connie = sqlite3.connect('product.db')
# c = connie.cursor()
#
# c.execute("""
# CREATE TABLE product(
#   ID INTEGER PRIMARY KEY AUTOINCREMENT,
#   barcode TEXT,
#   name TEXT,
#   number TEXT,
#   price TEXT
# );
# """)
#
# connie.commit()
# connie.close()

# Create the user database and table
# connieuser = sqlite3.connect('user.db')
# cuser = connieuser.cursor()
#
# cuser.execute("""
# CREATE TABLE user(
#   ID INTEGER PRIMARY KEY AUTOINCREMENT,
#   Name TEXT,
#   Psw TEXT
# );
# """)
#
# connieuser.commit()
# connieuser.close()
#
# # Create the history database and table
conniehistory = sqlite3.connect('history.db')
chistory = conniehistory.cursor()

chistory.execute("""
CREATE TABLE history(
  ID INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT,
  userID TEXT,
  productnames TEXT,
  prices TEXT,
  quantity TEXT
);
""")

conniehistory.commit()
conniehistory.close()
