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
    