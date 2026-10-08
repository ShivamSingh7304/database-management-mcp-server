from db_assistant.tools.db_tool.db_connection import get_db_connection


def get_schema():
    """
    Get the complete schema of the PostgreSQL database.

    Returns:
        dict: Database schema containing tables, columns,
              primary keys and foreign keys.
    """

    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                table_name,
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)

        rows = cursor.fetchall()

        schema = {}

        for row in rows:
            table_name = row[0]
            column_name = row[1]
            data_type = row[2]
            is_nullable = row[3]

            if table_name not in schema:
                schema[table_name] = {
                    "columns": [],
                    "primary_keys": [],
                    "foreign_keys": []
                }

            schema[table_name]["columns"].append({
                "name": column_name,
                "data_type": data_type,
                "nullable": is_nullable == "YES"
            })

        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = 'public'
            ORDER BY tc.table_name;
        """)

        primary_keys = cursor.fetchall()

        for table_name, column_name in primary_keys:
            if table_name in schema:
                schema[table_name]["primary_keys"].append(column_name)

        cursor.execute("""
            SELECT
                tc.table_name AS source_table,
                kcu.column_name AS source_column,
                ccu.table_name AS target_table,
                ccu.column_name AS target_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'
            ORDER BY tc.table_name;
        """)

        foreign_keys = cursor.fetchall()

        for (
            source_table,
            source_column,
            target_table,
            target_column
        ) in foreign_keys:

            if source_table in schema:
                schema[source_table]["foreign_keys"].append({
                    "column": source_column,
                    "references_table": target_table,
                    "references_column": target_column
                })

        return {
            "success": True,
            "tables": schema
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