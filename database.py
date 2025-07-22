import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class Database:
    """Enhanced database wrapper for receipts with analytics support"""

    def __init__(self, db_file="my_receipts.db"):
        self.db_file = db_file
        self._setup_database()

    def _setup_database(self):
        """Create the receipts table if it doesn't exist"""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS receipts (
                    id INTEGER PRIMARY KEY,
                    filename TEXT NOT NULL,
                    vendor TEXT NOT NULL,
                    date DATE NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT,
                    text TEXT,
                    upload_date DATETIME,
                    file_hash TEXT UNIQUE
                )
            """)
            
            # Add comprehensive indexes for better performance with analytics
            conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON receipts(date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vendor ON receipts(vendor)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON receipts(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_amount ON receipts(amount)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_upload_date ON receipts(upload_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_file_hash ON receipts(file_hash)")
            
            # Composite indexes for common query patterns
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vendor_date ON receipts(vendor, date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category_date ON receipts(category, date)")

    def save_receipt(self, receipt):
        """Save a receipt to the database"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.execute("""
                    INSERT OR REPLACE INTO receipts 
                    (filename, vendor, date, amount, category, text, upload_date, file_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    receipt.filename, receipt.vendor, receipt.date,
                    receipt.amount, receipt.category, receipt.text,
                    receipt.upload_date, receipt.file_hash
                ))
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Database save failed: {e}")
            return None

    def get_receipts(self, limit=100, offset=0, order_by='date', ascending=False):
        """Get receipts with flexible ordering and pagination"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                
                # Validate order_by field to prevent SQL injection
                valid_fields = ['id', 'filename', 'vendor', 'date', 'amount', 'category', 'upload_date']
                if order_by not in valid_fields:
                    order_by = 'date'
                
                order_direction = 'ASC' if ascending else 'DESC'
                
                cursor = conn.execute(f"""
                    SELECT * FROM receipts 
                    ORDER BY {order_by} {order_direction}
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Database query failed: {e}")
            return []

    def get_all_receipts(self, limit=None):
        """Get all receipts for analytics processing"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                
                query = "SELECT * FROM receipts ORDER BY date DESC"
                params = []
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Database query failed: {e}")
            return []

    def search_receipts(self, query: str = None, vendor: str = None, date_from: str = None, 
                       date_to: str = None, amount_min: float = None, amount_max: float = None,
                       category: str = None):
        """
        Enhanced search receipts with multiple criteria.
        - query: Keyword search in filename, vendor, and text.
        - vendor: Pattern search for vendor.
        - category: Pattern search for category.
        - date_from/to: Range search for date.
        - amount_min/max: Range search for amount.
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                
                sql_query = "SELECT * FROM receipts WHERE 1=1"
                params = []
                
                if query:
                    sql_query += " AND (filename LIKE ? OR text LIKE ? OR vendor LIKE ?)"
                    params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
                
                if vendor:
                    sql_query += " AND vendor LIKE ?"
                    params.append(f"%{vendor}%")
                
                if category:
                    sql_query += " AND category LIKE ?"
                    params.append(f"%{category}%")
                    
                if date_from:
                    sql_query += " AND date >= ?"
                    params.append(date_from)
                
                if date_to:
                    sql_query += " AND date <= ?"
                    params.append(date_to)
                    
                if amount_min is not None:
                    sql_query += " AND amount >= ?"
                    params.append(amount_min)
                
                if amount_max is not None:
                    sql_query += " AND amount <= ?"
                    params.append(amount_max)
                
                sql_query += " ORDER BY date DESC"
                
                cursor = conn.execute(sql_query, params)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Search query failed: {e}")
            return []

    def get_spending_summary(self):
        """Get basic spending stats"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_receipts,
                        SUM(amount) as total_spent,
                        AVG(amount) as avg_amount,
                        MIN(amount) as min_amount,
                        MAX(amount) as max_amount,
                        MIN(date) as earliest_date,
                        MAX(date) as latest_date
                    FROM receipts
                """)
                row = cursor.fetchone()
                # Median calculation
                cursor2 = conn.execute("SELECT amount FROM receipts")
                amounts = [r[0] for r in cursor2.fetchall() if r[0] is not None]
                median_spend = 0
                if amounts:
                    amounts.sort()
                    n = len(amounts)
                    mid = n // 2
                    if n % 2 == 0:
                        median_spend = (amounts[mid - 1] + amounts[mid]) / 2
                    else:
                        median_spend = amounts[mid]
                if row:
                    return {
                        'total_receipts': row[0],
                        'total_spent': round(row[1] or 0, 2),
                        'avg_amount': round(row[2] or 0, 2),
                        'min_amount': round(row[3] or 0, 2),
                        'max_amount': round(row[4] or 0, 2),
                        'earliest_date': row[5],
                        'latest_date': row[6],
                        'median_spend': round(median_spend, 2)
                    }
        except sqlite3.Error as e:
            logger.error(f"Summary query failed: {e}")
        
        return {'error': 'Could not get summary'}

    def get_category_summary(self):
        """Get spending summary grouped by category"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT 
                        category,
                        COUNT(*) as receipt_count,
                        SUM(amount) as total_amount,
                        AVG(amount) as avg_amount,
                        MIN(amount) as min_amount,
                        MAX(amount) as max_amount
                    FROM receipts 
                    GROUP BY category
                    ORDER BY total_amount DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Category summary failed: {e}")
            return []

    def get_vendor_summary(self):
        """Get spending summary grouped by vendor"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT 
                        vendor,
                        COUNT(*) as receipt_count,
                        SUM(amount) as total_amount,
                        AVG(amount) as avg_amount,
                        MIN(date) as first_visit,
                        MAX(date) as last_visit
                    FROM receipts 
                    GROUP BY vendor
                    ORDER BY total_amount DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Vendor summary failed: {e}")
            return []

    def get_monthly_spending(self, limit_months=12):
        """Get spending summary by month"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT 
                        strftime('%Y-%m', date) as month,
                        COUNT(*) as receipt_count,
                        SUM(amount) as total_amount,
                        AVG(amount) as avg_amount
                    FROM receipts 
                    GROUP BY strftime('%Y-%m', date)
                    ORDER BY month DESC
                    LIMIT ?
                """, (limit_months,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Monthly spending query failed: {e}")
            return []

    def get_daily_spending(self, days=30):
        """Get spending summary by day for recent days"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT 
                        date,
                        COUNT(*) as receipt_count,
                        SUM(amount) as total_amount
                    FROM receipts 
                    WHERE date >= date('now', '-' || ? || ' days')
                    GROUP BY date
                    ORDER BY date DESC
                """, (days,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Daily spending query failed: {e}")
            return []

    def check_duplicate(self, file_hash):
        """Check if a receipt with the same hash already exists"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.execute("SELECT id, filename FROM receipts WHERE file_hash = ?", (file_hash,))
                result = cursor.fetchone()
                return result[1] if result else None
        except sqlite3.Error as e:
            logger.error(f"Duplicate check failed: {e}")
            return None

    def delete_receipt(self, receipt_id):
        """Delete a receipt by ID"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Delete failed: {e}")
            return False

    def update_receipt(self, receipt_id, updates):
        """Update specific fields of a receipt"""
        try:
            if not updates:
                return False
                
            # Build dynamic update query
            valid_fields = ['filename', 'vendor', 'date', 'amount', 'category', 'text']
            update_fields = []
            params = []
            
            for field, value in updates.items():
                if field in valid_fields:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
            
            if not update_fields:
                return False
            
            params.append(receipt_id)
            
            with sqlite3.connect(self.db_file) as conn:
                query = f"UPDATE receipts SET {', '.join(update_fields)} WHERE id = ?"
                cursor = conn.execute(query, params)
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            logger.error(f"Update failed: {e}")
            return False

    def get_database_stats(self):
        """Get comprehensive database statistics"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_records,
                        COUNT(DISTINCT vendor) as unique_vendors,
                        COUNT(DISTINCT category) as unique_categories,
                        MIN(date) as oldest_receipt,
                        MAX(date) as newest_receipt,
                        SUM(amount) as total_value
                    FROM receipts
                """)
                row = cursor.fetchone()
                if row:
                    return {
                        'total_records': row[0],
                        'unique_vendors': row[1],
                        'unique_categories': row[2],
                        'oldest_receipt': row[3],
                        'newest_receipt': row[4],
                        'total_value': round(row[5] or 0, 2)
                    }
        except sqlite3.Error as e:
            logger.error(f"Database stats failed: {e}")
            return {'error': 'Could not get database statistics'}

    def vacuum_database(self):
        """Optimize database by reclaiming unused space"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute("VACUUM")
                return True
        except sqlite3.Error as e:
            logger.error(f"Database vacuum failed: {e}")
            return False

    def clear_all_data(self):
        """Delete all records from the receipts table."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute("DELETE FROM receipts")
                conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Clear all data failed: {e}")
            return False

    def add_receipt(self, receipt_dict):
        """
        Add a receipt to the database from a dictionary.
        """
        from receipt_processor import Receipt
        allowed_fields = {f.name for f in Receipt.__dataclass_fields__.values()}
        filtered_dict = {k: v for k, v in receipt_dict.items() if k in allowed_fields}
        receipt = Receipt(**filtered_dict)
        return self.save_receipt(receipt)