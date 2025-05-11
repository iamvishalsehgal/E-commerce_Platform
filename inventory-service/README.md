# Inventory Service
### Deployment to GCP
1. Create BigQuery dataset `group2_inventorydb` in project
2. Open port 5005:
   ```bash
   gcloud compute firewall-rules create flask-port-5005 --allow tcp:5005