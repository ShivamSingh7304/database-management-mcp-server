from db_assistant.tools.db_tool.db_connection import get_db_connection
def search_records(
    table_name: str,
    search_term: str,
    limit: int = 20
):
    """
    Search records in a table using a search term.

    Args:
        table_name (str): Name of the table to search.
        search_term (str): Text to search for.
        limit (int): Maximum number of records to return.

    Returns:
        dict: Matching records.
    """

    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        limit = min(limit, 100)

        # Get text columns from the table
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
              AND data_type IN (
                  'character varying',
                  'character',
                  'text'
              )
            ORDER BY ordinal_position;
        """, (table_name,))

        columns = cursor.fetchall()

        if not columns:
            return {
                "success": False,
                "error": f"No searchable text columns found in table '{table_name}'."
            }

        column_names = [column[0] for column in columns]
        conditions = []
        params = []

        for column in column_names:
            conditions.append(f'"{column}" ILIKE %s')
            params.append(f"%{search_term}%")

        where_clause = " OR ".join(conditions)
        query = f"""
            SELECT *
            FROM "public"."{table_name}"
            WHERE {where_clause}
            LIMIT %s;
        """

        params.append(limit)

        cursor.execute(query, params)

        rows = cursor.fetchall()

        result_columns = [desc[0] for desc in cursor.description]

        results = [
            dict(zip(result_columns, row))
            for row in rows
        ]

        return {
            "success": True,
            "table_name": table_name,
            "search_term": search_term,
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