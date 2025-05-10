# Order Service
### Deployment to GCP
1. Create a BigQuery dataset `group2_orderdb` in project.
2. Open port 5004:
   ```bash
   gcloud compute firewall-rules create flask-port-5004 --allow tcp:5004