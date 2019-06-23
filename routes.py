from flask import request
from app import app
from app.warehousemanager import WarehouseManager

gWarehouse = WarehouseManager('data.json')

@app.route('/api/v1/warehouse/fulfilment', methods=['POST'])
def ProcessOrders():
    content = request.json
    ResultDict = gWarehouse.FillOrders( content )
                
    gWarehouse.ProcessInternalStockThreshold()
    
    return str(ResultDict)
    
    
@app.errorhandler(405)
def BadUrlError(error):
    return "Error: Address was not found, please enter a valid address."

@app.errorhandler(405)
def WrongMethodError(error):
    return "Error: Unsupported method. Only POST is supported."
    