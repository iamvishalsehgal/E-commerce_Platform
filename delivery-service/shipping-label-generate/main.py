import functions_framework
import random
from flask import jsonify
from google.cloud import bigquery

@functions_framework.http
def generate_shipping_label(request):
    """HTTP Cloud Function that generates a shipping label."""

    request_json = request.get_json(silent=True)
    request_args = request.args

    # Extract parameters
    if request_json and all(k in request_json for k in ['orderid', 'deliveryid', 'senderinfo', 'receiverinfo']):
        order_id = request_json['orderid']
        delivery_id = request_json['deliveryid']
        sender_info = request_json['senderinfo']
        receiver_info = request_json['receiverinfo']
    elif request_args and all(k in request_args for k in ['orderid', 'deliveryid', 'senderinfo', 'receiverinfo']):
        order_id = request_args['orderid']
        delivery_id = request_args['deliveryid']
        sender_info = request_args['senderinfo']
        receiver_info = request_args['receiverinfo']
    else:
        return jsonify({"error": "Missing order ID, delivery ID, sender info, or receiver info"}), 400

    # Generate tracking ID and barcode
    tracking_id = random.randint(10**11, 10**12 - 1)  # 12-digit int
    barcode = ''.join(random.choices('0123456789', k=12))  # 12-digit string

    addDeliveryToDB(order_id, sender_info, receiver_info, delivery_id, tracking_id, barcode, "new")

    # Return all info
    return jsonify({
        "message": "Shipping label generated",
        "order_id": order_id,
        "delivery_id": delivery_id,
        "tracking_id": str(tracking_id),  # cast to string to avoid JSON number issues
        "barcode": barcode,
        "sender": sender_info,
        "receiver": receiver_info
    }), 200


def addDeliveryToDB(order_id, sender_info, receiver_info, delivery_id, tracking_id, barcode, delivery_status):
    # Construct a BigQuery client object
    client = bigquery.Client()

    # Define table ID (replace $PROJECT_ID)
    table_id = "de2024-435420.group2_deliverydb.delivery"  # Use actual project ID

    # Prepare the row to insert
    row = {
        "order_id": order_id,
        "id": delivery_id,
        "sender_info": sender_info,
        "reveiver_info": receiver_info,
        "barcode": barcode,
        "tracking_id": tracking_id,
        "delivery_status": delivery_status
    }

    # Use insert_rows_json for safer schema handling
    errors = client.insert_rows_json(table_id, [row])
    if errors:
        raise RuntimeError(f"BigQuery insert failed: {errors}")