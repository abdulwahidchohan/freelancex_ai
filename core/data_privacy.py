#!/usr/bin/env python3
"""
FreelanceX.AI Data Privacy & Governance
Data encryption, privacy settings, audit logs, and GDPR compliance
"""

import asyncio
import logging
import json
import hashlib
import hmac
import base64
import sqlite3
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import aiosqlite
from enum import Enum
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

class PrivacyLevel(Enum):
    """Privacy levels for data handling"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class DataCategory(Enum):
    """Categories of data for privacy management"""
    PERSONAL_INFO = "personal_info"
    FINANCIAL_DATA = "financial_data"
    INTERACTION_HISTORY = "interaction_history"
    SYSTEM_LOGS = "system_logs"
    ANALYTICS = "analytics"
    RESEARCH_DATA = "research_data"

@dataclass
class PrivacySettings:
    """User privacy settings"""
    user_id: str
    data_retention_days: int
    allow_analytics: bool
    allow_research: bool
    allow_marketing: bool
    data_export_enabled: bool
    auto_delete_enabled: bool
    encryption_level: PrivacyLevel
    last_updated: datetime

@dataclass
class AuditLog:
    """Audit log entry"""
    log_id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    success: bool
    details: Dict[str, Any]

@dataclass
class DataRetentionPolicy:
    """Data retention policy"""
    category: DataCategory
    retention_days: int
    auto_delete: bool
    encryption_required: bool
    access_logging: bool

class DataPrivacyGovernance:
    """
    Comprehensive data privacy and governance system for FreelanceX.AI
    Handles encryption, privacy settings, audit logs, and GDPR compliance
    """
    
    def __init__(self, db_path: str = "data/freelancex_privacy.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("FreelanceX.DataPrivacy")
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        asyncio.create_task(self._initialize_database())
        
        # Encryption setup
        self.encryption_key = self._load_or_generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Privacy policies
        self.retention_policies = self._setup_retention_policies()
        
        # Audit logging
        self.audit_buffer: List[AuditLog] = []
        self.audit_flush_interval = 30  # seconds
        self.last_audit_flush = datetime.now()
        
        # Start background tasks
        asyncio.create_task(self._start_audit_flush_loop())
        asyncio.create_task(self._start_data_cleanup_loop())
        
        self.logger.info("Data Privacy & Governance system initialized")
    
    def _load_or_generate_encryption_key(self) -> bytes:
        """Load existing encryption key or generate a new one"""
        key_file = Path("data/encryption.key")
        
        if key_file.exists():
            try:
                with open(key_file, "rb") as f:
                    return f.read()
            except Exception as e:
                self.logger.warning(f"Failed to load encryption key: {str(e)}")
        
        # Generate new key
        key_file.parent.mkdir(parents=True, exist_ok=True)
        new_key = Fernet.generate_key()
        
        try:
            with open(key_file, "wb") as f:
                f.write(new_key)
            self.logger.info("Generated new encryption key")
        except Exception as e:
            self.logger.error(f"Failed to save encryption key: {str(e)}")
        
        return new_key
    
    def _setup_retention_policies(self) -> Dict[DataCategory, DataRetentionPolicy]:
        """Setup default data retention policies"""
        return {
            DataCategory.PERSONAL_INFO: DataRetentionPolicy(
                category=DataCategory.PERSONAL_INFO,
                retention_days=2555,  # 7 years
                auto_delete=True,
                encryption_required=True,
                access_logging=True
            ),
            DataCategory.FINANCIAL_DATA: DataRetentionPolicy(
                category=DataCategory.FINANCIAL_DATA,
                retention_days=2555,  # 7 years
                auto_delete=True,
                encryption_required=True,
                access_logging=True
            ),
            DataCategory.INTERACTION_HISTORY: DataRetentionPolicy(
                category=DataCategory.INTERACTION_HISTORY,
                retention_days=365,  # 1 year
                auto_delete=True,
                encryption_required=False,
                access_logging=True
            ),
            DataCategory.SYSTEM_LOGS: DataRetentionPolicy(
                category=DataCategory.SYSTEM_LOGS,
                retention_days=90,  # 3 months
                auto_delete=True,
                encryption_required=False,
                access_logging=True
            ),
            DataCategory.ANALYTICS: DataRetentionPolicy(
                category=DataCategory.ANALYTICS,
                retention_days=730,  # 2 years
                auto_delete=True,
                encryption_required=False,
                access_logging=True
            ),
            DataCategory.RESEARCH_DATA: DataRetentionPolicy(
                category=DataCategory.RESEARCH_DATA,
                retention_days=1095,  # 3 years
                auto_delete=True,
                encryption_required=False,
                access_logging=True
            )
        }
    
    async def _initialize_database(self):
        """Initialize privacy database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Privacy settings table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS privacy_settings (
                    user_id TEXT PRIMARY KEY,
                    data_retention_days INTEGER DEFAULT 365,
                    allow_analytics BOOLEAN DEFAULT 1,
                    allow_research BOOLEAN DEFAULT 1,
                    allow_marketing BOOLEAN DEFAULT 0,
                    data_export_enabled BOOLEAN DEFAULT 1,
                    auto_delete_enabled BOOLEAN DEFAULT 1,
                    encryption_level TEXT DEFAULT 'confidential',
                    last_updated TEXT NOT NULL
                )
            """)
            
            # Audit logs table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    log_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    success BOOLEAN NOT NULL,
                    details TEXT
                )
            """)
            
            # Encrypted data table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS encrypted_data (
                    data_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    encrypted_data TEXT NOT NULL,
                    encryption_level TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT
                )
            """)
            
            # Data access logs table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS data_access_logs (
                    access_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    data_id TEXT NOT NULL,
                    access_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    success BOOLEAN NOT NULL,
                    FOREIGN KEY (data_id) REFERENCES encrypted_data (data_id)
                )
            """)
            
            # GDPR requests table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS gdpr_requests (
                    request_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    request_type TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    details TEXT
                )
            """)
            
            await db.commit()
            self.logger.info("Privacy database tables initialized")
    
    async def _start_audit_flush_loop(self):
        """Periodically flush audit logs to database"""
        while True:
            try:
                await asyncio.sleep(self.audit_flush_interval)
                await self._flush_audit_logs()
            except Exception as e:
                self.logger.error(f"Audit flush error: {str(e)}")
    
    async def _start_data_cleanup_loop(self):
        """Periodically clean up expired data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._cleanup_expired_data()
            except Exception as e:
                self.logger.error(f"Data cleanup error: {str(e)}")
    
    def encrypt_data(self, data: str, privacy_level: PrivacyLevel = PrivacyLevel.CONFIDENTIAL) -> str:
        """Encrypt sensitive data"""
        try:
            # Add privacy level to data for verification
            data_with_level = f"{privacy_level.value}:{data}"
            encrypted_bytes = self.cipher_suite.encrypt(data_with_level.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            decrypted_data = decrypted_bytes.decode()
            
            # Extract privacy level and actual data
            parts = decrypted_data.split(":", 1)
            if len(parts) == 2:
                return parts[1]
            return decrypted_data
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            raise
    
    async def store_encrypted_data(self, user_id: str, category: DataCategory, 
                                 data: Dict[str, Any], privacy_level: PrivacyLevel = PrivacyLevel.CONFIDENTIAL) -> str:
        """Store encrypted data with retention policy"""
        try:
            data_id = f"{category.value}_{user_id}_{int(datetime.now().timestamp())}"
            
            # Get retention policy
            policy = self.retention_policies.get(category)
            if not policy:
                raise ValueError(f"No retention policy for category: {category}")
            
            # Encrypt data
            data_json = json.dumps(data)
            encrypted_data = self.encrypt_data(data_json, privacy_level)
            
            # Calculate expiration
            expires_at = None
            if policy.retention_days > 0:
                expires_at = (datetime.now() + timedelta(days=policy.retention_days)).isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO encrypted_data 
                    (data_id, user_id, category, encrypted_data, encryption_level, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    data_id,
                    user_id,
                    category.value,
                    encrypted_data,
                    privacy_level.value,
                    datetime.now().isoformat(),
                    expires_at
                ))
                
                await db.commit()
                
                # Log access
                if policy.access_logging:
                    await self.log_data_access(user_id, data_id, "store", True)
                
                self.logger.info(f"Encrypted data stored: {data_id}")
                return data_id
                
        except Exception as e:
            self.logger.error(f"Failed to store encrypted data: {str(e)}")
            raise
    
    async def retrieve_encrypted_data(self, user_id: str, data_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve and decrypt data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT encrypted_data, encryption_level, category, access_count, last_accessed
                    FROM encrypted_data WHERE data_id = ? AND user_id = ?
                """, (data_id, user_id)) as cursor:
                    row = await cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    encrypted_data, encryption_level, category, access_count, last_accessed = row
                    
                    # Check if data is expired
                    async with db.execute("""
                        SELECT expires_at FROM encrypted_data WHERE data_id = ?
                    """, (data_id,)) as cursor:
                        expires_row = await cursor.fetchone()
                        if expires_row and expires_row[0]:
                            expires_at = datetime.fromisoformat(expires_row[0])
                            if datetime.now() > expires_at:
                                self.logger.warning(f"Attempted to access expired data: {data_id}")
                                return None
                    
                    # Decrypt data
                    decrypted_json = self.decrypt_data(encrypted_data)
                    data = json.loads(decrypted_json)
                    
                    # Update access count and timestamp
                    await db.execute("""
                        UPDATE encrypted_data 
                        SET access_count = ?, last_accessed = ?
                        WHERE data_id = ?
                    """, (access_count + 1, datetime.now().isoformat(), data_id))
                    
                    await db.commit()
                    
                    # Log access
                    policy = self.retention_policies.get(DataCategory(category))
                    if policy and policy.access_logging:
                        await self.log_data_access(user_id, data_id, "retrieve", True)
                    
                    return data
                    
        except Exception as e:
            self.logger.error(f"Failed to retrieve encrypted data: {str(e)}")
            await self.log_data_access(user_id, data_id, "retrieve", False)
            return None
    
    async def log_audit_event(self, user_id: str, action: str, resource_type: str, 
                            resource_id: str, ip_address: str = None, user_agent: str = None,
                            success: bool = True, details: Dict[str, Any] = None):
        """Log an audit event"""
        audit_log = AuditLog(
            log_id=f"audit_{int(datetime.now().timestamp())}_{secrets.token_hex(4)}",
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details or {}
        )
        
        self.audit_buffer.append(audit_log)
        
        # Flush if buffer is full
        if len(self.audit_buffer) >= 100:
            await self._flush_audit_logs()
    
    async def log_data_access(self, user_id: str, data_id: str, access_type: str, 
                            success: bool, ip_address: str = None, user_agent: str = None):
        """Log data access event"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                access_id = f"access_{int(datetime.now().timestamp())}_{secrets.token_hex(4)}"
                await db.execute("""
                    INSERT INTO data_access_logs 
                    (access_id, user_id, data_id, access_type, timestamp, ip_address, user_agent, success)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    access_id,
                    user_id,
                    data_id,
                    access_type,
                    datetime.now().isoformat(),
                    ip_address,
                    user_agent,
                    success
                ))
                
                await db.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to log data access: {str(e)}")
    
    async def _flush_audit_logs(self):
        """Flush audit logs buffer to database"""
        if not self.audit_buffer:
            return
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for audit_log in self.audit_buffer:
                    await db.execute("""
                        INSERT INTO audit_logs 
                        (log_id, user_id, action, resource_type, resource_id, timestamp, 
                         ip_address, user_agent, success, details)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        audit_log.log_id,
                        audit_log.user_id,
                        audit_log.action,
                        audit_log.resource_type,
                        audit_log.resource_id,
                        audit_log.timestamp.isoformat(),
                        audit_log.ip_address,
                        audit_log.user_agent,
                        audit_log.success,
                        json.dumps(audit_log.details)
                    ))
                
                await db.commit()
                self.logger.info(f"Flushed {len(self.audit_buffer)} audit logs")
                self.audit_buffer.clear()
                
        except Exception as e:
            self.logger.error(f"Failed to flush audit logs: {str(e)}")
    
    async def get_user_privacy_settings(self, user_id: str) -> Optional[PrivacySettings]:
        """Get user privacy settings"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT * FROM privacy_settings WHERE user_id = ?
                """, (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    if row:
                        return PrivacySettings(
                            user_id=row[0],
                            data_retention_days=row[1],
                            allow_analytics=bool(row[2]),
                            allow_research=bool(row[3]),
                            allow_marketing=bool(row[4]),
                            data_export_enabled=bool(row[5]),
                            auto_delete_enabled=bool(row[6]),
                            encryption_level=PrivacyLevel(row[7]),
                            last_updated=datetime.fromisoformat(row[8])
                        )
                    
                    return None
                    
        except Exception as e:
            self.logger.error(f"Failed to get privacy settings: {str(e)}")
            return None
    
    async def update_user_privacy_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """Update user privacy settings"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO privacy_settings 
                    (user_id, data_retention_days, allow_analytics, allow_research, allow_marketing,
                     data_export_enabled, auto_delete_enabled, encryption_level, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    settings.get('data_retention_days', 365),
                    settings.get('allow_analytics', True),
                    settings.get('allow_research', True),
                    settings.get('allow_marketing', False),
                    settings.get('data_export_enabled', True),
                    settings.get('auto_delete_enabled', True),
                    settings.get('encryption_level', PrivacyLevel.CONFIDENTIAL.value),
                    datetime.now().isoformat()
                ))
                
                await db.commit()
                
                # Log the privacy settings update
                await self.log_audit_event(
                    user_id, "update_privacy_settings", "privacy_settings", user_id,
                    success=True, details=settings
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update privacy settings: {str(e)}")
            return False
    
    async def create_gdpr_request(self, user_id: str, request_type: str, details: Dict[str, Any] = None) -> str:
        """Create a GDPR request (data export, deletion, etc.)"""
        try:
            request_id = f"gdpr_{request_type}_{int(datetime.now().timestamp())}"
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO gdpr_requests 
                    (request_id, user_id, request_type, status, created_at, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    request_id,
                    user_id,
                    request_type,
                    'pending',
                    datetime.now().isoformat(),
                    json.dumps(details or {})
                ))
                
                await db.commit()
                
                # Log the GDPR request
                await self.log_audit_event(
                    user_id, f"gdpr_{request_type}", "gdpr_request", request_id,
                    success=True, details=details
                )
                
                self.logger.info(f"GDPR request created: {request_id}")
                return request_id
                
        except Exception as e:
            self.logger.error(f"Failed to create GDPR request: {str(e)}")
            raise
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR compliance"""
        try:
            export_data = {
                'user_id': user_id,
                'export_timestamp': datetime.now().isoformat(),
                'privacy_settings': None,
                'encrypted_data': [],
                'audit_logs': [],
                'data_access_logs': []
            }
            
            async with aiosqlite.connect(self.db_path) as db:
                # Get privacy settings
                settings = await self.get_user_privacy_settings(user_id)
                if settings:
                    export_data['privacy_settings'] = asdict(settings)
                
                # Get encrypted data (decrypted)
                async with db.execute("""
                    SELECT data_id, category, encrypted_data, encryption_level, created_at
                    FROM encrypted_data WHERE user_id = ?
                """, (user_id,)) as cursor:
                    encrypted_rows = await cursor.fetchall()
                    
                    for row in encrypted_rows:
                        data_id, category, encrypted_data, encryption_level, created_at = row
                        try:
                            decrypted_data = self.decrypt_data(encrypted_data)
                            export_data['encrypted_data'].append({
                                'data_id': data_id,
                                'category': category,
                                'data': json.loads(decrypted_data),
                                'encryption_level': encryption_level,
                                'created_at': created_at
                            })
                        except Exception as e:
                            self.logger.warning(f"Failed to decrypt data for export: {data_id}")
                
                # Get audit logs
                async with db.execute("""
                    SELECT * FROM audit_logs WHERE user_id = ? ORDER BY timestamp DESC
                """, (user_id,)) as cursor:
                    audit_rows = await cursor.fetchall()
                    
                    for row in audit_rows:
                        export_data['audit_logs'].append({
                            'log_id': row[0],
                            'action': row[2],
                            'resource_type': row[3],
                            'resource_id': row[4],
                            'timestamp': row[5],
                            'ip_address': row[6],
                            'user_agent': row[7],
                            'success': bool(row[8]),
                            'details': json.loads(row[9]) if row[9] else {}
                        })
                
                # Get data access logs
                async with db.execute("""
                    SELECT * FROM data_access_logs WHERE user_id = ? ORDER BY timestamp DESC
                """, (user_id,)) as cursor:
                    access_rows = await cursor.fetchall()
                    
                    for row in access_rows:
                        export_data['data_access_logs'].append({
                            'access_id': row[0],
                            'data_id': row[2],
                            'access_type': row[3],
                            'timestamp': row[4],
                            'ip_address': row[5],
                            'user_agent': row[6],
                            'success': bool(row[7])
                        })
            
            # Log the data export
            await self.log_audit_event(
                user_id, "data_export", "user_data", user_id,
                success=True, details={'export_size': len(str(export_data))}
            )
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Failed to export user data: {str(e)}")
            raise
    
    async def delete_user_data(self, user_id: str) -> bool:
        """Delete all user data for GDPR compliance"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Delete encrypted data
                await db.execute("DELETE FROM encrypted_data WHERE user_id = ?", (user_id,))
                
                # Delete privacy settings
                await db.execute("DELETE FROM privacy_settings WHERE user_id = ?", (user_id,))
                
                # Delete data access logs
                await db.execute("DELETE FROM data_access_logs WHERE user_id = ?", (user_id,))
                
                # Mark audit logs as deleted (don't actually delete for compliance)
                await db.execute("""
                    UPDATE audit_logs SET details = json_set(details, '$.deleted', true)
                    WHERE user_id = ?
                """, (user_id,))
                
                await db.commit()
                
                # Log the data deletion
                await self.log_audit_event(
                    user_id, "data_deletion", "user_data", user_id,
                    success=True, details={'deletion_timestamp': datetime.now().isoformat()}
                )
                
                self.logger.info(f"All data deleted for user: {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to delete user data: {str(e)}")
            return False
    
    async def _cleanup_expired_data(self):
        """Clean up expired data based on retention policies"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get expired encrypted data
                async with db.execute("""
                    SELECT data_id, user_id, category FROM encrypted_data 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (datetime.now().isoformat(),)) as cursor:
                    expired_data = await cursor.fetchall()
                
                deleted_count = 0
                for data_id, user_id, category in expired_data:
                    await db.execute("DELETE FROM encrypted_data WHERE data_id = ?", (data_id,))
                    deleted_count += 1
                    
                    # Log the automatic deletion
                    await self.log_audit_event(
                        user_id, "auto_delete_expired", "encrypted_data", data_id,
                        success=True, details={'category': category, 'reason': 'retention_policy'}
                    )
                
                await db.commit()
                
                if deleted_count > 0:
                    self.logger.info(f"Cleaned up {deleted_count} expired data records")
                    
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired data: {str(e)}")
    
    async def get_privacy_compliance_report(self) -> Dict[str, Any]:
        """Generate privacy compliance report"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                report = {
                    'generated_at': datetime.now().isoformat(),
                    'data_retention': {},
                    'encryption_status': {},
                    'audit_coverage': {},
                    'gdpr_requests': {}
                }
                
                # Data retention compliance
                for category in DataCategory:
                    policy = self.retention_policies.get(category)
                    if policy:
                        async with db.execute("""
                            SELECT COUNT(*) FROM encrypted_data WHERE category = ?
                        """, (category.value,)) as cursor:
                            count = (await cursor.fetchone())[0]
                        
                        report['data_retention'][category.value] = {
                            'retention_days': policy.retention_days,
                            'auto_delete': policy.auto_delete,
                            'current_records': count
                        }
                
                # Encryption status
                async with db.execute("""
                    SELECT encryption_level, COUNT(*) FROM encrypted_data 
                    GROUP BY encryption_level
                """) as cursor:
                    encryption_stats = await cursor.fetchall()
                    report['encryption_status'] = {level: count for level, count in encryption_stats}
                
                # Audit coverage
                async with db.execute("SELECT COUNT(*) FROM audit_logs") as cursor:
                    total_audits = (await cursor.fetchone())[0]
                
                async with db.execute("""
                    SELECT COUNT(*) FROM audit_logs 
                    WHERE timestamp > ?
                """, ((datetime.now() - timedelta(days=30)).isoformat(),)) as cursor:
                    recent_audits = (await cursor.fetchone())[0]
                
                report['audit_coverage'] = {
                    'total_audits': total_audits,
                    'recent_audits_30d': recent_audits
                }
                
                # GDPR requests
                async with db.execute("""
                    SELECT request_type, status, COUNT(*) FROM gdpr_requests 
                    GROUP BY request_type, status
                """) as cursor:
                    gdpr_stats = await cursor.fetchall()
                    report['gdpr_requests'] = {
                        f"{req_type}_{status}": count for req_type, status, count in gdpr_stats
                    }
                
                return report
                
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {str(e)}")
            return {}