def test_openapi_contract_exposes_frontend_session_fields(client):
    schema = client.get("/openapi.json").json()["components"]["schemas"]

    assert "focus" in schema["ProgramRead"]["properties"]
    assert "is_session_snapshot" in schema["ProgramRead"]["properties"]
    assert "program_exercise_id" in schema["CompleteSetRequest"]["properties"]
    assert "program_exercise_id" in schema["WorkoutLogRead"]["properties"]
    assert "clients" in schema["TrainingSessionRead"]["properties"]
    assert "clients" in schema["SessionSummaryRead"]["properties"]
    assert "today_check_in" in schema["ClientDetailRead"]["properties"]
    assert "today_readiness" in schema["DashboardOverview"]["properties"]
    assert "TrainingGroupRead" in schema
    assert "clients" in schema["TrainingGroupRead"]["properties"]
    assert "exercises" in schema["TrainingGroupRead"]["properties"]
