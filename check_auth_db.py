#!/usr/bin/env python3
"""
Check authentication database structure and contents
"""

import sqlite3
import os

def check_auth_database():
    db_path = "auth_mem.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return
    
    print(f"📁 Authentication Database: {db_path}")
    print(f"📊 File size: {os.path.getsize(db_path)} bytes")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("🗂️  Database Tables:")
        for table in tables:
            table_name = table[0]
            print(f"  📋 {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"    Columns:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"      - {col_name} ({col_type}){' PRIMARY KEY' if pk else ''}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"    Rows: {count}")
            
            # Show sample data
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print(f"    Sample data:")
                for i, row in enumerate(rows, 1):
                    print(f"      {i}. {row}")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {e}")

if __name__ == "__main__":
    check_auth_database()
