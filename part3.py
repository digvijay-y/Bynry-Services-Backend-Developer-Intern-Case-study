@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):
    try:
        # check for company
        company = Company.query.get(company_id)
        if not company:
            return {"error": "Company not found"}
        
        # Fetch from DB
        alert_query = db.session.query(Product.ProductID.label("ProductID"),
                                       Product.ProductName.label("ProductName"),
                                       Product.SKU_ID.label("SKU_ID"),
                                       Inventory.InventoryID.label("InventoryID"),
                                       Inventory.Quantity.label("Quantity"),
                                       Categories.min_Quantity.label("min_Quantity"),
                                       Inventory.days_until_restock.label("days_until_restock"),
                                       Inventory.is_active.label("is_active"),
                                       Warehouse.WarehouseName.label("WarehouseName"),
                                       Warehouse.WarehouseID.label("WarehouseID"),
                                       Supplier.SupplierID.label("SupplierID"),
                                       Supplier.SupplierName.label("SupplierName"),
                                       Supplier.Contact_email.label("Contact_email")

        ).join(
            Inventory, Product.ProductID == Inventory.ProductID # Join invertory with reference to productID's
        ).join(
            Warehouse, Inventory.WarehouseID == Warehouse.WarehouseID # Join warehouse with reference to WarehouseID's
        ).join(
            Supplier, Product.SupplierID == Supplier.SupplierID # Join supplier with reference to SupplierID's
        ).join(
            Categories, Product.CategoryID == Categories.CategoryID # Join categories with reference to CategoryID's
        ).filter( 
            # Check for quantity
            Warehouse.CompanyID == company_id,
            Inventory.is_active == True,  # Only active inventory
            Inventory.Quantity <= Categories.min_Quantity
        ).all()

        alerts = [] # Notifications

        """Expected Response Format: 
{ 
  "alerts": [ 
    { 
      "product_id": 123, 
      "product_name": "Widget A", 
      "sku": "WID-001", 
      "warehouse_id": 456, 
      "warehouse_name": "Main Warehouse", 
      "current_stock": 5, 
      "threshold": 20, 
      "days_until_stockout": 12, 
      "supplier": { 
        "id": 789, 
        "name": "Supplier Corp", 
        "contact_email": "orders@supplier.com" 
      } 
    } 
  ], 
  "total_alerts": 1 
} 
"""

        for alert in alert_query:
            notification = {
                "product_id": alert.ProductID,
                "product_name": alert.ProductName,
                "sku": alert.SKU_ID,
                "warehouse_id": alert.WarehouseID,
                "warehouse_name": alert.WarehouseName,
                "current_stock": alert.Quantity,
                "threshold": alert.min_Quantity,
                "days_until_restock": alert.days_until_restock,
                "supplier":{
                    "id": alert.SupplierID,
                    "name": alert.SupplierName,
                    "contact_email": alert.Contact_email
                }
            }
            alerts.append(notification)
        return {
            "alerts": alerts,
            "total_alerts": len(alerts)
        }
    except Exception as e:
        return {"error": "Internal Error"}
