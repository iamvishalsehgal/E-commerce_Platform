# Tracking Service
### How to deploy this code to GCP
- Create a dataset `group2_trackingdb` in **BigQuery** under your project.
- Create a trigger in **Cloud Build** using `cloudbuild_cloudrun_tracking.json` file.
- Run the trigger.