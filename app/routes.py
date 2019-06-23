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
    
#If we run out of a product, we have to send off for some replacements, this is a stub
# for our outgoing product requests
gPendingInternalOrders = {}
gCurrentInternalOrderId = 0

@app.route('/api/v1/warehouse/fulfilment', methods=['POST'])
def ProcessOrders():
    content = request.json
    #test output
    print (content)
    ResultDict = {"unfulfillable":[]}
    
    for lCurrentOrderId in content["orderIds"]:
        #Obtain the order info for the requested order
        lTargetOrder = gOrderDict[lCurrentOrderId]
        
        # We need to check if the order is possible first, because we don't
        # partially fill orders, we don't want to start subtracting quantities before
        # we know we have to, otherwise we'd have to deal with some ugly quantity rollbacks
        lOrderPossible = True
        for lCurrentOrderedProduct in lTargetOrder["items"]:
            lTargetProduct = gProductDict[lCurrentOrderedProduct["productId"]]
            if ( lTargetProduct["quantityOnHand"] < lCurrentOrderedProduct["quantity"] ):
                #This is bad, we don't have enough stock on hand
                lOrderPossible = False
        
        if lOrderPossible == False:
            ResultDict["unfulfillable"].append(lCurrentOrderId)
            lTargetOrder["status"] = "Error: Unfulfillable"
        else:
            #if the order is valid, iterate through again removing the necessary quantities
            #we will investigatge later to see if it is necessary to submit a refill order for the products
            for lCurrentOrderedProduct in lTargetOrder["items"]:
                lTargetProduct = gProductDict[lCurrentOrderedProduct["productId"]]
                lTargetProduct["quantityOnHand"] -= lCurrentOrderedProduct["quantity"]
            lTargetOrder["status"] = "Fulfilled"
                
        
        
        
    #Process any new orders for products below the threshold
    #Check if order has already been sent to refill that product
    for lCurrentProduct in gProductDict.values():
        if lCurrentProduct["quantityOnHand"] < lCurrentProduct["reorderThreshold"]:
            #We need more of this item, check if we have already asked before
            #If we don't have one, make one
            if lCurrentProduct["productId"] in gPendingInternalOrders:
                gCurrentInternalOrderId += 1
                gPendingInternalOrders[lCurrentProduct["productId"]] = { "orderId" : gCurrentInternalOrderId, "orderQuantity" : lCurrentProduct["reorderAmount"] }
    
    return str(ResultDict)
    

@app.errorhandler(405)
def WrongMethodError(error):
    return "Use a valid method"
    