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
| GET | `/person-types/` | `IsAuthenticated` + `view_persontype` |
| POST | `/person-types/` | `IsAuthenticated` + `can_manage_person_type` |
| GET | `/person-types/{id}/` | `IsAuthenticated` + `view_persontype` |
| PUT | `/person-types/{id}/` | `IsAuthenticated` + `can_manage_person_type` |
| DELETE | `/person-types/{id}/` | `IsAuthenticated` + `can_manage_person_type` |

---

#### 2. Gates (ViewSet)

| Method | Endpoint | Permission Required |
|--------|----------|---------------------|
| GET | `/gates/` | `IsAuthenticated` + `view_gate` |
| POST | `/gates/` | `IsAuthenticated` + `can_manage_gate` |
| GET | `/gates/{id}/` | `IsAuthenticated` + `view_gate` |
| PUT | `/gates/{id}/` | `IsAuthenticated` + `can_manage_gate` |
| DELETE | `/gates/{id}/` | `IsAuthenticated` + `can_manage_gate` |

---

#### 3. Contractors (ViewSet)

| Method | Endpoint | Permission Required |
|--------|----------|---------------------|
| GET | `/contractors/` | `IsAuthenticated` + `view_contractor` |
| POST | `/contractors/` | `IsAuthenticated` + `add_contractor` |
| GET | `/contractors/{id}/` | `IsAuthenticated` + `view_contractor` |
| PUT/PATCH | `/contractors/{id}/` | `IsAuthenticated` + `change_contractor` |
| DELETE | `/contractors/{id}/` | `IsAuthenticated` + `delete_contractor` |

---

#### 4. Visitors (ViewSet)

| Method | Endpoint | Permission Required |
|--------|----------|---------------------|
| GET | `/visitors/` | `IsAuthenticated` + `view_visitor` |
| POST | `/visitors/` | `IsAuthenticated` + `add_visitor` |
| GET | `/visitors/{id}/` | `IsAuthenticated` + `view_visitor` |
| PUT/PATCH | `/visitors/{id}/` | `IsAuthenticated` + `change_visitor` |
| DELETE | `/visitors/{id}/` | `IsAuthenticated` + `delete_visitor` |

---

#### 5. Labours (ViewSet)

| Method | Endpoint | Permission Required |
|--------|----------|---------------------|
| GET | `/labours/` | `IsAuthenticated` + `view_labour` |
| POST | `/labours/` | `IsAuthenticated` + `add_labour` |
| GET | `/labours/{id}/` | `IsAuthenticated` + `view_labour` |
| PUT/PATCH | `/labours/{id}/` | `IsAuthenticated` + `change_labour` |
| DELETE | `/labours/{id}/` | `IsAuthenticated` + `delete_labour` |

---

### Entry APIs

#### 6. Create Entry (Gate-In)

```
POST /entry/create/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.add_entrylog`

---

#### 7. Entry Detail

```
GET /entry/{id}/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.view_entrylog`

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

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.change_entrylog`

---

#### 11. Inside List (Currently Inside)

```
GET /entry/inside/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.view_entrylog`

---

#### 12. Entries by Date

```
GET /entries/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.view_entrylog`

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

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.view_entrylog`

---

#### 15. Labour Entry History

```
GET /labour/{labour_id}/history/
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.view_entrylog`

---

#### 16. Check Person Status

```
GET /check-status/?visitor={id} or ?labour={id}
```

**Permission Required:** `IsAuthenticated` + `HasCompanyContext` + `person_gatein.view_entrylog`

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
| `/person-types/` | GET | `view_persontype` |
| `/person-types/` | POST/PUT/DELETE | `can_manage_person_type` |
| `/gates/` | GET | `view_gate` |
| `/gates/` | POST/PUT/DELETE | `can_manage_gate` |
| `/contractors/` | GET | `view_contractor` |
| `/contractors/` | POST | `add_contractor` |
| `/contractors/{id}/` | PUT/PATCH | `change_contractor` |
| `/contractors/{id}/` | DELETE | `delete_contractor` |
| `/visitors/` | GET | `view_visitor` |
| `/visitors/` | POST | `add_visitor` |
| `/visitors/{id}/` | PUT/PATCH | `change_visitor` |
| `/visitors/{id}/` | DELETE | `delete_visitor` |
| `/labours/` | GET | `view_labour` |
| `/labours/` | POST | `add_labour` |
| `/labours/{id}/` | PUT/PATCH | `change_labour` |
| `/labours/{id}/` | DELETE | `delete_labour` |
| `/entry/create/` | POST | `add_entrylog` |
| `/entry/{id}/` | GET | `view_entrylog` |
| `/entry/{id}/exit/` | POST | `can_exit_entry` |
| `/entry/{id}/cancel/` | POST | `can_cancel_entry` |
| `/entry/{id}/update/` | PATCH | `change_entrylog` |
| `/entry/inside/` | GET | `view_entrylog` |
| `/entries/` | GET | `view_entrylog` |
| `/entries/search/` | GET | `can_search_entry` |
| `/visitor/{id}/history/` | GET | `view_entrylog` |
| `/labour/{id}/history/` | GET | `view_entrylog` |
| `/check-status/` | GET | `view_entrylog` |
| `/dashboard/` | GET | `can_view_dashboard` |

## All Permissions

| Permission Codename | Description |
|---------------------|-------------|
| `person_gatein.view_persontype` | Can view person type |
| `person_gatein.can_manage_person_type` | Can manage person type |
| `person_gatein.view_gate` | Can view gate |
| `person_gatein.can_manage_gate` | Can manage gate |
| `person_gatein.add_contractor` | Can add contractor |
| `person_gatein.view_contractor` | Can view contractor |
| `person_gatein.change_contractor` | Can change contractor |
| `person_gatein.delete_contractor` | Can delete contractor |
| `person_gatein.add_visitor` | Can add visitor |
| `person_gatein.view_visitor` | Can view visitor |
| `person_gatein.change_visitor` | Can change visitor |
| `person_gatein.delete_visitor` | Can delete visitor |
| `person_gatein.add_labour` | Can add labour |
| `person_gatein.view_labour` | Can view labour |
| `person_gatein.change_labour` | Can change labour |
| `person_gatein.delete_labour` | Can delete labour |
| `person_gatein.add_entrylog` | Can add entry log |
| `person_gatein.view_entrylog` | Can view entry log |
| `person_gatein.change_entrylog` | Can change entry log |
| `person_gatein.delete_entrylog` | Can delete entry log |
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
