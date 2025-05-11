import functions_framework
import random
import string
from flask import jsonify

@functions_framework.http
def request_delivery(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'orderid' in request_json and 'senderinfo' in request_json and 'receiverinfo' in request_json:
        order_id = request_json['orderid']
        sender_info = request_json['senderinfo']
        receiver_info = request_json['receiverinfo']
    elif request_args and 'orderid' in request_args and 'senderinfo' in request_args and 'receiverinfo' in request_args:
        order_id = request_args['orderid']
        sender_info = request_args['senderinfo']
        receiver_info = request_args['receiverinfo']
    else:
        return jsonify({"error": "Missing order ID, sender info, or receiver info"}), 400

    delivery_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    return jsonify({
        "message": "Delivery accepted",
        "order_id": order_id,
        "delivery_id": delivery_id,
        "sender": sender_info,
        "receiver": receiver_info
    }), 200
