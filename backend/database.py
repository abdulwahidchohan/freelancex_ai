#!/usr/bin/env python3
"""
FreelanceX.AI Database Manager
Comprehensive data persistence layer with user profiles, memory management, and security
Features: User data storage, long-term memory, audit logging, encryption
"""

import asyncio
import sqlite3
import aiosqlite
import json
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncpg
from cryptography.fernet import Fernet
import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """Comprehensive user profile for FreelanceX.AI"""
    user_id: str
    username: str
    email: str
    password_hash: str
    first_name: str
    last_name: str
    skills: List[str]
    experience_years: int
    preferred_hourly_rate: float
    location: str
    time_zone: str
    work_schedule: Dict[str, Any]
    goals: List[str]
    preferences: Dict[str, Any]
    subscription_tier: str = "free"
    created_at: str = None
    last_updated: str = None
    last_login: str = None
    is_active: bool = True

@dataclass
class MemoryEntry:
    """Long-term memory entry for user interactions"""
    memory_id: str
    user_id: str
    agent_name: str
    interaction_type: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    importance_score: float
    created_at: str
    expires_at: Optional[str] = None

@dataclass
class AuditLog:
    """Audit log entry for system transparency"""
    log_id: str
    user_id: str
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    timestamp: str
    success: bool

