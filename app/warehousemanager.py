import json

class WarehouseManager:
    def __init__(self, aFilename ):
        with open( aFilename, 'r' ) as lFile:
            lLoadedFile = json.load( lFile )
            # Storing the products and orders as a dictionary makes lookup more efficient
            # than iterating through a list looking for the right product/order id, it adds 
            # more initial setup time but should allow for faster post responses
            self.mProductDict = { i["productId"] : i for i in lLoadedFile["products"] }
            self.mOrderDict = { i["orderId"] : i for i in lLoadedFile["orders"] }
        
        #If we run out of a product, we have to send off for some replacements, this is a stub
        # for our outgoing product requests
        self.mPendingInternalOrders = {}
        self.mCurrentInternalOrderId = 0
        
    def FillOrders( self, aRequestedOrders ):
        lResultDict = {"unfulfillable":[]}
    
        for lCurrentOrderId in aRequestedOrders["orderIds"]:
            #Obtain the order info for the requested order
            lTargetOrder = self.mOrderDict[lCurrentOrderId]
            
            # We need to check if the order is possible first, because we don't
            # partially fill orders, we don't want to start subtracting quantities before
            # we know we have to, otherwise we'd have to deal with some ugly quantity rollbacks
            lOrderPossible = True
            for lCurrentOrderedProduct in lTargetOrder["items"]:
                lTargetProduct = self.mProductDict[lCurrentOrderedProduct["productId"]]
                if ( lTargetProduct["quantityOnHand"] < lCurrentOrderedProduct["quantity"] ):
                    #This is bad, we don't have enough stock on hand
                    lOrderPossible = False
            
            if lOrderPossible == False:
                lResultDict["unfulfillable"].append(lCurrentOrderId)
                lTargetOrder["status"] = "Error: Unfulfillable"
            else:
                #if the order is valid, iterate through again removing the necessary quantities
                #we will investigatge later to see if it is necessary to submit a refill order for the products
                for lCurrentOrderedProduct in lTargetOrder["items"]:
                    lTargetProduct = self.mProductDict[lCurrentOrderedProduct["productId"]]
                    lTargetProduct["quantityOnHand"] -= lCurrentOrderedProduct["quantity"]
                lTargetOrder["status"] = "Fulfilled"
                
        return lResultDict
        
        
    def ProcessInternalStockThreshold( self ):
        #Process any new orders for products below the threshold
        #Check if order has already been sent to refill that product
        for lCurrentProduct in self.mProductDict.values():
            if lCurrentProduct["quantityOnHand"] < lCurrentProduct["reorderThreshold"]:
                #We need more of this item, check if we have already asked before
                #If we don't have one, make one
                if lCurrentProduct["productId"] not in self.mPendingInternalOrders:
                    self.mCurrentInternalOrderId += 1
                    self.mPendingInternalOrders[lCurrentProduct["productId"]] = { "orderId" : self.mCurrentInternalOrderId, "orderQuantity" : lCurrentProduct["reorderAmount"] }
        print( self.mPendingInternalOrders )            
                    
                    