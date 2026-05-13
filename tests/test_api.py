OK = 200
CREATED = 201
DELETED = 204
NOT_FOUND = 404


def test_get_user_404(client) -> None:

    # Teste de Recuperação
    get_response = client.get(f"/courses/00000000-0000-0000-0000-000000000000")
    assert get_response.status_code == NOT_FOUND  # noqa: S101


def test_create_and_get_course_and_delete_course(client) -> None:
    new_course = {"name": "course", "code": "course_code"}
    post_response = client.post("/courses", json=new_course)
    assert post_response.status_code == CREATED  # noqa: S101
    course_id = post_response.get_json()["id"]

    get_response = client.get(f"/courses/{course_id}")
    assert get_response.status_code == OK  # noqa: S101

    delete_response = client.delete(f"/courses/{course_id}")
    assert delete_response.status_code == DELETED  # noqa: S101


def test_create_and_delete_course(client) -> None:
    new_course = {"name": "course", "code": "course_code"}
    post_response = client.post("/courses", json=new_course)
    assert post_response.status_code == CREATED  # noqa: S101
    course_id = post_response.get_json()["id"]

    delete_response = client.delete(f"/courses/{course_id}")
    assert delete_response.status_code == DELETED  # noqa: S101


def test_create_two_courses_and_list_and_delete_both_courses(
    client,
) -> None:
    new_course_1 = {"name": "course_1", "code": "course_1_code"}
    post_response = client.post("/courses", json=new_course_1)
    assert post_response.status_code == CREATED  # noqa: S101
    course_1_id = post_response.get_json()["id"]

    new_course_2 = {"name": "course_2", "code": "course_2_code"}
    post_response = client.post("/courses", json=new_course_2)
    assert post_response.status_code == CREATED  # noqa: S101
    course_2_id = post_response.get_json()["id"]

    get_response = client.get("/courses")
    assert get_response.status_code == OK  # noqa: S101
    assert isinstance(get_response.json, list)  # noqa: S101
    assert len(get_response.json) == 2  # noqa: PLR2004, S101

    delete_response = client.delete(f"/courses/{course_1_id}")
    assert delete_response.status_code == DELETED  # noqa: S101
    delete_response = client.delete(f"/courses/{course_2_id}")
    assert delete_response.status_code == DELETED  # noqa: S101
