import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.database.config import SERVER_URL
from datetime import datetime

@pytest.mark.asyncio
async def test_inspect_all_databases(clean_db):
    log_lines = []
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_lines.append(f"Database Inspection Log - {timestamp}\n")

    # Connect to the server without specifying a database
    server_engine = create_async_engine(SERVER_URL, echo=False)
    async with server_engine.begin() as server_conn:
        # Get all databases
        result = await server_conn.execute(text("SHOW DATABASES"))
        databases = [row[0] for row in result.fetchall()]

    print("\n=== Database Inspection Summary ===\n")
    log_lines.append("\n=== Database Inspection Summary ===\n\n")
    for db in databases:
        print(f"Database: {db}")
        log_lines.append(f"Database: {db}\n")
        db_url = f"{SERVER_URL}/{db}"
        db_engine = create_async_engine(db_url, echo=False)
        try:
            async with db_engine.begin() as db_conn:
                table_query = text('''
                    SELECT
                        TABLE_NAME,
                        ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS SIZE_MB,
                        TABLE_ROWS
                    FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = :db
                    ORDER BY TABLE_NAME
                ''')
                table_result = await db_conn.execute(table_query, {"db": db})
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
            await db_engine.dispose()
        print()
        log_lines.append("\n")
    await server_engine.dispose()

    # Write log to file, overwriting each time
    with open("db_inspect.log", "w", encoding="utf-8") as log_file:
        log_file.writelines(log_lines) 