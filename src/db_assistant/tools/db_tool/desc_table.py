from db_assistant.tools.db_tool.db_connection import get_db_connection


def describe_table(table_name: str):
    """
    Describe the structure of a table in the PostgreSQL database.

    Args:
        table_name (str): Name of the table to describe.

    Returns:
        dict: Table name and column information.
    """

    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))

        columns = cursor.fetchall()

        if not columns:
            return {
                "table_name": table_name,
                "columns": [],
                "message": f"Table '{table_name}' not found."
            }

        return {
            "table_name": table_name,
            "columns": [
                {
                    "column_name": column[0],
                    "data_type": column[1],
                    "is_nullable": column[2]
                }
                for column in columns
            ]
        }

    except Exception as e:
        print(f"Error describing table '{table_name}': {e}")
        return {}

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()