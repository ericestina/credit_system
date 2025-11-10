import sqlite3

conn = sqlite3.connect("credit.db")
cur = conn.cursor()

print("\nPolicies")
for row in cur.execute("SELECT * FROM policies;"):
    print(row)

print("\nApplications")
for row in cur.execute("SELECT * FROM applications;"):
    print(row)

conn.close()