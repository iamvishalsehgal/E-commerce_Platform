# Order Service Deployment Guide

Steps to deploy the **Order Service** on Google Cloud Run. The service handles 5 operations
1. create_order
2. get_status
3. cancle_order
4. validate_order
5. update_Delivery

 using a Flask application with Pub/Sub integration.

## Steps
- Step 1. Navigate to the `order-service/` directory.

```bash
cd order-service
```

- Step 2. Deploy the Order Service to Google Cloud Run using  `cloudbuild_cloudrun_order.json` configuration. This step builds a Docker image, pushes it to Artifact Registry, and deploys it to Cloud Run.

Run the following command in your terminal (I use Vscode)

```bash
gcloud builds submit --config cloudbuild_cloudrun_order.json --substitutions=_TAG=0.0.1
```

- Step 3. Test the Service 
After deployment, Cloud Run will provide a service URL (e.g., `https://order-service-XXXXXX-uc.a.run.app`). Use this URL to test the service endpoints. Example commands using `curl`:


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
  ```

- Step 4: Delete the Service
To remove the deployed service from Cloud Run, run the following command:

```bash
gcloud run services delete order-service --region=us-central1
```

## Notes
- Ensure the BigQuery database (`group2_orderdb`) and Pub/Sub topics/subscriptions (`order-events`, `inventory-events`, `order-inventory-events-sub`) are set up before deployment.
- The service runs on port `5004` as specified in the `Dockerfile` and Cloud Run configuration.