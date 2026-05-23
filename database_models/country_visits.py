from database_models.db_connector import get_connection
from psycopg2.extras import RealDictCursor

def get_country_visits():
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT 
                country_code,
                COUNT(*) AS visit_count
            FROM country_visits
            GROUP BY country_code
            ORDER BY visit_count DESC
        """)

        result = cursor.fetchall()

        return {
            "status": "success",
            "data": [dict(row) for row in result]  # ← convert RealDictRow → plain dict
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "message2": "error fetching country visits"
        }

    finally:
        cursor.close()
        conn.close()

def get_today_country_visits():
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT 
                country_code,
                COUNT(*) AS visit_count
            FROM country_visits
            WHERE DATE(visited_at) = CURRENT_DATE
            GROUP BY country_code
            ORDER BY visit_count DESC
        """)

        result = cursor.fetchall()

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        cursor.close()
        conn.close()

def get_this_month_country_visits():
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT 
                country_code,
                COUNT(*) AS visit_count
            FROM country_visits
            WHERE DATE_TRUNC('month', visited_at) = DATE_TRUNC('month', CURRENT_DATE)
            GROUP BY country_code
            ORDER BY visit_count DESC
        """)

        result = cursor.fetchall()

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        cursor.close()
        conn.close()

def add_country_visit(country_code):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            INSERT INTO country_visits (country_code)
            VALUES (%s)
            RETURNING id, country_code, visited_at
        """, (country_code,))

        new_visit = cursor.fetchone()
        conn.commit()

        return {
            "status": "success",
            "data": new_visit
        }

    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": str(e),
            "message2": "error adding country visit"
        }

    finally:
        cursor.close()
        conn.close()