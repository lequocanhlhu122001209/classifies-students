"""Migrate data from old SQL Server database to new SQL Server database.

Source connection uses SQL_OLD_* env vars with fallback defaults:
- SQL_OLD_SERVER: (local)
- SQL_OLD_DATABASE: StudentClassification
- SQL_OLD_USERNAME / SQL_OLD_PASSWORD: empty (Windows auth)

Destination connection uses existing SQL_* env vars.
"""

import os
from typing import List

import pyodbc
from dotenv import load_dotenv


load_dotenv()


def _build_conn_str(prefix: str, default_server: str, default_database: str) -> str:
    server = os.getenv(f"{prefix}_SERVER", default_server)
    database = os.getenv(f"{prefix}_DATABASE", default_database)
    username = os.getenv(f"{prefix}_USERNAME", "")
    password = os.getenv(f"{prefix}_PASSWORD", "")
    driver = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")

    if username and password:
        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "TrustServerCertificate=yes;"
        )

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )


def _list_source_tables(src_conn: pyodbc.Connection) -> List[str]:
    cursor = src_conn.cursor()
    cursor.execute(
        """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
    )
    return [row[0] for row in cursor.fetchall()]


def _list_destination_tables(dst_conn: pyodbc.Connection) -> set:
    cursor = dst_conn.cursor()
    cursor.execute(
        """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_TYPE = 'BASE TABLE'
        """
    )
    return {row[0] for row in cursor.fetchall()}


def _sql_type_declaration(row: pyodbc.Row) -> str:
    data_type = row[1].lower()
    max_length = row[2]
    precision = row[3]
    scale = row[4]

    if data_type in {"varchar", "char", "varbinary", "binary"}:
        if max_length == -1:
            return f"{data_type}(max)"
        return f"{data_type}({max_length})"

    if data_type in {"nvarchar", "nchar"}:
        if max_length == -1:
            return f"{data_type}(max)"
        return f"{data_type}({max_length // 2})"

    if data_type in {"decimal", "numeric"}:
        return f"{data_type}({precision},{scale})"

    if data_type in {"datetime2", "datetimeoffset", "time"}:
        return f"{data_type}({scale})"

    return data_type


def _create_table_like_source(src_conn: pyodbc.Connection, dst_conn: pyodbc.Connection, table_name: str) -> None:
    src_cursor = src_conn.cursor()
    dst_cursor = dst_conn.cursor()

    src_cursor.execute(
        """
        SELECT
            c.name AS column_name,
            t.name AS data_type,
            c.max_length,
            c.precision,
            c.scale,
            c.is_nullable,
            c.is_identity
        FROM sys.columns c
        JOIN sys.types t ON c.user_type_id = t.user_type_id
        WHERE c.object_id = OBJECT_ID(?)
        ORDER BY c.column_id
        """,
        f"dbo.{table_name}",
    )
    columns = src_cursor.fetchall()
    if not columns:
        raise RuntimeError(f"Cannot read schema for table {table_name}")

    col_defs = []
    for col in columns:
        type_decl = _sql_type_declaration(col)
        column_name = col[0]
        is_nullable = col[5]
        is_identity = col[6]
        nullable_sql = "NULL" if is_nullable else "NOT NULL"
        identity_sql = " IDENTITY(1,1)" if is_identity else ""
        col_defs.append(f"[{column_name}] {type_decl}{identity_sql} {nullable_sql}")

    src_cursor.execute(
        """
        SELECT kc.COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kc
          ON tc.CONSTRAINT_NAME = kc.CONSTRAINT_NAME
         AND tc.TABLE_SCHEMA = kc.TABLE_SCHEMA
         AND tc.TABLE_NAME = kc.TABLE_NAME
        WHERE tc.TABLE_SCHEMA = 'dbo'
          AND tc.TABLE_NAME = ?
          AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
        ORDER BY kc.ORDINAL_POSITION
        """,
        table_name,
    )
    pk_cols = [f"[{r[0]}]" for r in src_cursor.fetchall()]
    if pk_cols:
        col_defs.append(
            f"CONSTRAINT [PK_{table_name}] PRIMARY KEY ({', '.join(pk_cols)})"
        )

    create_sql = f"CREATE TABLE dbo.[{table_name}] (\n  " + ",\n  ".join(col_defs) + "\n)"
    dst_cursor.execute(create_sql)
    dst_conn.commit()


def _table_has_identity(conn: pyodbc.Connection, table_name: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT 1
        FROM sys.identity_columns
        WHERE object_id = OBJECT_ID('dbo.[{table_name}]')
        """
    )
    return cursor.fetchone() is not None


