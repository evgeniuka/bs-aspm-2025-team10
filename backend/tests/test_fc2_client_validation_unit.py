from models.client import Client


def test_create_client_non_trainee_email_sets_user_id_none(client, create_user, auth_headers):
    trainer = create_user("trainer.validation@example.com", "trainer", full_name="Trainer")
    non_trainee = create_user("trainer.user@example.com", "trainer", full_name="Trainer User")
    headers = auth_headers(trainer)

    payload = {
        "name": "Casey Client",
        "age": 29,
        "fitness_level": "Beginner",
        "goals": "Improve overall strength and mobility",
        "user_email": non_trainee.email,
    }

    response = client.post("/api/clients", json=payload, headers=headers)

    assert response.status_code == 201
    data = response.get_json()
    assert data["user_id"] is None

    db_client = Client.query.filter_by(id=data["id"]).first()
    assert db_client.user_id is None


def test_update_client_invalid_fitness_level_returns_400(
    client, create_user, auth_headers, db_session
):
    trainer = create_user("trainer.update.fitness@example.com", "trainer", full_name="Trainer")
    headers = auth_headers(trainer)

    client_record = Client(
        trainer_id=trainer.id,
        name="Fitness Level Client",
        age=33,
        fitness_level="Intermediate",
        goals="Maintain consistent training schedule",
    )
    db_session.add(client_record)
    db_session.commit()

    response = client.put(
        f"/api/clients/{client_record.id}",
        json={"fitness_level": "Expert"},
        headers=headers,
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid fitness level"


def test_update_client_invalid_name_returns_400(client, create_user, auth_headers, db_session):
    trainer = create_user("trainer.update.name@example.com", "trainer", full_name="Trainer")
    headers = auth_headers(trainer)

    client_record = Client(
        trainer_id=trainer.id,
        name="Valid Name",
        age=27,
        fitness_level="Beginner",
        goals="Improve cardio endurance over time",
    )
    db_session.add(client_record)
    db_session.commit()

    response = client.put(
        f"/api/clients/{client_record.id}",
        json={"name": "Z"},
        headers=headers,
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Name must be 2-50 characters"
