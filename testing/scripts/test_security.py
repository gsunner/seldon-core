from seldon_e2e_utils import (
    wait_for_status,
    wait_for_rollout,
    retry_run,
    to_resources_path,
    rest_request,
)


def test_xss_escaping(namespace):
    sdep_name = "mymodel"
    sdep_path = to_resources_path("graph-echo.json")
    retry_run(f"kubectl apply -f {sdep_path} -n {namespace}")
    wait_for_status(sdep_name, namespace)
    wait_for_rollout(sdep_name, namespace)

    payload = '<div class="div-class"></div>'

    # There is a small difference between the engine and the executor, where
    # the engine will escape the `=` symbol as its unicode equivalent, so we
    # need to consider both.
    expected = [
        '\\u003cdiv class=\\"div-class\\"\\u003e\\u003c/div\\u003e',
        '\\u003cdiv class\\u003d\\"div-class\\"\\u003e\\u003c/div\\u003e',
    ]

    res = rest_request(sdep_name, namespace, data=payload, dtype="strData")

    # We need to compare raw text (instead of `.json()`). Otherwise, Python
    # interprets the escaped sequences.
    assert any([exp in res.text for exp in expected])


def test_xss_header(namespace):
    sdep_name = "mymodel"
    sdep_path = to_resources_path("graph-echo.json")
    retry_run(f"kubectl apply -f {sdep_path} -n {namespace}")
    wait_for_status(sdep_name, namespace)
    wait_for_rollout(sdep_name, namespace)

    res = rest_request(sdep_name, namespace)

    assert "X-Content-Type-Options" in res.headers
    assert res.headers["X-Content-Type-Options"] == "nosniff"