import psycopg


def get_db_connection():
    """
    Establish a connection to the PostgreSQL database.

    Returns:
        psycopg.Connection: A database connection object.
    """
    try:
        connection = psycopg.connect(
            host="your_host",
            port=5432,
            user="your_username",
            password="your_password",
            dbname="your_database"
        )

        return connection

    except psycopg.Error as err:
        print(f"Error connecting to the database: {err}")
        return None