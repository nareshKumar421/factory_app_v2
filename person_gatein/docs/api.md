# Person Gate-In API Documentation

## Base URL
```
/api/v1/person-gatein/
```

## Headers Required
```
Authorization: Bearer <access_token>
Company-Code: <company_code>
```

---

## Endpoints

### Master APIs

#### 1. Person Types (ViewSet)

| Method | Endpoint | Permission Required |
|--------|----------|---------------------|
| GET | `/person-types/` | `IsAuthenticated` + `can_view_person_type` |
| POST | `/person-types/` | `IsAuthenticated` + `can_manage_person_type` |
| GET | `/person-types/{id}/` | `IsAuthenticated` + `can_view_person_type` |
| PUT | `/person-types/{id}/` | `IsAuthenticated` + `can_manage_person_type` |
| DELETE | `/person-types/{id}/` | `IsAuthenticated` + `can_manage_person_type` |

---

#### 2. Gates (ViewSet)

| Method | Endpoint | Permission Required |
|--------|----------|---------------------|
| GET | `/gates/` | `IsAuthenticated` + `can_view_gate` |
| POST | `/gates/` | `IsAuthenticated` + `can_manage_gate` |
| GET | `/gates/{id}/` | `IsAuthenticated` + `can_view_gate` |
| PUT | `/gates/{id}/` | `IsAuthenticated` + `can_manage_gate` |
| DELETE | `/gates/{id}/` | `IsAuthenticated` + `can_manage_gate` |

---

#### 3. Contractors (ViewSet)

| Method | Endpoint | Permission Required |
|--------|----------|---------------------|
| GET | `/contractors/` | `IsAuthenticated` + `can_view_contractor` |
| POST | `/contractors/` | `IsAuthenticated` + `can_create_contractor` |
| GET | `/contractors/{id}/` | `IsAuthenticated` + `can_view_contractor` |
| PUT/PATCH | `/contractors/{id}/` | `IsAuthenticated` + `can_edit_contractor` |
| DELETE | `/contractors/{id}/` | `IsAuthenticated` + `can_delete_contractor` |

---

#### 4. Visitors (ViewSet)

| Method | Endpoint | Permission Required |
|--------|----------|---------------------|
| GET | `/visitors/` | `IsAuthenticated` + `can_view_visitor` |
| POST | `/visitors/` | `IsAuthenticated` + `can_create_visitor` |
| GET | `/visitors/{id}/` | `IsAuthenticated` + `can_view_visitor` |
| PUT/PATCH | `/visitors/{id}/` | `IsAuthenticated` + `can_edit_visitor` |
| DELETE | `/visitors/{id}/` | `IsAuthenticated` + `can_delete_visitor` |

---

#### 5. Labours (ViewSet)

| Method | Endpoint | Permission Required |
|--------|----------|---------------------|
| GET | `/labours/` | `IsAuthenticated` + `can_view_labour` |
| POST | `/labours/` | `IsAuthenticated` + `can_create_labour` |
| GET | `/labours/{id}/` | `IsAuthenticated` + `can_view_labour` |
| PUT/PATCH | `/labours/{id}/` | `IsAuthenticated` + `can_edit_labour` |
| DELETE | `/labours/{id}/` | `IsAuthenticated` + `can_delete_labour` |

---

### Entry APIs

#### 6. Create Entry (Gate-In)

```
POST /entry/create/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.can_create_entry`

---

#### 7. Entry Detail

```
GET /entry/{id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.can_view_entry`

---

#### 8. Exit Entry (Gate-Out)

```
POST /entry/{id}/exit/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.can_exit_entry`

---

#### 9. Cancel Entry

```
POST /entry/{id}/cancel/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.can_cancel_entry`

---

#### 10. Update Entry

```
PATCH /entry/{id}/update/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.can_edit_entry`

---

#### 11. Inside List (Currently Inside)

```
GET /entry/inside/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.can_view_entry`

---

#### 12. Entries by Date

```
GET /entries/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.can_view_entry`

**Query Parameters:** `date`, `start_date`, `end_date`, `status`, `person_type`, `gate_in`, `visitor`, `labour`

---

#### 13. Search Entries

```
GET /entries/search/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.can_search_entry`

