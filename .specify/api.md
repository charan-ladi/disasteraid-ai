# Internal API Specification

POST /upload

Inputs

- image
- video
- audio
- pdf
- text

Response

{
    status
}

---

POST /extract

Returns

{
 structured_json
}

---

GET /dashboard

Returns

All incidents.

---

GET /incident/{id}

Returns

Incident details.

---

GET /export/json

Downloads JSON.

---

GET /export/csv

Downloads CSV.