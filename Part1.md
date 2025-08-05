# Product API Code Review - Intern Assessment

## Part 1: Issues Identified

### 1. Error Handling
- **Problem**: No validation for missing fields
- **Impact**: Server crashes with KeyError

### 2. Misplaced Entities
- **Problem**: Product has warehouse_id (should be in Inventory only)
- **Impact**: Violates "products in multiple warehouses" requirement

### 3. Rollback
- **Problem**: No exception incase of error or mid-termination.
- **Impact**: Lead to corrupted data.

## Part 2: Improved code!

```python
@app.route('/api/products', methods=['POST']) 
def create_product():
    try:

        # Check if server is connected.
        db.session.execute('SELECT 1')

        data = request.json 
        
        if not data:
            return {"error": "Invalid input"}

        # Check for fields
        fields = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']

        for field in fields:
            if field not in data:
                return {"error": f"Missing field: {field}"}
        
        
        # Unique SKU check
        existing_sku = product.query.filter_by(sku=data['sku']).first()
        if existing_sku:
            return {"error": "SKU already exists"}
        
        
        db.session.begin()


        # Create new product 
        product = Product( 
            name=data['name'], 
            sku=data['sku'], 
            price=data['price']
            # Not need for warhouse_id here.
            # Assuming inventory Entity has warehouse_id key, and it is not present in Product Entity.
        ) 
        
        db.session.add(product) 
        db.session.flush() # not commiting here
        
        
        # Update inventory count 
        inventory = Inventory( 
            product_id=product.id, 
            warehouse_id=data['warehouse_id'], 
            quantity=data['initial_quantity'] 
        ) 
        
        db.session.add(inventory) 
        db.session.commit() 
        
        return {"message": "Product created", "product_id": product.id}
    
    except SQLAlchemyError:
        db.session.rollback()
        return {"error" : "Database not connected!"}
    
    except Exception as e:
        db.session.rollback()
        return {"error": "Internal Error!"}
```

## Part 3: Questions for team
- Need database schema for complete analysis
