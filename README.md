Overview

This repository contains the implementation for Assignment 2 of the Advance Data Architecture (ADA) course, developed by Group 2. It focuses on building a part of an E-commerce platform, covering the design and deployment of microservices across three domains: Order, Product, and Delivery.

Domains

The project is structured around three domains:





Order (Core Domain): Manages order-related operations.



Product (Core Domain): Handles product inventory and stock management.



Delivery (Support Domain): Supports delivery and tracking functionalities.

Microservices and Operations

The implementation includes 4 microservices with a total of 14 operations:

Order Domain (Core)





Order Service (RESTful Service):





create_order: Creates a new order.



get_status: Retrieves the status of an order.



cancel_order: Cancels an existing order.



validate_order: Validates order details.



update_delivery: Updates delivery information for an order.

Product Domain (Core)





Product Service (RESTful Service):





add_product: Adds a new product to the catalog.



check_stock: Checks product stock availability.



update_stock: Updates stock levels.



deduct_inventory: Deducts inventory upon order fulfillment.

Delivery Domain (Support)





Inventory Service (FaaS):





delivery-request: Initiates a delivery request.



shipping-label-generate: Generates a shipping label.



Tracking Service (RESTful Service):





register_tracking: Registers tracking for a delivery.



get_tracking_status: Retrieves the current tracking status.



update_tracking_status: Updates the tracking status.

Orchestration

A workflow for delivery registration is implemented in the file \orchestration\delivery-register-process.yaml. The main steps include:





Register delivery



Generate shipping label



Register tracking



Update delivery status

Deployment

For detailed instructions on deploying each microservice, refer to the README.md files located in the respective service folders.
