"""
Database inspection test for the Quest of Life Backend API.
Inspects all databases and tables on the server and logs their structure and size.
"""
import pytest
from sqlalchemy import text, create_engine
from src.database.config import SYNC_SERVER_URL
from datetime import datetime

def test_inspect_all_databases(test_database) -> None:
    """
    Inspects all databases and their tables, printing and logging their structure and size.
    Used for manual inspection and debugging of the test database environment.
    """
    log_lines = []
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_lines.append(f"Database Inspection Log - {timestamp}\n")

    # Connect to the server without specifying a database
    server_engine = create_engine(SYNC_SERVER_URL, echo=False)
    with server_engine.connect() as server_conn:
        # Get all databases
        result = server_conn.execute(text("SHOW DATABASES"))
        databases = [row[0] for row in result.fetchall()]

    print("\n=== Database Inspection Summary ===\n")
    log_lines.append("\n=== Database Inspection Summary ===\n\n")
    for db in databases:
        print(f"Database: {db}")
        log_lines.append(f"Database: {db}\n")
        db_url = f"{SYNC_SERVER_URL}/{db}"
        db_engine = create_engine(db_url, echo=False)
        try:
            with db_engine.connect() as db_conn:
                table_query = text('''
                    SELECT
                        TABLE_NAME,
                        ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS SIZE_MB,
                        TABLE_ROWS
                    FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = :db
                    ORDER BY TABLE_NAME
                ''')
                table_result = db_conn.execute(table_query, {"db": db})
                tables = table_result.fetchall()
                if not tables:
                    print("  (No tables or no access)")
                    log_lines.append("  (No tables or no access)\n")
                else:
                    for table_name, size_mb, table_rows in tables:
                        line = f"  Table: {table_name:30} | Size: {size_mb:8} MB | Rows (approx): {table_rows}"
                        print(line)
                        log_lines.append(line + "\n")
        except Exception as e:
            err_line = f"  [Could not inspect tables: {e}]"
            print(err_line)
            log_lines.append(err_line + "\n")
        finally:
            db_engine.dispose()
        print()
        log_lines.append("\n")
    server_engine.dispose()

    # Write log to file, overwriting each time
    with open("db_inspect.log", "w", encoding="utf-8") as log_file:
        log_file.writelines(log_lines) 