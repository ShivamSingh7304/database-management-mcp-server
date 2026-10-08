from db_assistant.tools.db_tool.db_connection import get_db_connection


def execute_read_query(query: str):
    """
    Execute a read-only SQL query on the connected PostgreSQL database.

    Args:
        query (str): SQL SELECT query.

    Returns:
        dict: Query results and metadata.
    """

    connection = get_db_connection()
    cursor = None

    try:

        normalized_query = query.strip().upper()

        # Only allow read operations
        if not (
            normalized_query.startswith("SELECT")
            or normalized_query.startswith("WITH")
        ):
            return {
                "success": False,
                "error": "Only SELECT and WITH queries are allowed."
            }

        cursor = connection.cursor()

        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]

        rows = cursor.fetchall()
        results = [
            dict(zip(columns, row))
            for row in rows
        ]

        return {
            "success": True,
            "columns": columns,
            "row_count": len(results),
            "data": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()