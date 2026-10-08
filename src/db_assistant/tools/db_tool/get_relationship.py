from db_assistant.tools.db_tool.db_connection import get_db_connection


def get_relationships():
    """
    Get foreign-key relationships between tables
    in the PostgreSQL database.

    Returns:
        dict: Database table relationships.
    """

    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                tc.table_name AS source_table,
                kcu.column_name AS source_column,
                ccu.table_name AS target_table,
                ccu.column_name AS target_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'
            ORDER BY tc.table_name;
        """)

        relationships = cursor.fetchall()

        return {
            "success": True,
            "relationships": [
                {
                    "source_table": row[0],
                    "source_column": row[1],
                    "target_table": row[2],
                    "target_column": row[3]
                }
                for row in relationships
            ]
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