def _copy_table_data(src_conn: pyodbc.Connection, dst_conn: pyodbc.Connection, table_name: str) -> int:
    src_cursor = src_conn.cursor()
    dst_cursor = dst_conn.cursor()

    src_cursor.execute(f"SELECT * FROM dbo.[{table_name}]")
    src_rows = src_cursor.fetchall()
    src_cols = [col[0] for col in src_cursor.description]
    if not src_cols:
        return 0

    dst_cursor.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """,
        table_name,
    )
    dst_cols = [row[0] for row in dst_cursor.fetchall()]

    common_cols = [c for c in dst_cols if c in src_cols]
    if not common_cols:
        print(f"Skipped {table_name}: no common columns")
        return 0

    src_idx = [src_cols.index(c) for c in common_cols]
    rows = [tuple(r[i] for i in src_idx) for r in src_rows]

    dst_cursor.execute(f"DELETE FROM dbo.[{table_name}]")

    if not rows:
        dst_conn.commit()
        return 0

    placeholders = ", ".join(["?"] * len(common_cols))
    columns_sql = ", ".join([f"[{c}]" for c in common_cols])
    insert_sql = f"INSERT INTO dbo.[{table_name}] ({columns_sql}) VALUES ({placeholders})"

    identity_on = _table_has_identity(dst_conn, table_name)
    if identity_on:
        dst_cursor.execute(
            f"""
            SELECT name
            FROM sys.identity_columns
            WHERE object_id = OBJECT_ID('dbo.[{table_name}]')
            """
        )
        identity_col = dst_cursor.fetchone()
        identity_name = identity_col[0] if identity_col else None
    else:
        identity_name = None

    need_identity_insert = identity_on and identity_name in common_cols
    if need_identity_insert:
        dst_cursor.execute(f"SET IDENTITY_INSERT dbo.[{table_name}] ON")

    dst_cursor.fast_executemany = True
    dst_cursor.executemany(insert_sql, rows)

    if need_identity_insert:
        dst_cursor.execute(f"SET IDENTITY_INSERT dbo.[{table_name}] OFF")

    dst_conn.commit()
    return len(rows)


def main() -> None:
    src_conn_str = _build_conn_str("SQL_OLD", "(local)", "StudentClassification")
    dst_conn_str = _build_conn_str("SQL", "(local)", "StudentClassification")

    print("Connecting source SQL...")
    src_conn = pyodbc.connect(src_conn_str)
    print("Connecting destination SQL...")
    dst_conn = pyodbc.connect(dst_conn_str)

    try:
        source_tables = _list_source_tables(src_conn)
        destination_tables = _list_destination_tables(dst_conn)

        missing_tables = [t for t in source_tables if t not in destination_tables]
        if missing_tables:
            print(f"Creating {len(missing_tables)} missing destination tables...")
            for table_name in missing_tables:
                if table_name.lower() == "sysdiagrams":
                    continue
                _create_table_like_source(src_conn, dst_conn, table_name)
                print(f"  Created table {table_name}")

            destination_tables = _list_destination_tables(dst_conn)

        tables_to_copy = [t for t in source_tables if t in destination_tables and t.lower() != "sysdiagrams"]
        skipped_tables = [t for t in source_tables if t not in destination_tables]

        print(f"Found {len(source_tables)} source tables")
        print(f"Will copy {len(tables_to_copy)} matching tables")

        if skipped_tables:
            print("Skipped tables (not found in destination):")
            for t in skipped_tables:
                print(f"  - {t}")

        # Disable FK checks during bulk copy, then re-enable.
        dst_cursor = dst_conn.cursor()
        dst_cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'")
        dst_conn.commit()

        total_rows = 0
        for table_name in tables_to_copy:
            copied = _copy_table_data(src_conn, dst_conn, table_name)
            total_rows += copied
            print(f"Copied {copied} rows from {table_name}")

        dst_cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL'")
        dst_conn.commit()

        print("Migration completed")
        print(f"Total rows copied: {total_rows}")
    finally:
        src_conn.close()
        dst_conn.close()


if __name__ == "__main__":
    main()
