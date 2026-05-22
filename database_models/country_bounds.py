from database_models.db_connector import get_connection
from psycopg2.extras import RealDictCursor


def get_country_bounds(country_code=None):
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

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "message2": "error fetching country bounds"
        }

    finally:
        cursor.close()
        conn.close()