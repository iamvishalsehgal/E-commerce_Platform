# Inventory Service
### Deployment to GCP
1. Create a BigQuery dataset `group2_inventorydb` in your project.
2. Open port 5004 in the firewall:
   ```bash
   gcloud compute firewall-rules create flask-port-5004 --allow tcp:5004



# Create Inventory
curl -X POST https://inventory-service-1070510678521.us-central1.run.app/inventory \
-H "Content-Type: application/json" \
-d '{
  "product_id": "laptop",
  "quantity": 50,
  "location": "Denbosch"
}'

# Create order 
curl -X POST https://order-service-1070510678521.us-central1.run.app/orders \
-H "Content-Type: application/json" \
-d '{
  "customer_id": "vishal",
  "product_id": "laptop",
  "quantity": 3
}'

# Validate order 
curl -X PUT https://order-service-1070510678521.us-central1.run.app/orders/{order_id}/validate


# Check order status
curl https://order-service-1070510678521.us-central1.run.app/orders/{order_id}

# to cancel
curl -X PUT https://order-service-1070510678521.us-central1.run.app/orders/{order_id}/cancel

# change delivery status 
curl -X PUT "https://order-service-1070510678521.us-central1.run.app/orders/{order_id}/delivery?status=shipped"