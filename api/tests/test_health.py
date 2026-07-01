def test_health_ok(client, tmp_claude):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert "claude_dir" not in body
