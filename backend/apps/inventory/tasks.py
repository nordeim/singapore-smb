"""
Celery tasks for inventory domain.

Handles:
- Expired reservation cleanup (periodic)
- Low stock alerts (periodic)
- Marketplace inventory sync (future)
"""
from celery import shared_task
from django.utils import timezone
import logging


logger = logging.getLogger(__name__)


@shared_task(name='inventory.cleanup_expired_reservations')
def cleanup_expired_reservations() -> dict:
    """
    Clean up expired inventory reservations (periodic task).
    
    Should be scheduled to run every 5-10 minutes via Celery Beat.
    
    Returns:
        Dict with count of expired reservations per company
    """
    from apps.inventory.services import InventoryService
    from apps.accounts.models import Company
    
    results = {}
    total = 0
    
    for company in Company.objects.filter(is_active=True):
        try:
            count = InventoryService.cleanup_expired_reservations(company=company)
            if count > 0:
                results[str(company.id)] = count
                total += count
        except Exception as e:
            logger.error(f"Error cleaning up reservations for {company.id}: {e}")
    
    return {
        'total_expired': total,
        'by_company': results,
        'timestamp': timezone.now().isoformat(),
    }


@shared_task(name='inventory.send_low_stock_alerts')
def send_low_stock_alerts() -> dict:
    """
    Send notifications for low stock items (periodic task).
    
    Should be scheduled to run daily via Celery Beat.
    
    Returns:
        Dict with count of low stock items per company
    """
    from apps.inventory.services import InventoryService
    from apps.accounts.models import Company
    
    results = {}
    
    for company in Company.objects.filter(is_active=True):
        try:
            low_stock_items = InventoryService.check_low_stock(company=company)
            
            if low_stock_items:
                # TODO: Implement actual notification via email or webhook
                # For now, just log the alert
                for item in low_stock_items:
                    logger.warning(
                        f"Low stock alert: {item.sku} at {item.location.code} "
                        f"has {item.net_qty} units (threshold: {item.reorder_point})"
                    )
                
                results[str(company.id)] = {
                    'count': len(low_stock_items),
                    'items': [
                        {
                            'sku': item.sku,
                            'location': item.location.code,
                            'net_qty': item.net_qty,
                            'reorder_point': item.reorder_point,
                        }
                        for item in low_stock_items[:10]  # Limit to 10 per company
                    ]
                }
        except Exception as e:
            logger.error(f"Error checking low stock for {company.id}: {e}")
    
    return {
        'total_companies_with_low_stock': len(results),
        'by_company': results,
        'timestamp': timezone.now().isoformat(),
    }


@shared_task(name='inventory.sync_marketplace_inventory')
def sync_marketplace_inventory(company_id: str, marketplace: str) -> dict:
    """
    Sync inventory levels with external marketplace (future integration).
    
    Args:
        company_id: UUID of the company
        marketplace: Marketplace name (shopee, lazada, qoo10)
        
    Returns:
        Dict with sync results
    """
    # TODO: Implement marketplace inventory sync in Phase 5
    logger.info(
        f"Marketplace inventory sync requested for company {company_id}, "
        f"marketplace: {marketplace}. Integration not yet implemented."
    )
    
    return {
        'status': 'not_implemented',
        'company_id': company_id,
        'marketplace': marketplace,
        'message': 'Marketplace integration will be implemented in Phase 5',
    }


@shared_task(name='inventory.record_stock_count')
def record_stock_count(
    inventory_item_id: str,
    counted_qty: int,
    user_id: str = None,
    notes: str = ''
) -> dict:
    """
    Record a physical stock count and create adjustment if needed.
    
    Args:
        inventory_item_id: UUID of the inventory item
        counted_qty: Physical count result
        user_id: UUID of user performing count
        notes: Count notes
        
    Returns:
        Dict with count result and any adjustment made
    """
    from apps.inventory.models import InventoryItem
    from apps.inventory.services import InventoryService
    from apps.accounts.models import User
    
    try:
        item = InventoryItem.objects.get(id=inventory_item_id)
        user = User.objects.get(id=user_id) if user_id else None
        
        variance = counted_qty - item.available_qty
        
        result = {
            'item_id': str(item.id),
            'sku': item.sku,
            'expected_qty': item.available_qty,
            'counted_qty': counted_qty,
            'variance': variance,
        }
        
        if variance != 0:
            # Create adjustment movement
            InventoryService.adjust_stock(
                inventory_item=item,
                quantity_delta=variance,
                notes=f"Stock count: {notes}" if notes else "Stock count adjustment",
                user=user,
            )
            result['adjustment_created'] = True
        else:
            result['adjustment_created'] = False
        
        # Update last counted timestamp
        item.last_counted_at = timezone.now()
        item.save(update_fields=['last_counted_at', 'updated_at'])
        
        logger.info(f"Stock count recorded for {item.sku}: variance {variance:+d}")
        
        return result
        
    except InventoryItem.DoesNotExist:
        return {
            'error': f"Inventory item {inventory_item_id} not found",
            'status': 'failed',
        }
