import psycopg2

def get_connection():
    return psycopg2.connect(
        host = "localhost",
        user = "postgres",
        password = "masteryimain31",
        database = "environmental_monitoring"
    )

def test_connection():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT current_database();")
    db_name = cursor.fetchone()
    print(f"Floatingbar DB Connected : {db_name} ")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_connection()