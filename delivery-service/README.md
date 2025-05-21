## How to deploy the two delivery services

In delivery domain, we use Faas. There are two functions (two services): **delivery-request** and **shipping-label-generate**.

### Delivery Request Service
- Step 1. Navigate to `delivery-service/delivery-request/`.
    ```bash
    cd delivery-request
    ```
- Step 2. Create the GCloud Function.
  - Run the command below in Terminal (I use Pycharm).
    ```bash
    gcloud functions deploy delivery-request-http --gen2 --region=us-central1 --runtime=python312 --entry-point=request_delivery --trigger-http --allow-unauthenticated
    ```
- Step 3. Test.
  - The function creating step will generate an uri. Use this uri to test the http trigger.
- Step 4. Delete.
  - Run the command below in Terminal.
    ```bash
    gcloud functions delete delivery-request-http
    ```
    
### Shipping Label Generate Service
- Step 1. Navigate to `delivery-service/shipping-label-generate/`.
    ```bash
    cd shipping-label-generate
    ```
- Step 2. Create the GCloud Function.
  - Run the command below in Terminal (I use Pycharm).
    ```bash
    gcloud functions deploy shipping-label-generate-http --gen2 --region=us-central1 --runtime=python312 --entry-point=generate_shipping_label --trigger-http --allow-unauthenticated
    ```
- Step 3. Test.
  - The function creating step will generate an uri. Use this uri to test the http trigger.
- Step 4. Delete.
  - Run the command below in Terminal.
    ```bash
    gcloud functions delete shipping-label-generate-http
    ```
    