import json

class WarehouseManager:
    #--------------------------------------------------------------------------
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
        self.mPendingProducts = []
        self.mPendingInternalOrders = {}
        self.mCurrentInternalOrderId = 0
    #init    
        
        
    #--------------------------------------------------------------------------    
    def FillOrders( self, aRequestedOrders ):
        if "orderIds" not in aRequestedOrders:
            return "Error: orderIds not present"
        lResultDict = {"unfulfillable":[]}
    
        for lCurrentOrderId in aRequestedOrders["orderIds"]:
        
            if lCurrentOrderId not in self.mOrderDict:
                # We don't have this order, add it to error output and continue
                # we don't want to silently fail because that might be implied as
                # succeeding
                lResultDict["unfulfillable"].append(lCurrentOrderId)
                continue
            
            #Obtain the order info for the requested order
            lTargetOrder = self.mOrderDict[lCurrentOrderId]
            
            #If the order has previosly been filled, ignore
            if lTargetOrder["status"] == "Fulfilled":
                continue
            
            # We need to check if the order is possible first, because we don't
            # partially fill orders, we don't want to start subtracting quantities before
            # we know we have to, otherwise we'd have to deal with some ugly quantity rollbacks
            lOrderPossible = True
            for lCurrentOrderedProduct in lTargetOrder["items"]:
                
                if lCurrentOrderedProduct["productId"] not in self.mProductDict:
                    lOrderPossible = False
                    
                lTargetProduct = self.mProductDict[lCurrentOrderedProduct["productId"]]
                if ( lTargetProduct["quantityOnHand"] < lCurrentOrderedProduct["quantity"] ):
                    #This is bad, we don't have enough stock on hand
                    lOrderPossible = False
                    
                # If this order is no longer valid, there's no reason to check
                # ALL the products requested
                if lOrderPossible == False:
                    break
            
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
    #FillOrders    
        
    
    #--------------------------------------------------------------------------    
    def ProcessInternalStockThreshold( self ):
        #Process any new orders for products below the threshold
        #Check if order has already been sent to refill that product
        for lCurrentProduct in self.mProductDict.values():
            if lCurrentProduct["quantityOnHand"] < lCurrentProduct["reorderThreshold"]:
                #We need more of this item, check if we have already asked before
                #If we don't have one, make one
                if lCurrentProduct["productId"] not in self.mPendingProducts:
                    self.mCurrentInternalOrderId += 1
                    self.mPendingInternalOrders[self.mCurrentInternalOrderId] = { "productId" : lCurrentProduct["productId"], "orderQuantity" : lCurrentProduct["reorderAmount"] }
                    self.mPendingProducts.append(lCurrentProduct["productId"])
    #ProcessInternalStockThreshold


    #--------------------------------------------------------------------------
    def FillInternalOrders( self, aCompleteOrders ):
        lResultDict = {"unknownIds":[]}
        for lCurrentOrderId in aCompleteOrders["orderIds"]:
            if lCurrentOrderId in self.mPendingInternalOrders: 
                lTargetProduct = self.mPendingInternalOrders[lCurrentOrderId]["productId"]
                self.mProductDict[lTargetProduct]["quantityOnHand"] += self.mPendingInternalOrders[lCurrentOrderId]["orderQuantity"]
                #Now that we have restored the quantitiy of the product due to the order, it's time to delete
                #Our pending order indicators so we can receive new orders for this product when it runs out again
                self.mPendingInternalOrders.pop(lCurrentOrderId, None)
                self.mPendingProducts.remove(lTargetProduct)
            else:
                lResultDict["unknownIds"].append(lCurrentOrderId)
                
        return lResultDict
    #FillInternalOrders       

    #Helper functions for internal tests
    #--------------------------------------------------------------------------
    def GetInternalOrders( self ):
        return self.mPendingInternalOrders
    def GetCurrentOrders( self ):
        return self.mOrderDict
    def GetProductQuantities( self ):
        return self.mProductDict
                    