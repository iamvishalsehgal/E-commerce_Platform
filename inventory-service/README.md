Steps to deploy the **Inventory service ** on Google Cloud Run. The service handles 4 operations
2. add into inventory
3. update inventrory
4. deduct


# Create Inventory
curl -X POST https://inventory-service-1070510678521.us-central1.run.app/inventory \
-H "Content-Type: application/json" \
-d '{
  "product_id": "phone",
  "quantity": 100,
  "location": "Amsterdam"
}'

# check inventory
curl https://inventory-service-1070510678521.us-central1.run.app/inventory/phone

# update inventory 
curl -X PUT https://inventory-service-1070510678521.us-central1.run.app/inventory/phone \ 
-H "Content-Type: application/json" \
-d '{
  "quantity": 75,
  "location": "Rotterdam"
}'

# deduct inventory by forcing a pub/sub event via rest api
curl -X POST \
  https://inventory-service-1070510678521.us-central1.run.app/inventory/phone/deduct \
  -H "Content-Type: application/json" \
  -d '{"quantity": 2}'