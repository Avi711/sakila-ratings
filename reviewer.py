import os
import mysql.connector
import re
from dotenv import load_dotenv
load_dotenv()
password = os.getenv('MYSQL_ROOT_PASSWORD')
# Create a connection
cnx = mysql.connector.connect(
    user='root',
    password=os.getenv('MYSQL_ROOT_PASSWORD', password),
    host='127.0.0.1',
    port='3307',
    database='sakila'
)
cursor = cnx.cursor()
cnx.autocommit = True

def create_rating_table():
    if check_table_exists("rating"):
        return
    cursor.execute("""
        CREATE TABLE rating (
          film_id SMALLINT,
          reviewer_id INT, 
          rating DECIMAL(2,1),
          FOREIGN KEY (film_id) REFERENCES film(film_id),
          FOREIGN KEY (reviewer_id) REFERENCES reviewer(reviewer_id)
        );
    """)

def create_reviewer_table():
    if check_table_exists("reviewer"):
        return
    cursor.execute("""
        CREATE TABLE reviewer (
          reviewer_id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
          first_name varchar(45),
          last_name varchar(45)
        );
    """)


def check_table_exists(table_name):
    cursor.execute(f"SHOW tables LIKE '{table_name}'")
    result = cursor.fetchall()
    return True if result != [] else False


insert_to_reviewer_stm = "INSERT INTO reviewer (first_name, last_name) VALUES (%s, %s)"
def find_customer_by_id(id):
    cursor.execute(f"SELECT * FROM reviewer WHERE reviewer_id= {id};")
    result = cursor.fetchall()
    return result

def add_reviewer_by_name():
    first_name = input("Please enter your first name: ")
    last_name = input("Please enter your last name: ")
    cursor.execute(insert_to_reviewer_stm, (first_name, last_name))
    id = cursor.lastrowid
    return [(id,first_name, last_name)]

def film_exists(film_name):
    cursor.execute(f"SELECT * FROM film WHERE title = '{film_name}';")
    result = cursor.fetchall()
    return result

def is_rating_valid(rating):
    pattern = re.compile(r"^\d\.\d$")
    return pattern.match(rating)


create_reviewer_table()
#create_rating_table()


customer_id = input("Please enter your id: ")
result = find_customer_by_id(customer_id)
if(result == []):
    result = add_reviewer_by_name()
print("Hello,", result[0][1], result[0][2] + ".")

film_name = input("Please enter film name to rate: ")
films = []
film_id = ""
while(films == []):
    films = film_exists(film_name)
    if (len(films) == 1):
        film_id = films[0][0]
        break
    if (len(films) > 1):
        ids = []
        for film in films:
            ids.append(film[0])
            print("film name:", film[0], "year:", film[3])
        chosen_id = input("Please pick movie id from the list above")
        if chosen_id in ids:
            film_id = chosen_id
            break
    film_name = input("The film doesn't exists please enter another name: ")

print("film id:", film_id)

rating = input("Please enter rating for the film: ")
while (not is_rating_valid(rating)):
    rating = input("Invalid rating please enter valid rating: ")



