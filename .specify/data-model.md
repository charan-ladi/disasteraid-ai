# Database Schema

## incidents

| Field | Type |
|--------|------|
| id | INTEGER |
| disaster_type | TEXT |
| severity | TEXT |
| people_trapped | INTEGER |
| children | INTEGER |
| elderly | INTEGER |
| injured | BOOLEAN |
| food_needed | BOOLEAN |
| water_needed | BOOLEAN |
| medicine_needed | BOOLEAN |
| location | TEXT |
| latitude | REAL |
| longitude | REAL |
| timestamp | TEXT |
| status | TEXT |
| priority_score | INTEGER |

---

## reports

| Field | Type |
|--------|------|
| id | INTEGER |
| incident_id | INTEGER |
| source_type | TEXT |
| filename | TEXT |
| extracted_text | TEXT |