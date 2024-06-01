import pytest, configparser, keyring, getpass
from playwright.sync_api import sync_playwright, Page, expect

params = configparser.ConfigParser()
params.read('params.ini', encoding='utf-8')

# サイトのログイン情報のキー
KEYRING_SERVICE = params['DEFAULT']['keyring_service']
KEYRING_USER = params['DEFAULT']['keyring_user']

"""
削除するには
python -c "import keyring; keyring.delete_password('fwhq01.prosper2.net', 'admin')"
"""

def get_login_info():
    # keyringからログイン情報を取得
    KEYRING_PASS = keyring.get_password(KEYRING_SERVICE,KEYRING_USER)
    if not KEYRING_PASS:
        KEYRING_PASS = getpass.getpass("Enter '"+KEYRING_USER+"' password: ")
        # ログイン情報をkeyringに保存
        keyring.set_password(KEYRING_SERVICE, KEYRING_USER, KEYRING_PASS)
    return KEYRING_PASS


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        #browser = p.chromium.launch(headless=False)
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture(scope="session")
def context(browser):
    context = browser.new_context(viewport={"width": 1024, "height": 768}, ignore_https_errors=True)

    # トレースしながらテスト実行
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context
    context.tracing.stop(path="trace.zip")

    context.close()

@pytest.fixture(scope="session")
def page(context):
    page = context.new_page()
    yield page
    page.close()

@pytest.fixture(scope="session")
def login(page):
    # ログイン情報を取得
    KEYRING_PASS = get_login_info()

    # ログイン処理を実行する
    # ここでは例として、ユーザー名とパスワードを入力してログインすると仮定します
    page.goto("https://fwhq01.prosper2.net/login?redir=%2F")
    page.get_by_placeholder("ユーザ名").fill(KEYRING_USER)
    page.get_by_placeholder("パスワード").fill(KEYRING_PASS)
    page.get_by_role("button", name="ログイン").click()

    # ログインできたことを確認したい
    #print("\n# Login succeeded\n")

    # ログイン後、Cookieを取得して返す
    return page.context.cookies()

@pytest.fixture(scope="session")
def authenticated_page(context, login):
    # ログインCookieをセットする
    context.add_cookies(login)

    # 認証済みのページを返す
    page = context.new_page()
    yield page

    # テストが終了したらログアウト処理を実行する
    page.get_by_label("admin").click()
    page.get_by_label("ログアウト").click()


@pytest.fixture(scope="function")
def params():
    params = configparser.ConfigParser()
    params.read('params.ini', encoding='utf-8')
    yield params

