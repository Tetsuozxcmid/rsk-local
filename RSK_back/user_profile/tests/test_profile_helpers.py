import pytest

from cruds.profile_crud import ProfileCRUD
from db.models.user_enum import UserEnum


def test_normalize_text_strips():
    assert ProfileCRUD._normalize_text("  x  ") == "x"
    assert ProfileCRUD._normalize_text(None) == ""


def test_split_full_name_three_parts():
    f, l, p = ProfileCRUD._split_full_name("Иван Сергеевич Петров")
    assert f == "Иван"
    assert l == "Сергеевич"
    assert p == "Петров"


def test_split_full_name_short_returns_empty_triple():
    assert ProfileCRUD._split_full_name("Один") == ("", "", "")


def test_resolve_role_student_and_teacher():
    assert ProfileCRUD._resolve_role("student") == UserEnum.Student
    assert ProfileCRUD._resolve_role("TEACHER") == UserEnum.Teacher


def test_resolve_role_unknown_defaults_student():
    assert ProfileCRUD._resolve_role("not-a-real-role") == UserEnum.Student


def test_should_replace_username_when_empty_current():
    assert ProfileCRUD._should_replace_username(None, "new", "vk") is True


def test_should_replace_username_same_incoming_false():
    assert ProfileCRUD._should_replace_username("nick", "nick", "vk") is False
