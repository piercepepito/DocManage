# Company API

**Role:** Source of truth

This service simulates an existing company's document system. It owns the original documents and their authoritative versions.

## Responsibilities

- Create and store documents in its own PostgreSQL database.
- Assign each document a unique ID and an initial version.
- Retrieve document content and metadata.
- Update document content and increment its version.
- Send document-update webhooks to DocView when a document changes.