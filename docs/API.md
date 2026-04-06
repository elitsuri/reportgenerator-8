# reportgenerator — API Reference

All endpoints are prefixed with `/api/v1`.
Protected endpoints require `Authorization: Bearer <token>` header.

---

## Authentication

### POST /auth/register
Create a new user account.
**Body:** `{ email, password, full_name }`
**Response:** `201` `{ id, email, full_name, role }`

### POST /auth/login
Obtain a JWT access token.
**Body (form):** `username=<email>&password=<password>`
**Response:** `200` `{ access_token, token_type }`

### GET /auth/me
Return the authenticated user's profile. **Protected.**
**Response:** `200` `{ id, email, full_name, role, is_active }`

---

## Items

### GET /items/
List items with pagination. **Protected.**
**Query:** `page`, `page_size`
**Response:** `200` `{ items: [...], total, page, pages }`

### POST /items/
Create a new item. **Protected.**
**Body:** `{ title, description }`
**Response:** `201` item object

### GET /items/{id}
Retrieve a single item by ID. **Protected.**
**Response:** `200` item object | `404`

### PUT /items/{id}
Update an item. **Protected (owner or admin).**
**Body:** `{ title?, description? }`
**Response:** `200` updated item

### DELETE /items/{id}
Delete an item. **Protected (owner or admin).**
**Response:** `204`

---

## Analytics

### GET /analytics/overview
Aggregated stats. **Protected.**
**Response:** `{ total_items, total_users, total_notifications, items_this_week, active_users_today }`

### GET /analytics/timeseries?days=30
Daily item creation counts. **Protected.**
**Response:** `{ points: [{ date, count }], total }`

### GET /analytics/top-items?limit=10
Top items by view count. **Protected.**
**Response:** `[{ id, title, view_count, created_at }]`

---

## Notifications

### GET /notifications/ — list all; includes `unread_count`
### POST /notifications/ — create; body `{ title, body, type }`
### POST /notifications/{id}/read — mark single as read
### POST /notifications/read-all — mark all as read
### DELETE /notifications/{id} — delete

---

## Settings

### GET /settings/ — get user preferences
### PUT /settings/ — update; body `{ theme?, language?, timezone?, notifications_enabled? }`

---

## Admin  *(admin role required)*

### GET /admin/users — list all users
### PUT /admin/users/{id}/role — body `{ role: 'admin'|'user'|'moderator' }`
### DELETE /admin/users/{id} — permanently delete user
### GET /admin/stats — `{ total_users, active_users, total_items }`

---

## Search

### GET /search/?q=&type=all|items|users
**Response:** `{ items: [...], users: [...] }`

---

## Upload

### POST /upload/file
Multipart form upload. Max 10 MB. Allowed: jpeg/png/gif/webp/pdf/text/csv.
**Response:** `201` `{ url, filename, size }`

---

## Health

### GET /health/ — public health check
**Response:** `{ status, version, components: { database, cache, disk } }`

---

## Error responses
All errors return `{ detail: string }`. Validation errors include `errors` array.
HTTP status codes: `400` Bad Request, `401` Unauthorized, `403` Forbidden,
`404` Not Found, `409` Conflict, `413` Too Large, `415` Unsupported Type,
`422` Unprocessable Entity, `429` Rate Limited, `500` Internal Error.
