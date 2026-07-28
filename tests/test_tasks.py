# ---------- POST /tasks ----------
from datetime import date, timedelta

def test_create_task_valid_returns_201_with_full_body(client):
    response = client.post("/tasks", json={"title": "Write report", "priority": "High"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write report"
    assert body["priority"] == "High"
    assert body["status"] == "ToDo"
    assert "id" in body and "created_at" in body and "updated_at" in body


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "x", "priority": "Urgent"})
    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "x", "made_up": "value"})
    assert response.status_code == 422


# ---------- GET /tasks ----------

def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client, created_task):
    response = client.get("/tasks", params={"status": "Done"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "low one", "priority": "Low"})
    client.post("/tasks", json={"title": "high one", "priority": "High"})
    response = client.get("/tasks", params={"priority": "High"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "high one"


# ---------- GET /tasks/{id} ----------

def test_get_task_by_id_returns_task(client, created_task):
    response = client.get(f"/tasks/{created_task['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created_task["id"]


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    response = client.get("/tasks/does-not-exist")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# ---------- PATCH /tasks/{id} ----------

def test_patch_partial_update_keeps_other_fields(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"priority": "High"})
    assert response.status_code == 200
    body = response.json()
    assert body["priority"] == "High"
    assert body["title"] == created_task["title"]


def test_patch_not_found_returns_404(client):
    response = client.patch("/tasks/does-not-exist", json={"priority": "High"})
    assert response.status_code == 404


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "InProgress"})
    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "Done"})
    assert response.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "ToDo"})
    assert response.status_code == 422


def test_patch_invalid_priority_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"priority": "Urgent"})
    assert response.status_code == 422


# ---------- DELETE /tasks/{id} ----------

def test_delete_existing_returns_204_no_body(client, created_task):
    response = client.delete(f"/tasks/{created_task['id']}")
    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    response = client.delete("/tasks/does-not-exist")
    assert response.status_code == 404

# ---------- Mid-course Feature 1: due dates + overdue filter ----------

def test_create_task_with_valid_due_date_returns_201(client):
    due = (date.today() + timedelta(days=3)).isoformat()
    response = client.post("/tasks", json={"title": "Ship release", "due_date": due})
    assert response.status_code == 201
    assert response.json()["due_date"] == due


def test_create_task_with_invalid_due_date_format_returns_422(client):
    response = client.post("/tasks", json={"title": "x", "due_date": "next tuesday"})
    assert response.status_code == 422


def test_patch_update_due_date_changes_value(client, created_task):
    new_due = (date.today() + timedelta(days=10)).isoformat()
    response = client.patch(f"/tasks/{created_task['id']}", json={"due_date": new_due})
    assert response.status_code == 200
    assert response.json()["due_date"] == new_due


def test_list_tasks_overdue_filter_returns_only_overdue(client):
    past = (date.today() - timedelta(days=2)).isoformat()
    future = (date.today() + timedelta(days=2)).isoformat()

    client.post("/tasks", json={"title": "late task", "due_date": past})
    client.post("/tasks", json={"title": "upcoming task", "due_date": future})
    client.post("/tasks", json={"title": "no due date"})

    # A Done task with a past due date should NOT count as overdue.
    done_task = client.post("/tasks", json={"title": "finished late", "due_date": past}).json()
    client.patch(f"/tasks/{done_task['id']}", json={"status": "InProgress"})
    client.patch(f"/tasks/{done_task['id']}", json={"status": "Done"})

    response = client.get("/tasks", params={"overdue": "true"})
    assert response.status_code == 200
    titles = {t["title"] for t in response.json()}
    assert titles == {"late task"}


# ---------- Mid-course Feature 2: tags ----------

def test_create_task_with_tags_returns_tags_in_body(client):
    response = client.post("/tasks", json={"title": "Tagged task", "tags": ["backend", "urgent"]})
    assert response.status_code == 201
    assert response.json()["tags"] == ["backend", "urgent"]


def test_create_task_with_blank_tag_returns_422(client):
    response = client.post("/tasks", json={"title": "x", "tags": ["ok", "   "]})
    assert response.status_code == 422


def test_patch_update_tags_replaces_list(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"tags": ["frontend"]})
    assert response.status_code == 200
    assert response.json()["tags"] == ["frontend"]


def test_list_tasks_filter_by_tag_returns_only_matches(client):
    client.post("/tasks", json={"title": "a", "tags": ["backend"]})
    client.post("/tasks", json={"title": "b", "tags": ["frontend"]})
    response = client.get("/tasks", params={"tag": "backend"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "a"


def test_patch_unrelated_update_preserves_tags(client):
    created = client.post("/tasks", json={"title": "keep tags", "tags": ["backend"]}).json()
    response = client.patch(f"/tasks/{created['id']}", json={"priority": "High"})
    assert response.status_code == 200
    assert response.json()["tags"] == ["backend"]