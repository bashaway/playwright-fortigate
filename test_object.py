import inspect
import time
import pytest
from playwright.sync_api import sync_playwright, Page, expect

class TestObject:
    # 状態確認
    def check_state(self, authenticated_page, item_name, count, ss_name):
        authenticated_page.get_by_placeholder("検索").fill(item_name)
        authenticated_page.locator("nu-mutable-search").get_by_role("button").click()
        # 結果が表示しきるまえにカウントチェックされると「表示されなくてゼロ」なのか「結果がゼロ件」か判別できない
        time.sleep(1)
        expect(authenticated_page.locator("span").get_by_text(item_name, exact=True)).to_have_count(count)
        authenticated_page.screenshot(path=ss_name, full_page=True)

    # テスト
    def test_object_addresses(self, authenticated_page, params):
        # テストパラメータ設定
        test_target = ((inspect.currentframe().f_code.co_name).replace('test_',''))
        ss_base=params['DEFAULT']['ss_directory']+'/'+test_target

        # テスト対象のURLへ移動
        authenticated_page.goto(params[test_target]['test_url'])
        # 存在しないことを確認
        self.check_state(authenticated_page, params[test_target]['item_name'], 0, ss_base+"_01.png")

        # 作成する
        authenticated_page.get_by_label("新規作成").click()
        authenticated_page.locator("f-field").filter(has_text="名前").get_by_role("textbox").fill(params[test_target]['item_name'])
        authenticated_page.get_by_placeholder("コメント記入…").fill(params[test_target]['item_desc'])
        authenticated_page.locator("f-field").filter(has_text="IP/ネットマスク").get_by_role("textbox").fill(params[test_target]['item_value'])
        authenticated_page.screenshot(path=ss_base+"_02.png", full_page=True)
        authenticated_page.get_by_role("button", name="OK").click()
        # 存在することを確認
        self.check_state(authenticated_page, params[test_target]['item_name'], 1, ss_base+"_03.png")

        # 削除する
        authenticated_page.locator("span").get_by_text(params[test_target]['item_name'], exact=True).click()
        authenticated_page.get_by_label("削除").click()
        authenticated_page.screenshot(path=ss_base+"_04.png", full_page=True)
        authenticated_page.get_by_label("OK").click()
        # 存在しないことを確認
        self.check_state(authenticated_page, params[test_target]['item_name'], 0, ss_base+"_05.png")


    def test_object_services(self, authenticated_page, params):
        # テストパラメータ設定
        test_target = ((inspect.currentframe().f_code.co_name).replace('test_',''))
        ss_base=params['DEFAULT']['ss_directory']+'/'+test_target

        # テスト対象のURLへ移動
        authenticated_page.goto(params[test_target]['test_url'])
        # 存在しないことを確認
        self.check_state(authenticated_page, params[test_target]['item_name'], 0, ss_base+"_01.png")

        # 作成する
        authenticated_page.get_by_label("新規作成").click()
        authenticated_page.get_by_label("名前").fill(params[test_target]['item_name'])
        authenticated_page.get_by_placeholder("コメント記入…").fill(params[test_target]['item_desc'])
        authenticated_page.get_by_placeholder("Low").fill(params[test_target]['item_value'])
        authenticated_page.screenshot(path=ss_base+"_02.png", full_page=True)
        authenticated_page.get_by_role("button", name="OK").click()
        # 存在することを確認
        self.check_state(authenticated_page, params[test_target]['item_name'], 1, ss_base+test_target+"_03.png")

        # 削除する
        authenticated_page.locator("span").get_by_text(params[test_target]['item_name'], exact=True).click()
        authenticated_page.get_by_label("削除").click()
        authenticated_page.screenshot(path=ss_base+"_04.png", full_page=True)
        authenticated_page.get_by_label("OK").click()
        # 存在しないことを確認
        self.check_state(authenticated_page, params[test_target]['item_name'], 0, ss_base+"_05.png")

