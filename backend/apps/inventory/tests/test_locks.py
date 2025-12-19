"""
Tests for Redis distributed locking.
"""
import pytest
from unittest.mock import patch, MagicMock
import uuid

from apps.inventory.locks import (
    InventoryLock, MultiItemLock,
    LockAcquisitionError, LockTimeoutError,
)


class TestInventoryLock:
    """Tests for InventoryLock."""
    
    @patch('apps.inventory.locks.cache')
    def test_acquire_lock_success(self, mock_cache):
        """Test successful lock acquisition."""
        mock_cache.add.return_value = True
        
        lock = InventoryLock(item_id=uuid.uuid4())
        result = lock.acquire()
        
        assert result is True
        assert lock._acquired is True
        mock_cache.add.assert_called_once()
    
    @patch('apps.inventory.locks.cache')
    def test_acquire_lock_retry(self, mock_cache):
        """Test lock acquisition with retry."""
        # Fail twice, succeed on third attempt
        mock_cache.add.side_effect = [False, False, True]
        
        lock = InventoryLock(
            item_id=uuid.uuid4(),
            max_retries=3,
            retry_delay_ms=10,  # Small delay for test
        )
        result = lock.acquire()
        
        assert result is True
        assert mock_cache.add.call_count == 3
    
    @patch('apps.inventory.locks.cache')
    def test_acquire_lock_failure(self, mock_cache):
        """Test lock acquisition failure after retries."""
        mock_cache.add.return_value = False
        
        lock = InventoryLock(
            item_id=uuid.uuid4(),
            max_retries=2,
            retry_delay_ms=10,
        )
        
        with pytest.raises(LockAcquisitionError):
            lock.acquire()
    
    @patch('apps.inventory.locks.cache')
    def test_release_lock_success(self, mock_cache):
        """Test successful lock release."""
        item_id = uuid.uuid4()
        lock = InventoryLock(item_id=item_id)
        lock._acquired = True
        
        # Mock cache to return our owner as current owner
        mock_cache.get.return_value = lock.owner
        mock_cache.delete.return_value = True
        
        result = lock.release()
        
        assert result is True
        assert lock._acquired is False
        mock_cache.delete.assert_called_once()
    
    @patch('apps.inventory.locks.cache')
    def test_release_lock_wrong_owner(self, mock_cache):
        """Test release fails if someone else owns the lock."""
        lock = InventoryLock(item_id=uuid.uuid4())
        lock._acquired = True
        
        # Mock cache to return a different owner
        mock_cache.get.return_value = 'different-owner'
        
        result = lock.release()
        
        assert result is False
        mock_cache.delete.assert_not_called()
    
    @patch('apps.inventory.locks.cache')
    def test_context_manager(self, mock_cache):
        """Test lock as context manager."""
        mock_cache.add.return_value = True
        mock_cache.get.return_value = None  # Will be set by the lock
        
        item_id = uuid.uuid4()
        
        with patch.object(InventoryLock, 'release') as mock_release:
            mock_release.return_value = True
            
            with InventoryLock(item_id) as lock:
                assert lock._acquired is True
            
            mock_release.assert_called_once()
    
    @patch('apps.inventory.locks.cache')
    def test_extend_lock(self, mock_cache):
        """Test lock extension."""
        lock = InventoryLock(item_id=uuid.uuid4(), timeout=15)
        lock._acquired = True
        
        mock_cache.get.return_value = lock.owner
        mock_cache.set.return_value = True
        
        result = lock.extend(additional_time=30)
        
        assert result is True
        mock_cache.set.assert_called_once()


class TestMultiItemLock:
    """Tests for MultiItemLock."""
    
    @patch('apps.inventory.locks.InventoryLock')
    def test_multi_lock_acquire(self, MockLock):
        """Test acquiring multiple locks."""
        mock_lock_instance = MagicMock()
        mock_lock_instance.acquire.return_value = True
        MockLock.return_value = mock_lock_instance
        
        item_ids = [uuid.uuid4(), uuid.uuid4()]
        multi_lock = MultiItemLock(item_ids)
        
        result = multi_lock.acquire()
        
        assert result is True
        assert len(multi_lock.locks) == 2
    
    @patch('apps.inventory.locks.InventoryLock')
    def test_multi_lock_consistent_order(self, MockLock):
        """Test locks are acquired in consistent order to prevent deadlocks."""
        captured_ids = []
        
        def track_lock_creation(item_id, timeout):
            captured_ids.append(str(item_id))
            mock = MagicMock()
            mock.acquire.return_value = True
            return mock
        
        MockLock.side_effect = track_lock_creation
        
        # Create locks in any order
        id1 = uuid.UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
        id2 = uuid.UUID('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb')
        
        multi_lock = MultiItemLock([id2, id1])  # Passed in reverse order
        multi_lock.acquire()
        
        # Should be sorted alphabetically
        assert captured_ids[0] < captured_ids[1]
    
    @patch('apps.inventory.locks.InventoryLock')
    def test_multi_lock_release_on_failure(self, MockLock):
        """Test all locks are released if one acquisition fails."""
        first_lock = MagicMock()
        first_lock.acquire.return_value = True
        first_lock.release.return_value = True
        
        second_lock = MagicMock()
        second_lock.acquire.side_effect = LockAcquisitionError("Failed")
        
        MockLock.side_effect = [first_lock, second_lock]
        
        item_ids = [uuid.uuid4(), uuid.uuid4()]
        multi_lock = MultiItemLock(item_ids)
        
        with pytest.raises(LockAcquisitionError):
            multi_lock.acquire()
        
        # First lock should have been released
        first_lock.release.assert_called_once()
