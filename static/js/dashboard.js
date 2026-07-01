async function loadIncidents() {
  const res = await fetch("/api/incidents");
  const incidents = await res.json();
  const body = document.getElementById("incidentBody");
  body.innerHTML = "";

  incidents.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.incident_id}</td>
      <td>${row.disaster_type || ""}</td>
      <td><span class="badge ${row.severity}">${row.severity || ""}</span></td>
      <td>${row.people_trapped ?? 0}</td>
      <td>${row.location || ""}</td>
      <td>${row.priority_score ?? 0}</td>
      <td>${row.status || ""}</td>
      <td><button class="delete-btn" data-id="${row.incident_id}">Delete</button></td>
    `;
    body.appendChild(tr);
  });

  document.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      await fetch(`/api/incidents/${btn.dataset.id}`, { method: "DELETE" });
      loadIncidents();
    });
  });
}

document.addEventListener("DOMContentLoaded", loadIncidents);
