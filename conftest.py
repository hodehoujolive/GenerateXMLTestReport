from os import environ

import pytest
from selenium import webdriver
from selenium.webdriver.remote.remote_connection import RemoteConnection


@pytest.fixture(scope='function')
def driver(request):
    desired_caps = {}

    browser = {
        "platform": "Windows 10",
        "browserName": "chrome",
        "version": "latest"
    }

    username = ""
    access_key = ""

    desired_caps.update(browser)
    test_name = request.node.name
    build = environ.get('BUILD', "Generate - Test Report")
    tunnel_id = environ.get('TUNNEL', False)

    selenium_endpoint = "http://{}:{}@hub.lambdatest.com/wd/hub".format(username, access_key)
    desired_caps['build'] = build
    desired_caps['name'] = test_name
    desired_caps['video'] = True
    desired_caps['visual'] = True
    desired_caps['network'] = True
    desired_caps['console'] = True
    desired_caps['terminal'] = True
    caps = {"LT:Options": desired_caps}

    executor = RemoteConnection(selenium_endpoint)
    browser = webdriver.Remote(
        command_executor=executor,
        desired_capabilities=caps
    )
    yield browser

    def fin():
        # browser.execute_script("lambda-status=".format(str(not request.node.rep_call.failed if "passed" else
        # "failed").lower()))
        if request.node.rep_call.failed:
            browser.execute_script("lambda-status=failed")
        else:
            browser.execute_script("lambda-status=passed")
            browser.quit()

    request.addfinalizer(fin)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # this sets the result as a test attribute for LambdaTest reporting.
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)