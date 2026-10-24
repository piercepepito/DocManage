# Docmanage - A Document Management and Version Control System

## What is DocManage?

DocManage is a backend application that manages documents through a REST API. It provides CRUD operations, document version tracking, and the ability to compare changes between saved versions and restore previous versions.

The application focuses on reliable data handling and efficient document processing, making it easier to manage document changes while preserving version history.

## Why DocManage?

Document changes can sometimes result in valuable information being accidentally deleted or important details being lost. When this happens, recovering previous content can be difficult without a reliable version history.

DocManage addresses this problem by preserving previous document versions, allowing users to review changes, compare revisions, and restore earlier versions when needed. By maintaining a history of document changes, it helps protect valuable information and provides a reliable way to recover from mistakes. 

## Main Features

1. Document Management
    1. Perform CRUD operations through REST API endpoints
    2. Maintain document data in Supabase (PostgreSQL)
2. Document Version Control
    1. Preserve previous document versions to prevent valuable information from being permanently lost
    2. Compare saved versions to identify changes between revisions
    3. Restore previous versions when needed
3. External Service Integration
    1. Integrated with [DocView](https://github.com/piercepepito/DocView) to make documents easier to review
    2. Generates an HMAC signature to help verification of webhook payloads
    3. Document updates are sent to DocView for preview generation and AI-powered summarization. 
4. Reliable server to server communication (*In Progress*)
    1. **Idempotency**: Prevent duplicate processing from causing unintended repeated effects
    2. **Automatic Retries**: Retries sending of data with exponential backoff + jitter, to improve the chances of a sucessful delivery
    3. **Dead Letter Queue**: Isolate events that haven't been succesfully sent for investigation and recovery

## Reliability and Quality Assurance

1. Error Handling
    1. Validate input data and handle failures appropriately
    2. Return the appropriate HTTP status codes and error responses
    3. Handle communication failures and unsuccesful operations without losing any important error messages both on the user and server side, while avoiding any sensitive data

2. Automated Testing
    1. **Unit Tests**: Verify individual functions for their intended use and test for edge cases to ensure reliability
    2. **Integration Tests**: Verify functions work together with different components such as a database and other external services

## how does its architecture work?



## How can someone run and test it?
1. .env file
2. Setup docker