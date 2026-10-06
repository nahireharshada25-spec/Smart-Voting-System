import psycopg2

def get_connection():
    connection = psycopg2.connect(
        host="localhost",
        database="online_voting",
        user="postgres",
        password="root",
        port="5432"
    )

    return connection


if __name__ == "__main__":

    try:
        connection = get_connection()

        print("Database connected successfully!")

        connection.close()

    except Exception as error:

        print("Database connection failed!")

        print(error)
