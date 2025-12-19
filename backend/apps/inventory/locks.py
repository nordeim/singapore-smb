"""
Redis distributed locking for inventory operations.

Provides thread-safe, distributed locks for concurrent stock operations.
Prevents race conditions during stock reservations and transfers.

Usage:
    with InventoryLock(item_id) as lock:
        # perform inventory operation
        pass
"""
import time
import uuid
import logging
from typing import Optional

from django.core.cache import cache
from django.conf import settings


logger = logging.getLogger(__name__)

# Default lock timeout in seconds (user configured: 15 seconds)
DEFAULT_LOCK_TIMEOUT = getattr(settings, 'INVENTORY_LOCK_TIMEOUT_SECONDS', 15)

# Retry configuration
MAX_RETRIES = getattr(settings, 'INVENTORY_LOCK_MAX_RETRIES', 3)
RETRY_DELAY_MS = getattr(settings, 'INVENTORY_LOCK_RETRY_DELAY_MS', 100)


class LockAcquisitionError(Exception):
    """Raised when lock cannot be acquired."""
    pass


class LockTimeoutError(Exception):
    """Raised when lock times out during operation."""
    pass


class InventoryLock:
    """
    Distributed lock for inventory operations using Redis.
    
    Uses Django's cache backend (which should be Redis in production).
    Implements lock acquisition with retry and exponential backoff.
    
    Attributes:
        item_id: UUID of the inventory item to lock
        timeout: Lock timeout in seconds
        owner: Unique identifier for this lock holder
    
    Example:
        with InventoryLock(item.id) as lock:
            item.available_qty -= quantity
            item.save()
    """
    
    def __init__(
        self,
        item_id: str,
        timeout: int = DEFAULT_LOCK_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        retry_delay_ms: int = RETRY_DELAY_MS,
    ):
        """
        Initialize inventory lock.
        
        Args:
            item_id: UUID of the inventory item to lock
            timeout: Lock timeout in seconds (default 15)
            max_retries: Maximum retry attempts (default 3)
            retry_delay_ms: Initial retry delay in milliseconds (default 100)
        """
        self.item_id = str(item_id)
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay_ms = retry_delay_ms
        self.owner = str(uuid.uuid4())
        self._acquired = False
    
    @property
    def lock_key(self) -> str:
        """Get the Redis key for this lock."""
        return f"inventory:lock:{self.item_id}"
    
    def acquire(self) -> bool:
        """
        Attempt to acquire the lock with retry logic.
        
        Uses exponential backoff for retries.
        
        Returns:
            True if lock acquired
            
        Raises:
            LockAcquisitionError: If lock cannot be acquired after retries
        """
        for attempt in range(self.max_retries + 1):
            # Try to set the lock (nx=True means only if not exists)
            success = cache.add(self.lock_key, self.owner, self.timeout)
            
            if success:
                self._acquired = True
                logger.debug(f"Lock acquired: {self.lock_key} (owner: {self.owner})")
                return True
            
            if attempt < self.max_retries:
                # Exponential backoff
                delay = (self.retry_delay_ms * (2 ** attempt)) / 1000.0
                logger.debug(
                    f"Lock contention on {self.lock_key}, "
                    f"retry {attempt + 1}/{self.max_retries} after {delay:.2f}s"
                )
                time.sleep(delay)
        
        raise LockAcquisitionError(
            f"Failed to acquire lock for inventory item {self.item_id} "
            f"after {self.max_retries} retries"
        )
    
    def release(self) -> bool:
        """
        Release the lock.
        
        Only releases if we are the owner (prevents releasing someone else's lock).
        
        Returns:
            True if lock was released
        """
        if not self._acquired:
            return False
        
        # Verify we're the owner before releasing
        current_owner = cache.get(self.lock_key)
        
        if current_owner == self.owner:
            cache.delete(self.lock_key)
            self._acquired = False
            logger.debug(f"Lock released: {self.lock_key}")
            return True
        elif current_owner is None:
            # Lock already expired
            logger.warning(f"Lock already expired: {self.lock_key}")
            self._acquired = False
            return False
        else:
            # Someone else owns it now (shouldn't happen)
            logger.error(
                f"Lock owner mismatch on {self.lock_key}: "
                f"expected {self.owner}, got {current_owner}"
            )
            self._acquired = False
            return False
    
    def extend(self, additional_time: int = None) -> bool:
        """
        Extend the lock timeout.
        
        Args:
            additional_time: Additional seconds (default: original timeout)
            
        Returns:
            True if lock was extended
        """
        if not self._acquired:
            return False
        
        current_owner = cache.get(self.lock_key)
        if current_owner != self.owner:
            return False
        
        # Re-set with new timeout
        extend_time = additional_time or self.timeout
        cache.set(self.lock_key, self.owner, extend_time)
        logger.debug(f"Lock extended: {self.lock_key} by {extend_time}s")
        return True
    
    def __enter__(self) -> 'InventoryLock':
        """Context manager entry - acquire lock."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - release lock."""
        self.release()
        return False  # Don't suppress exceptions


class MultiItemLock:
    """
    Lock multiple inventory items atomically.
    
    Used for transfers between locations.
    Acquires locks in consistent order to prevent deadlocks.
    
    Example:
        with MultiItemLock([source_item.id, dest_item.id]) as locks:
            # Transfer operation
            pass
    """
    
    def __init__(
        self,
        item_ids: list,
        timeout: int = DEFAULT_LOCK_TIMEOUT,
    ):
        """
        Initialize multi-item lock.
        
        Args:
            item_ids: List of inventory item UUIDs
            timeout: Lock timeout per item
        """
        # Sort to ensure consistent lock ordering (prevent deadlocks)
        self.item_ids = sorted([str(iid) for iid in item_ids])
        self.timeout = timeout
        self.locks: list[InventoryLock] = []
    
    def acquire(self) -> bool:
        """Acquire all locks in order."""
        try:
            for item_id in self.item_ids:
                lock = InventoryLock(item_id, self.timeout)
                lock.acquire()
                self.locks.append(lock)
            return True
        except LockAcquisitionError:
            # Release any acquired locks
            self.release()
            raise
    
    def release(self):
        """Release all locks in reverse order."""
        for lock in reversed(self.locks):
            try:
                lock.release()
            except Exception as e:
                logger.error(f"Error releasing lock: {e}")
        self.locks = []
    
    def __enter__(self) -> 'MultiItemLock':
        """Context manager entry."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
        return False
