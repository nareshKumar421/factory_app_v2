# GRPO App Documentation

The GRPO (Goods Receipt Purchase Order) app handles the posting of goods receipts to SAP B1 after gate entry completion.

## Overview

This app provides APIs to:
1. View completed gate entries pending GRPO posting
2. Preview GRPO data before posting
3. Post GRPO to SAP
4. View GRPO posting history

## Documentation Index

- [API Reference](api_reference.md) - Complete API documentation with endpoints, payloads, and responses
- [Models](models.md) - Database models and their relationships
- [Workflow](workflow.md) - GRPO posting workflow and business logic
- [Error Codes](error_codes.md) - Error codes and troubleshooting

## Quick Start

### Prerequisites
- Gate entry must be in `COMPLETED` or `QC_COMPLETED` status
- All PO items must have completed QC (ACCEPTED or REJECTED)
- User must be authenticated with company context

### Basic Flow

1. **Get Pending Entries**
   ```
   GET /api/v1/grpo/pending/
   ```

2. **Preview GRPO Data**
   ```
   GET /api/v1/grpo/preview/<vehicle_entry_id>/
   ```

3. **Post GRPO to SAP**
   ```
   POST /api/v1/grpo/post/
   {
     "vehicle_entry_id": 123,
     "po_receipt_id": 456
   }
   ```

4. **View Posting History**
   ```
   GET /api/v1/grpo/history/
   ```
