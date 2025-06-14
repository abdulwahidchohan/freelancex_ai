# Financial tracking
from backend.database import Database
from datetime import datetime
import logging
class EarningsTracker:
    def __init__(self, db_path=':memory:'):
        self.db = Database(db_path)
        self.db.connect()
        self._setup_logging()
        self._create_tables()

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _create_tables(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS earnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount DECIMAL(10,2) NOT NULL,
            source VARCHAR(255) NOT NULL,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute_query(create_table_query)

    def add_earning(self, amount, source):
        if not self.db.connected:
            self.logger.error("Cannot add earning: Database not connected.")
            return False
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            query = """
                INSERT INTO earnings (amount, source, date_added) 
                VALUES (?, ?, ?)
            """
            params = (amount, source, datetime.now())
            result = self.db.execute_query(query, params)
            
            if result and result.get("status") == "success":
                self.logger.info(f"Successfully added earning: ${amount:.2f} from {source}")
                return True
            return False
            
        except (ValueError, TypeError) as e:
            self.logger.error(f"Error adding earning: {str(e)}")
            return False

    def get_total_earnings(self, start_date=None, end_date=None):
        if not self.db.connected:
            self.logger.error("Cannot get total earnings: Database not connected.")
            return 0
        
        try:
            query = "SELECT COALESCE(SUM(amount), 0) as total FROM earnings"
            params = []
            
            if start_date or end_date:
                conditions = []
                if start_date:
                    conditions.append("date_added >= ?")
                    params.append(start_date)
                if end_date:
                    conditions.append("date_added <= ?")
                    params.append(end_date)
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            result = self.db.execute_query(query, params)
            
            if result and "rows" in result:
                return float(result["rows"][0]["total"])
            return 0
            
        except Exception as e:
            self.logger.error(f"Error getting total earnings: {str(e)}")
            return 0
