# Data persistence
class Database:
    def __init__(self, db_path=':memory:', max_retries=3, retry_delay=1):
        self.db_path = db_path
        self.connected = False
        self.connection = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._transaction_level = 0

    def connect(self):
        """Establishes connection to database with retry mechanism"""
        print(f"Connecting to the database at {self.db_path}...")
        
        for attempt in range(self.max_retries):
            try:
                # Example: self.connection = sqlite3.connect(self.db_path)
                self.connected = True
                print(f"Database connection successful on attempt {attempt + 1}.")
                return True
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                print(f"Database connection failed after {self.max_retries} attempts")
                self.connected = False
                return False

    def disconnect(self):
        """Safely closes database connection"""
        if not self.connected:
            return False
            
        try:
            if self._transaction_level > 0:
                # Example: self.connection.rollback()
                print("Warning: Disconnecting with active transactions. Rolling back.")
            
            print("Disconnecting from the database...")
            # Example: self.connection.close()
            self.connected = False
            self.connection = None
            print("Database disconnected successfully.")
            return True
        except Exception as e:
            print(f"Error during disconnect: {e}")
            return False

    def execute_query(self, query, params=None):
        """Executes a database query with parameter binding support"""
        if not self.connected:
            raise ConnectionError("Cannot execute query: Not connected to database.")

        try:
            print(f"Executing query: {query}")
            if params:
                print(f"With parameters: {params}")
            # Example: 
            # cursor = self.connection.cursor()
            # result = cursor.execute(query, params)
            # self.connection.commit()
            # return result
            
            # Simulate query execution
            return {
                "status": "success",
                "rows_affected": 1,
                "parameters": params
            }
        except Exception as e:
            print(f"Query execution failed: {e}")
            # Example: self.connection.rollback()
            raise

    def begin_transaction(self):
        """Begins a new database transaction"""
        if not self.connected:
            raise ConnectionError("Cannot start transaction: Not connected to database.")
        self._transaction_level += 1
        # Example: self.connection.begin()
        return True

    def commit(self):
        """Commits the current transaction"""
        if not self.connected:
            raise ConnectionError("Cannot commit: Not connected to database.")
        if self._transaction_level > 0:
            self._transaction_level -= 1
            # Example: self.connection.commit()
            return True
        return False

    def rollback(self):
        """Rolls back the current transaction"""
        if not self.connected:
            raise ConnectionError("Cannot rollback: Not connected to database.")
        if self._transaction_level > 0:
            self._transaction_level -= 1
            # Example: self.connection.rollback()
            return True
        return False