**Query Parameters:** `q` (required), `status` (optional)

---

### History & Status APIs

#### 14. Visitor Entry History

```
GET /visitor/{visitor_id}/history/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.can_view_entry`

---

#### 15. Labour Entry History

```
GET /labour/{labour_id}/history/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.can_view_entry`

---

#### 16. Check Person Status

```
GET /check-status/?visitor={id} or ?labour={id}
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.can_view_entry`

---

### Dashboard API

#### 17. Dashboard Statistics

```
GET /dashboard/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.can_view_dashboard`

---

## Permission Summary

| Endpoint | Method | Permission Codename |
|----------|--------|---------------------|
| `/person-types/` | GET | `can_view_person_type` |
| `/person-types/` | POST/PUT/DELETE | `can_manage_person_type` |
| `/gates/` | GET | `can_view_gate` |
| `/gates/` | POST/PUT/DELETE | `can_manage_gate` |
| `/contractors/` | GET | `can_view_contractor` |
| `/contractors/` | POST | `can_create_contractor` |
| `/contractors/{id}/` | PUT/PATCH | `can_edit_contractor` |
| `/contractors/{id}/` | DELETE | `can_delete_contractor` |
| `/visitors/` | GET | `can_view_visitor` |
| `/visitors/` | POST | `can_create_visitor` |
| `/visitors/{id}/` | PUT/PATCH | `can_edit_visitor` |
| `/visitors/{id}/` | DELETE | `can_delete_visitor` |
| `/labours/` | GET | `can_view_labour` |
| `/labours/` | POST | `can_create_labour` |
| `/labours/{id}/` | PUT/PATCH | `can_edit_labour` |
| `/labours/{id}/` | DELETE | `can_delete_labour` |
| `/entry/create/` | POST | `can_create_entry` |
| `/entry/{id}/` | GET | `can_view_entry` |
| `/entry/{id}/exit/` | POST | `can_exit_entry` |
| `/entry/{id}/cancel/` | POST | `can_cancel_entry` |
| `/entry/{id}/update/` | PATCH | `can_edit_entry` |
| `/entry/inside/` | GET | `can_view_entry` |
| `/entries/` | GET | `can_view_entry` |
| `/entries/search/` | GET | `can_search_entry` |
| `/visitor/{id}/history/` | GET | `can_view_entry` |
| `/labour/{id}/history/` | GET | `can_view_entry` |
| `/check-status/` | GET | `can_view_entry` |
| `/dashboard/` | GET | `can_view_dashboard` |

## All Permissions

| Permission Codename | Description |
|---------------------|-------------|
| `person_gatein.can_view_person_type` | Can view person type |
| `person_gatein.can_manage_person_type` | Can manage person type |
| `person_gatein.can_view_gate` | Can view gate |
| `person_gatein.can_manage_gate` | Can manage gate |
| `person_gatein.can_create_contractor` | Can create contractor |
| `person_gatein.can_view_contractor` | Can view contractor |
| `person_gatein.can_edit_contractor` | Can edit contractor |
| `person_gatein.can_delete_contractor` | Can delete contractor |
| `person_gatein.can_create_visitor` | Can create visitor |
| `person_gatein.can_view_visitor` | Can view visitor |
| `person_gatein.can_edit_visitor` | Can edit visitor |
| `person_gatein.can_delete_visitor` | Can delete visitor |
| `person_gatein.can_create_labour` | Can create labour |
| `person_gatein.can_view_labour` | Can view labour |
| `person_gatein.can_edit_labour` | Can edit labour |
| `person_gatein.can_delete_labour` | Can delete labour |
| `person_gatein.can_create_entry` | Can create person gate entry |
| `person_gatein.can_view_entry` | Can view person gate entry |
| `person_gatein.can_edit_entry` | Can edit person gate entry |
| `person_gatein.can_delete_entry` | Can delete person gate entry |
| `person_gatein.can_cancel_entry` | Can cancel person gate entry |
| `person_gatein.can_exit_entry` | Can mark person gate exit |
| `person_gatein.can_search_entry` | Can search person gate entries |
| `person_gatein.can_view_dashboard` | Can view person gate dashboard |

---

## Error Responses

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```
