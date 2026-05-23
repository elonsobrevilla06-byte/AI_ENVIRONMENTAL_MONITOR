from database_models.db_connector import get_connection
from psycopg2.extras import RealDictCursor



def get_admin_accounts(admin_id=None):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if admin_id:
            cursor.execute("""
                SELECT id, username, email, created_at, is_active, password_hash
                FROM admin_accounts
                WHERE id = %s
            """, (admin_id,))
            result = cursor.fetchone()
        else:
            cursor.execute("""
                SELECT id, username, email, created_at, is_active, password_hash
                FROM admin_accounts
                ORDER BY created_at DESC
            """)
            result = cursor.fetchall()

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "message2": "error fetching admin accounts"
        }

    finally:
        cursor.close()
        conn.close()



def create_admin_account(username, email, password_hash):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            INSERT INTO admin_accounts (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, username, email, created_at, is_active
        """, (username, email, password_hash))

        new_admin = cursor.fetchone()
        conn.commit()

        return {
            "status": "success",
            "data": new_admin
        }

    except Exception as e:
        conn.rollback()
        return {
            "status": "error",
            "message": str(e),
            "message2": "error creating admin account"
        }

    finally:
        cursor.close()
        conn.close()



def update_admin_account(admin_id, fields):
    try:
        conn = get_connection()
        cur = conn.cursor()

        set_clause = ", ".join([f"{key} = %s" for key in fields.keys()])
        values = list(fields.values())

        values.append(admin_id)

        query = f"""
            UPDATE admin_accounts
            SET {set_clause}
            WHERE id = %s
            RETURNING id, username, email, is_active;
        """

        cur.execute(query, values)
        updated_admin = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        if not updated_admin:
            return {
                "status": "error",
                "message": "Admin not found"
            }

        return {
            "status": "success",
            "message": "Admin updated successfully",
            "data": {
                "id": updated_admin[0],
                "username": updated_admin[1],
                "email": updated_admin[2],
                "is_active": updated_admin[3],
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    
def delete_admin_account(admin_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        query = """
            DELETE FROM admin_accounts
            WHERE id = %s
            RETURNING id, username, email;
        """

        cur.execute(query, (admin_id,))
        deleted_admin = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        if not deleted_admin:
            return {
                "status": "error",
                "message": "Admin not found"
            }

        return {
            "status": "success",
            "message": "Admin deleted successfully",
            "data": {
                "id": deleted_admin[0],
                "username": deleted_admin[1],
                "email": deleted_admin[2]
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }