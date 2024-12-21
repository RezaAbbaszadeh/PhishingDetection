import sqlite3
import os

def clean_sql_for_sqlite(input_path, output_path):
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            # Skip MySQL-specific comments and SET statements
            if line.strip().startswith(("/*!40101", "SET", "START TRANSACTION", "COMMIT")):
                continue
            line = line.replace("CHARACTER SET utf8mb3", "")
            line = line.replace("CHARACTER SET utf8", "")
            line = line.replace("COLLATE utf8_unicode_ci", "")
            line = line.replace("DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci", "")
            line = line.replace("AUTO_INCREMENT", "AUTOINCREMENT")
            outfile.write(line)

input_sql_file = 'dataset/index.sql'
cleaned_sql_file = 'dataset/cleaned_index.sql'

clean_sql_for_sqlite(input_sql_file, cleaned_sql_file)
print(f"Cleaned SQL file saved to {cleaned_sql_file}")


def execute_sql_file(file_path, connection):
    with open(file_path, 'r') as file:
        sql_commands = file.read()
    cursor = connection.cursor()
    
    try:
        for command in sql_commands.split(';'):
            command = command.strip()
            if command:
                cursor.execute(command)
        connection.commit()
        print("SQL file executed successfully!")
    except sqlite3.Error as err:
        print(f"Error: {err}")
        connection.rollback()
    finally:
        cursor.close()


database_path = 'dataset/database.db'
if os.path.exists(database_path):
    os.remove('dataset/database.db')
    
try:
    conn = sqlite3.connect(database_path)
    execute_sql_file(cleaned_sql_file, conn)
except sqlite3.Error as err:
    print(f"Connection error: {err}")
finally:
    if conn:
        conn.close()
