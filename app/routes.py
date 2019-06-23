from flask import request, jsonify
from app import app


@app.route('/api/v1/warehouse/fulfilment', methods=['POST'])
def ProcessOrders():
    return "Oh boy it worked"
    

@app.errorhandler(405)
def WrongMethodError(error):
    return "Use a valid method"
    