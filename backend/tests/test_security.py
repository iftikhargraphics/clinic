from app.security import hash_password, verify_password

def test_password_hash_verifies():
    encoded=hash_password("a-long-demo-password")
    assert encoded != "a-long-demo-password"
    assert verify_password("a-long-demo-password",encoded)
    assert not verify_password("wrong-password",encoded)
