# Tracking Service
### How to deploy this code to GCP
- Create a dataset `group2_trackingdb` in **BigQuery** under your project.
- In cloud shell, run the following command if port `5003` is not open yet. 
    ```bash
    gcloud compute firewall-rules create flask-port-5003 --allow tcp:5003
    ``` 
- Create a trigger in **Cloud Build** using the `cloudbuild_cloudrun_tracking.json` file. Remember to add two variables `_LOCATION = us-central1` and `_REPOSITORY = labrepo`.
- Run the trigger.
### How to test the deployment
  - In **Cloud Run** we can find the created service `tracking-service`. Click the service name to the detail page of the service. Copy the URL.
  - In Insomnia, create a workspace (if necessary), add a collection to the workspace (if necessary). 
  - Test Tracking Register Operation
    - Create a new **HTTP Request**.
    - Change the HTTP method to `POST`.
    - Use `url-you-just-copied/tracking/register` as the url.
    - Use the following data as body:
      ```json
      {
        "id":2025008,
        "latitude": "51.688023",
        "longitude": "5.298669"
      }
      ```
    - Send the request.
    - If there is not a record with `id=2025008`, it will return the following code:
      ```json
      {
        "tracking_id": 2025008
      }
      ```
  - Test Getting Tracking Info Operation
    - Create a new **HTTP Request**.
    - Change the HTTP method to `GET`. 
    - Use `url-you-just-copied/tracking/2025008` as the url.
    - Send the request.
    - If there is already a record with `id=2025008`, it will return a data in the following format:
      ```json
      {
         "latitude": "52.888888",
         "longitude": "5.202222",
         "tracking_id": 2025008,
         "update_time": "Sun, 04 May 2025 19:43:57 GMT"
      }
      ```
    
  - Test Tracking Update Operation
    - Create a new **HTTP Request**.
    - Change the HTTP method to `PUT`.
    - Use `url-you-just-copied/tracking/2025008?latitude=52.888888&longitude=5.202222` as the url.
    - Send the request.
    - If there is already a record with `id=2025008`, it will return the following code:
      ```json
      {
        "message": "Tracking info updated"
      }
      ```
    - After that, if we send a **GET** request, it will return the updated data.