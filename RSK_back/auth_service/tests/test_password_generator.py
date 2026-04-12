import string

from services.password_generator import generate_random_password


def test_generate_random_password_length_and_charset():
    for length in (8, 12, 24):
        pwd = generate_random_password(length)
        assert len(pwd) == length
    long_pwd = generate_random_password(200)
    allowed = set(string.ascii_letters + string.digits + "!@#$%^&*")
    assert set(long_pwd) <= allowed
