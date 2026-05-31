"""
OdooClient — Gold Tier implementation for accounting system integration.
Uses Odoo JSON-RPC API for external communication.
"""
import logging
import xmlrpc.client
from typing import Any, Dict, List, Optional
from src.actions.base_action import BaseAction

logger = logging.getLogger(__name__)


class OdooClient(BaseAction):
    """
    Client for interacting with Odoo Community edition.
    Supports invoice creation and general accounting tasks.
    """

    def __init__(self, config_instance=None):
        super().__init__(name="OdooClient", config_instance=config_instance)
        
        # Odoo settings from config (should be in .env)
        self.url = getattr(self.config, 'odoo_url', 'http://localhost:8069')
        self.db = getattr(self.config, 'odoo_db', 'odoo')
        self.username = getattr(self.config, 'odoo_username', 'admin')
        self.password = getattr(self.config, 'odoo_password', 'admin')
        
        self.uid = None
        self.common = None
        self.models = None

    def _connect(self):
        """Internal method to authenticate and connect to Odoo."""
        if self.uid:
            return

        try:
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            logger.info(f"[OdooClient] Connected successfully to {self.url} (UID: {self.uid})")
        except Exception as e:
            logger.error(f"[OdooClient] Connection failed: {e}")
            raise ConnectionError(f"Odoo connection failed: {e}")

    def execute(self, model: str, method: str, args: List = None, kwargs: Dict = None) -> Any:
        """
        Generic execute method for Odoo RPC calls.
        
        Args:
            model: Odoo model name (e.g., 'account.move')
            method: Odoo method (e.g., 'create', 'search_read')
            args: Positional arguments for the RPC call
            kwargs: Keyword arguments for the RPC call
            
        Returns:
            Result of the RPC call
        """
        action_desc = f"Odoo {method} on {model}"
        
        # 1. Dry run check
        if not self.dry_run_check(action_desc):
            return {"status": "dry_run", "message": "Dry run enabled. Action not performed."}

        self.log_action_start("odoo_rpc", action_desc, {"model": model, "method": method})

        try:
            self._connect()
            
            # Use models proxy to execute the call
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args or [], kwargs or {}
            )
            
            self.log_action_success("odoo_rpc", action_desc, {"status": "success"})
            return result

        except Exception as e:
            self.log_action_failure("odoo_rpc", action_desc, str(e))
            raise

    def create_invoice(self, partner_id: int, lines: List[Dict], invoice_date: str = None) -> int:
        """
        Convenience method to create an invoice in Odoo.
        
        Args:
            partner_id: ID of the customer
            lines: List of invoice line items
            invoice_date: Date string (YYYY-MM-DD)
            
        Returns:
            ID of the created invoice
        """
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': partner_id,
            'invoice_date': invoice_date or None,
            'invoice_line_ids': [
                (0, 0, line) for line in lines
            ]
        }
        
        return self.execute('account.move', 'create', [invoice_vals])

    def search_partners(self, domain: List) -> List[Dict]:
        """Search for partners/customers."""
        return self.execute('res.partner', 'search_read', [domain], {'fields': ['id', 'name', 'email']})

def main():
    """Test script for OdooClient."""
    from src.config import Config
    import sys
    
    logging.basicConfig(level=logging.INFO)
    client = OdooClient(Config())
    
    # Example: search for customers
    try:
        # result = client.search_partners([['customer_rank', '>', 0]])
        # print(f"Customers: {result}")
        print("OdooClient testing skipped in dry-run/no-server mode.")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    main()
