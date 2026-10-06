import pymysql

passwords_to_try = ["", "root", "password", "admin", "123456", "mysql"]
success = False

for pwd in passwords_to_try:
    try:
        conn = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password=pwd,
            connect_timeout=2
        )
        print(f"[SUCCESS] Connected to MySQL on 127.0.0.1:3306 with user='root' and password='{pwd if pwd else '(empty)'}'!")
        
        with conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES;")
            dbs = [row[0] for row in cursor.fetchall()]
            print(f"Databases present: {dbs}")
            
            cursor.execute("CREATE DATABASE IF NOT EXISTS smart_healthcare_db;")
            print("Database `smart_healthcare_db` verified/created successfully!")
            
        conn.close()
        success = True
        break
    except Exception as e:
        print(f"Failed with password '{pwd if pwd else '(empty)'}': {e}")

if not success:
    print("[INFO] Root credentials could not be guessed automatically.")
