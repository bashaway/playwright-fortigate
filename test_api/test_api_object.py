import time
from enum import auto
import os
from typing import Generator

import pytest
from playwright.sync_api import Playwright, Page, APIRequestContext, expect

class TestPage:

    def test_get_pages(self, api_request_context: APIRequestContext, params) -> None:
        # テストパラメータ設定
        page_title=params['page']['item_title']
        page_body=params['page']['item_body']
        page_parent=params['page']['item_parent']

        # ページを作成
        data = {
            "spaceId": "196609",
            "status": "current",
            "title": f"{page_title}",
            "parentId": f"{page_parent}",
            "body": {
                "representation": "storage",
                "value": f"{page_body}"
            }
        }
        new_page = api_request_context.post(f"/wiki/api/v2/pages", data=data)
        assert new_page.ok
    
        # ページが存在することを確認
        query_params = {"title": f"{page_title}"}
        page = api_request_context.get(f"/wiki/api/v2/pages", params=query_params)
        assert page.ok
        got_page_id = (page.json())["results"][0]["id"]

        # ページ本文が作成したものと同じであることを確認
        query_params = {"body-format": "storage"}
        page = api_request_context.get(f"/wiki/api/v2/pages/{got_page_id}", params=query_params)
        assert page.ok
        got_page_body = (page.json())["body"]["storage"]["value"]
        assert got_page_body == page_body

        # ページをゴミ箱に移動
        page = api_request_context.delete(f"/wiki/api/v2/pages/{got_page_id}")
        assert page.ok

        # ゴミ箱のページを完全に削除
        query_params = {"purge": "true"}
        page = api_request_context.delete(f"/wiki/api/v2/pages/{got_page_id}", params=query_params)
        assert page.ok

        # ページが存在しないことを確認
        query_params = {"title": f"{page_title}"}
        page = api_request_context.get(f"/wiki/api/v2/pages", params=query_params)
        assert page.ok
        got_results = (page.json())["results"]
        assert len(got_results) == 0

