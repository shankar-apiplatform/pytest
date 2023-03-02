from __future__ import print_function
from pytest import fixture
from _pytest._code.code import ExceptionInfo
import pytest
import requests
import os

buildId = 0


@fixture
def global_fixture():
    print("\n(Doing global fixture setup stuff!)")


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "db: Example marker for tagging Database related tests"
    )
    config.addinivalue_line(
        "markers", "slow: Example marker for tagging extremely slow tests"
    )


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):

    outcome = yield
    result = outcome.get_result()

    when = call.when
    excinfo = call.excinfo
    if not call.excinfo:
        outcome = "passed"
        longrepr = None
    else:
        if not isinstance(excinfo, ExceptionInfo):
            outcome = "failed"
            longrepr = excinfo
        elif excinfo.errisinstance(pytest.skip.Exception):
            outcome = "skipped"
            r = excinfo._getreprcrash()
            longrepr = (str(r.path), r.lineno, r.message)
        else:
            outcome = "failed"
            if call.when == "call":
                longrepr = call.excinfo.exconly()
            else: # exception in setup or teardown
                longrepr = item._repr_failure_py(excinfo,
                                            style=item.config.option.tbstyle)

    rep = {"nodeid": item.nodeid, "outcome": outcome, "exception": longrepr, "when": when, "start": call.start, "stop": call.stop}
    item.session.results.append(rep)


def pytest_sessionstart(session):

    session.results = []
    print("start")



def pytest_sessionfinish(session, exitstatus):

    url = "https://aut-services.gateway.apiplatform.io/v1/pytest-testsuite"

    buildNumber = None
    if 'BUILD_NUMBER' in os.environ:
        buildNumber = os.environ['BUILD_NUMBER']

    payload = {
        "buildNumber": buildNumber,
        "tests": session.results
    }
    headers = {"Content-Type": "application/json",
    "API-PLATFORM-PARTNER": "dev-shankar",    # account information in which the external testsuite api exists.
    "API-PLATFORM-PARTNER-KEY": "3fbccc5898ff47983f8d4a17886e3dc0"}
    params = {
        "api-name": "shankar",      # include api name and version as query params
        "api-version": "v3"
    }

    response = requests.request("POST", url, json=payload, params=params, headers=headers)

    print(response.text)
    print("end")

