import pytest, configparser, keyring, getpass
from typing import Generator
from playwright.sync_api import Playwright, APIRequestContext

params = configparser.ConfigParser()
params.read('params.ini', encoding='utf-8')

# サイトのログイン情報のキー
KEYRING_SERVICE = params['DEFAULT']['keyring_service_api']
KEYRING_USER = params['DEFAULT']['keyring_user_api']

"""
削除するには
python -c "import keyring; keyring.delete_password('bashaway.atlassian.net', 'CF_SERVICE_ACCOUNT_RW_BASE64')"
"""

def get_login_info():
    # keyringからログイン情報を取得
    KEYRING_PASS = keyring.get_password(KEYRING_SERVICE,KEYRING_USER)
    if not KEYRING_PASS:
        KEYRING_PASS = getpass.getpass("Enter '"+KEYRING_USER+"' token: ")
        # ログイン情報をkeyringに保存
        keyring.set_password(KEYRING_SERVICE, KEYRING_USER, KEYRING_PASS)
    return KEYRING_PASS

@pytest.fixture(scope="session")
def api_request_context(
    playwright: Playwright,
) -> Generator[APIRequestContext, None, None]:

    # ログイン情報を取得
    KEYRING_PASS = get_login_info()

    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {KEYRING_PASS}",
    }
    request_context = playwright.request.new_context(
        base_url="https://bashaway.atlassian.net", extra_http_headers=headers
    )
    yield request_context
    request_context.dispose()

# autouse=Trueなので、どのfunctionが実行されても、自動的に実行される（ただしscope=sessionなので最初の１回だけ）
#@pytest.fixture(scope="session", autouse=True)
#def create_test_repository(
#    api_request_context: APIRequestContext,
#) -> Generator[None, None, None]:
#    # Before all
#    new_repo = api_request_context.post("/user/repos", data={"name": GITHUB_REPO})
#    assert new_repo.ok
#    yield
#    # After all
#    deleted_repo = api_request_context.delete(f"/repos/{GITHUB_USER}/{GITHUB_REPO}")
#    assert deleted_repo.ok

@pytest.fixture(scope="function")
def params():
    params = configparser.ConfigParser()
    params.read('params.ini', encoding='utf-8')
    yield params

