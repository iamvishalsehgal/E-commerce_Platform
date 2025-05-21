# Assignment 2 for Advanced Data Architecture - Group 2

### Introduction
This is the repo for ADA course's assignment 2 - Implementation of the Design.

This is a part of an E-commerce platform.

### Domains

There are 3 domains in this part: order, product, and delivery. The first two domains are core domains, and the third one is a support domain.

### Microservices and Operations
4 microservices and 14 operations are implemented.
- Order Domain (Core)
  - Order Service (RESTful service)
    - create_order
    - get_status
    - cancel_order
    - validate_order
    - update_delivery
- Product Domain (Core)
  - Product Service (RESTful service)
    - add_product
    - check_stock
    - update_stock
    - deduct_inventory
- Delivery Domain (Support)
  - Inventory Service (Faas)
    - delivery-request
    - shipping-label-generate
  - Tracking Service (RESTful service)
    - register_tracking
    - get_tracking_status
    - update_tracking_status

### Orchestration
There is one workflow to handle delivery register. The script for this workflow is in `\orchestration\delivery-register-process.yaml`.

Main steps in this workflow:
1. Register delivery
2. Generate shipping label
3. Register tracking
4. Update delivery status

### How to deploy the services?
See the `README.md` files directly under the folders of the services.
