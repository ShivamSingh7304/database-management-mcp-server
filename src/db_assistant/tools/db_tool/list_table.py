from src.db_assistant.tools.db_tool.db_connection import get_db_connection


def list_tables():
    """
    List all tables in the PostgreSQL database.

    Returns:
        list[str]: A list of table names.
    """
    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()

        return [table[0] for table in tables]

    except Exception as e:
        print(f"Error listing tables: {e}")
        return []

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()