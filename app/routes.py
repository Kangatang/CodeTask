from flask import request
from app import app
import json

# Load up the JSON values from a file
with open('data.json', 'r') as lFile:
    gLoadedFile = json.load(lFile)
    # Storing the products and orders as a dictionary makes lookup more efficient
    # than iterating through a list looking for the right product/order id, it adds 
    # more initial setup time but should allow for faster post responses
    gProductDict = { i["productId"] : i for i in gLoadedFile["products"] }
    gOrderDict = { i["orderId"] : i for i in gLoadedFile["orders"] }

@app.route('/api/v1/warehouse/fulfilment', methods=['POST'])
def ProcessOrders():
    content = request.json
    #test output
    print (content)
    ResultDict = {"unfulfillable":[]}
    
    for lCurrentOrderId in content["orderIds"]:
        #Obtain the order info for the requested order
        lTargetOrder = gOrderDict[lCurrentOrderId]
        lOrderPossible = True
        for lCurrentOrderedProduct in lTargetOrder["items"]:
            lTargetProduct = gProductDict[lCurrentOrderedProduct["productId"]]
            if ( lTargetProduct["quantityOnHand"] < lCurrentOrderedProduct["quantity"] ):
                #This is bad, we don't have enough stock on hand
                lOrderPossible = False
        
        if lOrderPossible == False:
            ResultDict["unfulfillable"].append(lCurrentOrderId)
    return str(ResultDict)
    

@app.errorhandler(405)
def WrongMethodError(error):
    return "Use a valid method"
    