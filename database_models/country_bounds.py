import json
from database_models.db_connector import get_connection
from psycopg2.extras import RealDictCursor


def get_country_bounds(country_code=None):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if country_code:
            cursor.execute(
                'SELECT * FROM country_bounds WHERE country_code = %s',
                (country_code,)
            )
            result = cursor.fetchone()
        else:
            cursor.execute('SELECT * FROM country_bounds')
            result = cursor.fetchall()

        # Deserialize bounds from JSON string if needed
        if result:
            if isinstance(result, list):
                for row in result:
                    if isinstance(row.get('bounds'), str):
                        row['bounds'] = json.loads(row['bounds'])
            else:
                if isinstance(result.get('bounds'), str):
                    result['bounds'] = json.loads(result['bounds'])

        return {
            "status": "success",
            "data": result if result is not None else ([] if not country_code else None)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "message2": "error fetching country bounds"
        }

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def create_country_bounds(country_code, bounds):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Serialize bounds to JSON string for storage
        bounds_json = json.dumps(bounds) if not isinstance(bounds, str) else bounds

        cursor.execute("""
            INSERT INTO country_bounds (country_code, bounds)
            VALUES (%s, %s)
            RETURNING id, country_code, bounds
        """, (country_code, bounds_json))

        new_record = cursor.fetchone()
        conn.commit()

        # Deserialize bounds back for response
        if new_record and isinstance(new_record.get('bounds'), str):
            new_record['bounds'] = json.loads(new_record['bounds'])

        return {
            "status": "success",
            "data": new_record
        }

    except Exception as e:
        if conn: conn.rollback()
        return {
            "status": "error",
            "message": str(e),
            "message2": "error creating country bounds"
        }

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def update_country_bounds(country_id, country_code=None, bounds=None):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        update_fields = []
        values = []

        if country_code is not None:
            update_fields.append("country_code = %s")
            values.append(country_code)

        if bounds is not None:
            update_fields.append("bounds = %s")
            # Serialize bounds to JSON string for storage
            values.append(json.dumps(bounds) if not isinstance(bounds, str) else bounds)

        if not update_fields:
            return {
                "status": "error",
                "message": "No fields to update"
            }

        values.append(country_id)

        query = f"""
            UPDATE country_bounds
            SET {", ".join(update_fields)}
            WHERE id = %s
            RETURNING id, country_code, bounds;
        """

        cursor.execute(query, values)
        updated_record = cursor.fetchone()
        conn.commit()

        if not updated_record:
            return {
                "status": "error",
                "message": "Country bounds not found"
            }

        # Deserialize bounds back for response
        if updated_record and isinstance(updated_record.get('bounds'), str):
            updated_record['bounds'] = json.loads(updated_record['bounds'])

        return {
            "status": "success",
            "data": updated_record
        }

    except Exception as e:
        if conn: conn.rollback()
        return {
            "status": "error",
            "message": str(e),
            "message2": "error updating country bounds"
        }

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def delete_country_bounds(country_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            DELETE FROM country_bounds
            WHERE id = %s
            RETURNING id, country_code, bounds;
        """, (country_id,))

        deleted_record = cursor.fetchone()
        conn.commit()

        if not deleted_record:
            return {
                "status": "error",
                "message": "Country bounds not found"
            }

        return {
            "status": "success",
            "message": "Country bounds deleted successfully",
            "data": deleted_record
        }

    except Exception as e:
        if conn: conn.rollback()
        return {
            "status": "error",
            "message": str(e),
            "message2": "error deleting country bounds"
        }

    finally:
        if cursor: cursor.close()
        if conn: conn.close()