class DatabaseManager:
    """
    Comprehensive database manager for FreelanceX.AI
    Handles user data, memory storage, audit logging, and encryption
    """
    
    def __init__(self, db_path: str = "freelancex.db", encryption_key: str = None):
        self.db_path = Path(db_path)
        self.connected = False
        self.connection = None
        
        # Encryption setup
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Database configuration
        self.max_retries = 3
        self.retry_delay = 1
        self._transaction_level = 0
        
        logger.info(f"DatabaseManager initialized with path: {self.db_path}")

    async def connect(self) -> bool:
        """Establish database connection and initialize schema"""
        try:
            # Create database directory if it doesn't exist
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to SQLite database
            self.connection = await aiosqlite.connect(str(self.db_path))
            self.connection.row_factory = aiosqlite.Row
            
            # Initialize database schema
            await self._initialize_schema()
            
            self.connected = True
            logger.info("Database connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            self.connected = False
            return False

    async def disconnect(self) -> bool:
        """Safely close database connection"""
        try:
            if self.connection:
                await self.connection.close()
                self.connected = False
                logger.info("Database disconnected successfully")
            return True
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")
            return False

    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connected

    async def _initialize_schema(self):
        """Initialize database schema with all required tables"""
        
        # Users table
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                skills TEXT,  -- JSON encoded
                experience_years INTEGER DEFAULT 0,
                preferred_hourly_rate REAL DEFAULT 0.0,
                location TEXT,
                time_zone TEXT DEFAULT 'UTC',
                work_schedule TEXT,  -- JSON encoded
                goals TEXT,  -- JSON encoded
                preferences TEXT,  -- JSON encoded (encrypted)
                subscription_tier TEXT DEFAULT 'free',
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                last_login TEXT,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # User memory table for long-term memory
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS user_memory (
                memory_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                content TEXT NOT NULL,  -- JSON encoded (encrypted)
                metadata TEXT,  -- JSON encoded
                importance_score REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Job search history
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS job_search_history (
                search_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                search_query TEXT NOT NULL,
                filters TEXT,  -- JSON encoded
                results_count INTEGER DEFAULT 0,
                search_timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Agent interactions log
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS agent_interactions (
                interaction_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                action TEXT NOT NULL,
                request_data TEXT,  -- JSON encoded
                response_data TEXT,  -- JSON encoded
                execution_time REAL DEFAULT 0.0,
                success BOOLEAN DEFAULT 1,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Audit logs
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id TEXT PRIMARY KEY,
                user_id TEXT,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                details TEXT,  -- JSON encoded
                ip_address TEXT,
                user_agent TEXT,
                timestamp TEXT NOT NULL,
                success BOOLEAN DEFAULT 1
            )
        """)
        
        # System metrics
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                metric_id TEXT PRIMARY KEY,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metadata TEXT,  -- JSON encoded
                timestamp TEXT NOT NULL
            )
        """)
        
        # Create indexes for better performance
        await self._create_indexes()
        
        await self.connection.commit()
        logger.info("Database schema initialized successfully")

    async def _create_indexes(self):
        """Create database indexes for improved performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_memory_user_id ON user_memory(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_memory_agent ON user_memory(agent_name)",
            "CREATE INDEX IF NOT EXISTS idx_memory_created_at ON user_memory(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_job_search_user_id ON job_search_history(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON agent_interactions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_interactions_agent ON agent_interactions(agent_name)",
            "CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_logs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_name ON system_metrics(metric_name)"
        ]
        
        for index_sql in indexes:
            await self.connection.execute(index_sql)

    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(data.encode()).decode()

    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    async def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Create a new user profile"""
        try:
            user_id = secrets.token_urlsafe(16)
            current_time = datetime.now().isoformat()
            
            # Hash password
            password_hash = self._hash_password(user_data['password'])
            
            # Encrypt sensitive preferences
            preferences_json = json.dumps(user_data.get('preferences', {}))
            encrypted_preferences = self._encrypt_data(preferences_json)
            
            await self.connection.execute("""
                INSERT INTO users (
                    user_id, username, email, password_hash, first_name, last_name,
                    skills, experience_years, preferred_hourly_rate, location, time_zone,
                    work_schedule, goals, preferences, subscription_tier, created_at, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                user_data['username'],
                user_data['email'],
                password_hash,
                user_data['first_name'],
                user_data['last_name'],
                json.dumps(user_data.get('skills', [])),
                user_data.get('experience_years', 0),
                user_data.get('preferred_hourly_rate', 0.0),
                user_data.get('location', ''),
                user_data.get('time_zone', 'UTC'),
                json.dumps(user_data.get('work_schedule', {})),
                json.dumps(user_data.get('goals', [])),
                encrypted_preferences,
                user_data.get('subscription_tier', 'free'),
                current_time,
                current_time
            ))
            
            await self.connection.commit()
            
            # Log user creation
            await self._log_audit(
                user_id=user_id,
                action="USER_CREATED",
                resource="users",
                details={"username": user_data['username']},
                success=True
            )
            
            logger.info(f"User created successfully: {user_data['username']}")
            return user_id
            
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            await self.connection.rollback()
            return None

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            cursor = await self.connection.execute(
                "SELECT * FROM users WHERE username = ? AND is_active = 1",
                (username,)
            )
            row = await cursor.fetchone()
            
            if row:
                user_data = dict(row)
                
                # Decrypt sensitive data
                if user_data['preferences']:
                    try:
                        decrypted_prefs = self._decrypt_data(user_data['preferences'])
                        user_data['preferences'] = json.loads(decrypted_prefs)
                    except:
                        user_data['preferences'] = {}
                
                # Parse JSON fields
                user_data['skills'] = json.loads(user_data['skills'] or '[]')
                user_data['work_schedule'] = json.loads(user_data['work_schedule'] or '{}')
                user_data['goals'] = json.loads(user_data['goals'] or '[]')
                
                return user_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by username: {str(e)}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            cursor = await self.connection.execute(
                "SELECT * FROM users WHERE user_id = ? AND is_active = 1",
                (user_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                user_data = dict(row)
                
                # Decrypt and parse data similar to get_user_by_username
                if user_data['preferences']:
                    try:
                        decrypted_prefs = self._decrypt_data(user_data['preferences'])
                        user_data['preferences'] = json.loads(decrypted_prefs)
                    except:
                        user_data['preferences'] = {}
                
                user_data['skills'] = json.loads(user_data['skills'] or '[]')
                user_data['work_schedule'] = json.loads(user_data['work_schedule'] or '{}')
                user_data['goals'] = json.loads(user_data['goals'] or '[]')
                
                return user_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by ID: {str(e)}")
            return None

    async def update_user_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            current_time = datetime.now().isoformat()
            await self.connection.execute(
                "UPDATE users SET last_login = ? WHERE user_id = ?",
                (current_time, user_id)
            )
            await self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update user login: {str(e)}")
            return False

    async def store_memory(self, memory_entry: MemoryEntry) -> bool:
        """Store long-term memory entry"""
        try:
            # Encrypt sensitive content
            content_json = json.dumps(memory_entry.content)
            encrypted_content = self._encrypt_data(content_json)
            
            await self.connection.execute("""
                INSERT INTO user_memory (
                    memory_id, user_id, agent_name, interaction_type,
                    content, metadata, importance_score, created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory_entry.memory_id,
                memory_entry.user_id,
                memory_entry.agent_name,
                memory_entry.interaction_type,
                encrypted_content,
                json.dumps(memory_entry.metadata),
                memory_entry.importance_score,
                memory_entry.created_at,
                memory_entry.expires_at
            ))
            
            await self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to store memory: {str(e)}")
            return False

    async def get_user_memories(self, user_id: str, agent_name: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve user memories with optional agent filter"""
        try:
            if agent_name:
                cursor = await self.connection.execute("""
                    SELECT * FROM user_memory 
                    WHERE user_id = ? AND agent_name = ? 
                    AND (expires_at IS NULL OR expires_at > ?)
                    ORDER BY importance_score DESC, created_at DESC 
                    LIMIT ?
                """, (user_id, agent_name, datetime.now().isoformat(), limit))
            else:
                cursor = await self.connection.execute("""
                    SELECT * FROM user_memory 
                    WHERE user_id = ? 
                    AND (expires_at IS NULL OR expires_at > ?)
                    ORDER BY importance_score DESC, created_at DESC 
                    LIMIT ?
                """, (user_id, datetime.now().isoformat(), limit))
            
            rows = await cursor.fetchall()
            memories = []
            
            for row in rows:
                memory = dict(row)
                
                # Decrypt content
                try:
                    decrypted_content = self._decrypt_data(memory['content'])
                    memory['content'] = json.loads(decrypted_content)
                except:
                    memory['content'] = {}
                
                memory['metadata'] = json.loads(memory['metadata'] or '{}')
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get user memories: {str(e)}")
            return []

    async def log_agent_interaction(self, user_id: str, agent_name: str, action: str, 
                                  request_data: Dict[str, Any], response_data: Dict[str, Any],
                                  execution_time: float, success: bool) -> bool:
        """Log agent interaction for analytics"""
        try:
            interaction_id = secrets.token_urlsafe(16)
            
            await self.connection.execute("""
                INSERT INTO agent_interactions (
                    interaction_id, user_id, agent_name, action,
                    request_data, response_data, execution_time, success, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                interaction_id,
                user_id,
                agent_name,
                action,
                json.dumps(request_data),
                json.dumps(response_data),
                execution_time,
                success,
                datetime.now().isoformat()
            ))
            
            await self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to log agent interaction: {str(e)}")
            return False

    async def _log_audit(self, user_id: str, action: str, resource: str, 
                        details: Dict[str, Any], ip_address: str = None,
                        user_agent: str = None, success: bool = True) -> bool:
        """Log audit entry for transparency"""
        try:
            log_id = secrets.token_urlsafe(16)
            
            await self.connection.execute("""
                INSERT INTO audit_logs (
                    log_id, user_id, action, resource, details,
                    ip_address, user_agent, timestamp, success
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_id,
                user_id,
                action,
                resource,
                json.dumps(details),
                ip_address,
                user_agent,
                datetime.now().isoformat(),
                success
            ))
            
            await self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to log audit entry: {str(e)}")
            return False

    async def cleanup_expired_memories(self) -> int:
        """Clean up expired memory entries"""
        try:
            cursor = await self.connection.execute("""
                DELETE FROM user_memory 
                WHERE expires_at IS NOT NULL AND expires_at <= ?
            """, (datetime.now().isoformat(),))
            
            rows_deleted = cursor.rowcount
            await self.connection.commit()
            
            if rows_deleted > 0:
                logger.info(f"Cleaned up {rows_deleted} expired memory entries")
            
            return rows_deleted
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired memories: {str(e)}")
            return 0

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        try:
            metrics = {}
            
            # User metrics
            cursor = await self.connection.execute("SELECT COUNT(*) as total_users FROM users WHERE is_active = 1")
            row = await cursor.fetchone()
            metrics['total_users'] = row['total_users']
            
            # Active users (logged in within last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            cursor = await self.connection.execute(
                "SELECT COUNT(*) as active_users FROM users WHERE last_login >= ? AND is_active = 1",
                (thirty_days_ago,)
            )
            row = await cursor.fetchone()
            metrics['active_users'] = row['active_users']
            
            # Memory entries
            cursor = await self.connection.execute("SELECT COUNT(*) as total_memories FROM user_memory")
            row = await cursor.fetchone()
            metrics['total_memories'] = row['total_memories']
            
            # Agent interactions
            cursor = await self.connection.execute("SELECT COUNT(*) as total_interactions FROM agent_interactions")
            row = await cursor.fetchone()
            metrics['total_interactions'] = row['total_interactions']
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {str(e)}")
            return {}

# Legacy compatibility
class Database(DatabaseManager):
    """Legacy Database class for backward compatibility"""
    
    def __init__(self, db_path=':memory:', max_retries=3, retry_delay=1):
        super().__init__(db_path if db_path != ':memory:' else 'freelancex.db')
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def connect(self):
        """Legacy sync connect method"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(super().connect())

    def disconnect(self):
        """Legacy sync disconnect method"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(super().disconnect())

    def execute_query(self, query, params=None):
        """Legacy query execution"""
        # This is a placeholder for backward compatibility
        return {
            "status": "success",
            "rows_affected": 1,
            "parameters": params
        }

    def begin_transaction(self):
        self._transaction_level += 1
        return True

    def commit(self):
        if self._transaction_level > 0:
            self._transaction_level -= 1
        return True

    def rollback(self):
        if self._transaction_level > 0:
            self._transaction_level -= 1
        return True
