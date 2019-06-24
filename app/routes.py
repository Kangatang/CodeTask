from flask import request
from app import app
from app.warehousemanager import WarehouseManager

gWarehouse = WarehouseManager('data.json')

# Our main route, used to process all of our currently pending orders
@app.route('/api/v1/warehouse/fulfilment', methods=['POST'])
def ProcessOrders():
    lContent = request.json
    # Tell our warehouse to attempt to fill the orders given
    ResultDict = gWarehouse.FillOrders( lContent )
    
    # Our products may have gone below their refill threshold
    # Ensure that if they have, we send a corresponding internal order
    gWarehouse.ProcessInternalStockThreshold()
    
    return str(ResultDict)

# Test function to reset the quantities of the products to allow for more orders
# to be processed    
@app.route('/api/v1/warehouse/serviceinternalorder', methods=['POST'])
def ProcessInternalOrders():
    lContent = request.json
    
    #Mark our pending internal orders as complete, refilling products quantities
    ResultDict = gWarehouse.FillInternalOrders( lContent )
    
    #Just in case there is ever a situation where refilling a products quantity leaves it
    #still below the products refill threshold
    gWarehouse.ProcessInternalStockThreshold()
    
    return str(ResultDict)
        
 
@app.errorhandler(404)
def BadUrlError(error):
    return "Error: Address was not found, please enter a valid address."

@app.errorhandler(405)
def WrongMethodError(error):
    return "Error: Unsupported method. Only POST is supported."
    
@app.errorhandler(400)
def WrongFormat(error):
    return "Error: Request in incorrect format. Valid JSON is required"
    
# Debugging sanity test route to confirm basic operation is still working
# uses a dummy instance of the server to avoid 'corrupting' the true instance
@app.route('/api/v1/warehouse/RunInternalSanityTest', methods=['POST'])
def RunInternalSanityTest():
    
    TestWarehouse = WarehouseManager('data.json')
    
    # First test - basic order being filled
    lMessage = {"orderIds": [1122]}
    ResultDict = TestWarehouse.FillOrders( lMessage )
    TestSucceeded = True
    if str(ResultDict) != "{'unfulfillable': []}":
        TestSucceeded = False
    if TestWarehouse.GetCurrentOrders()[1122]["status"] != "Fulfilled":
        TestSucceeded = False
    if TestSucceeded == False:
        return "Error: First test has failed"
        
    # Second test - order failing, check for request of more product
    lMessage = {"orderIds": [1125]}
    ResultDict = TestWarehouse.FillOrders( lMessage )
    TestWarehouse.ProcessInternalStockThreshold()
    TestSucceeded = True
    if str(ResultDict) != "{'unfulfillable': [1125]}":
        TestSucceeded = False
    if TestWarehouse.GetCurrentOrders()[1125]["status"] != "Error: Unfulfillable":
        TestSucceeded = False
    # Verify we have checked BOTH internal orders
    if TestWarehouse.GetInternalOrders()[1]["productId"] != 2:
        TestSucceeded = False
    if TestWarehouse.GetInternalOrders()[2]["productId"] != 3:
        TestSucceeded = False
    if TestSucceeded == False:
        return "Error: Second test has failed"
        
    # Third test - Refilling product quantity and having order then be processed successfully
    TestSucceeded = True
    lOrderFill = {"orderIds": [1,2]}
    TestWarehouse.FillInternalOrders( lOrderFill )
    # Verify we have restored the product quantity 
    if TestWarehouse.GetProductQuantities()[2]["quantityOnHand"] == 0:
        TestSucceeded = False
    if TestWarehouse.GetProductQuantities()[3]["quantityOnHand"] == 0:
        TestSucceeded = False
    # Try Resent our message    
    lMessage = {"orderIds": [1125]}
    ResultDict = TestWarehouse.FillOrders( lMessage )
    TestWarehouse.ProcessInternalStockThreshold()
    
    if str(ResultDict) != "{'unfulfillable': []}":
        TestSucceeded = False
    if TestWarehouse.GetCurrentOrders()[1122]["status"] != "Fulfilled":
        TestSucceeded = False
    if 1 in TestWarehouse.GetInternalOrders(): # Verify our pending refill order has been filled
        TestSucceeded = False
    if 2 in TestWarehouse.GetInternalOrders():
        TestSucceeded = False
    if TestSucceeded == False:
        return "Error: Third test has failed"
        
    return "All Tests Successful"