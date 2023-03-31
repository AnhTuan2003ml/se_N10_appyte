import mysql.connector

# Tạo kết nối tới database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="anhtuan2003",
  database="health_advice"
)

# Thực hiện truy vấn SQL
mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM user")

myresult = mycursor.fetchall()

for x in myresult:
  print(x)
