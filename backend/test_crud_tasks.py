import requests

API_URL = "http://localhost:8000/api/tasks/"
TOKEN = "eyJzdWIiOiAiNTdiZjljZjAtMjFkMC00OWE0LWFhMGUtMzRjNDUwYTdlYjQ0IiwgImVtYWlsIjogImFkbWluIiwgImlhbSI6ICJhZG1pbiIsICJleHAiOiAxNzAzNzYwMDAwLCAiaWF0IjogMTcwMzc1NjQwMH0ifQ=="
headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# Crear tarea
payload = {
    "titulo": "Tarea CRUD",
    "descripcion": "Prueba de creación",
    "tipo": "RECOLECCION",
    "prioridad": "MEDIA",
    "estado": "PENDIENTE",
    "progreso": 0
}

resp = requests.post(API_URL, json=payload, headers=headers)
print("CREAR:", resp.status_code, resp.text)

# Listar tareas
resp = requests.get(API_URL, headers=headers)
print("LISTAR:", resp.status_code, resp.text)

tasks = resp.json().get("tasks", []) if resp.ok else []
if tasks:
    task_id = tasks[0]["id"]
    # Actualizar tarea
    update_payload = {"estado": "EN_PROGRESO", "progreso": 50}
    resp = requests.patch(f"{API_URL}{task_id}", json=update_payload, headers=headers)
    print("ACTUALIZAR:", resp.status_code, resp.text)
    # Borrar tarea
    resp = requests.delete(f"{API_URL}{task_id}", headers=headers)
    print("BORRAR:", resp.status_code, resp.text)
else:
    print("No hay tareas para actualizar/borrar.")
