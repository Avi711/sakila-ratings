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
          film_id SMALLINT unsigned,
          reviewer_id INT, 
          rating DECIMAL(2,1),
          primary key (film_id,reviewer_id),
          FOREIGN KEY (film_id) REFERENCES film(film_id) ON DELETE CASCADE ON UPDATE CASCADE,
          FOREIGN KEY (reviewer_id) REFERENCES reviewer(reviewer_id) ON DELETE CASCADE ON UPDATE CASCADE
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
    try:
        cursor.execute(f"SELECT * FROM reviewer WHERE reviewer_id= {id};")

    except:
        return None
    result = cursor.fetchall()
    return result


def add_reviewer_by_name():

    id = None
    while id == None:
        first_name = input("Please enter your first name: ")
        last_name = input("Please enter your last name: ")
        try:
            cursor.execute(insert_to_reviewer_stm, (first_name, last_name))
            id = cursor.lastrowid
        except:
            print("first name or last name too logn")
    return [(id, first_name, last_name)]


def film_exists(film_name):
    cursor.execute(f"SELECT * FROM film WHERE title = '{film_name}';")
    result = cursor.fetchall()
    return result


def is_rating_valid(rating):
    pattern = re.compile(r"^\d\.\d$")
    return pattern.match(rating)


def print_rating():
    cursor.execute("""
            select f.title, concat(rev.first_name, " ", rev.last_name), r.rating
            from rating as r, film as f, reviewer as rev
            where r.film_id = f.film_id AND r.reviewer_id = rev.reviewer_id
            limit 100            
        """)
    ratings = cursor.fetchall()
    for rate in ratings:
        print("Film name:", rate[0] + ",", "Full name:", rate[1] + ",", "Rating:", float(rate[2]))


insert_to_rating_stm = "INSERT INTO rating (film_id, reviewer_id, rating) VALUES (%s, %s, %s)"
update_to_rating_stm = "UPDATE rating SET rating = %s WHERE film_id = %s AND reviewer_id = %s"


def add_rating(film_id, reviewer_id, rating):
    cursor.execute(f"SELECT * FROM rating WHERE film_id = '{film_id}' AND reviewer_id = '{reviewer_id}';")
    result = cursor.fetchall()
    if result == []:
        cursor.execute(insert_to_rating_stm, (film_id, reviewer_id, rating))
    else:
        cursor.execute(update_to_rating_stm, (rating, film_id, reviewer_id))


create_reviewer_table()
create_rating_table()


result = None
while result == None:
    customer_id = input("Please enter your id: ")
    result = find_customer_by_id(customer_id)

if (result == []):
    result = add_reviewer_by_name()
print("Hello,", result[0][1], result[0][2] + ".")

film_name = input("Please enter film name to rate: ")
films = []
film_id = ""
while (films == []):
    films = film_exists(film_name)
    if (len(films) == 1):
        film_id = films[0][0]
        break
    if (len(films) > 1):
        ids = []
        for film in films:
            ids.append(film[0])
            print("film id:", film[0],",", "year:", film[3])
        chosen_id = input("Please pick movie id from the list above: ")
        if int(chosen_id) in ids:
            film_id = chosen_id
            break
    film_name = input("The film doesn't exists please enter another name: ")

rating = input("Please enter rating for the film: ")
while (not is_rating_valid(rating)):
    rating = input("Invalid rating please enter valid rating: ")

try:
    add_rating(film_id, result[0][0], rating)
except:
    print("couldn't add the rating")
print_rating()
