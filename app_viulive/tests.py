from django.test import TestCase
from django.test import override_settings
from .models import Channel


class ChannelDatabaseTests(TestCase):
    def setUp(self):
        Channel.objects.create(
            id="test-news",
            name="Test News",
            logo="https://example.com/logo.png",
            country="Kenya",
            group_title="News",
            urls={
                "url": "https://example.com/live.m3u8",
                "url-2": "https://example.com/backup.m3u8",
            },
        )

    def test_channel_list_uses_database_and_hides_stream_urls(self):
        response = self.client.get("/api/viulive/channels/")

        self.assertEqual(response.status_code, 200)
        channel = response.json()["data"]["channels"][0]
        self.assertEqual(channel["id"], "test-news")
        self.assertEqual(channel["url_count"], 2)
        self.assertNotIn("url", channel)
        self.assertNotIn("url-2", channel)

    def test_search_and_groups_use_database(self):
        search_response = self.client.get(
            "/api/viulive/channels/search/", {"q": "Test News"}
        )
        groups_response = self.client.get("/api/viulive/channels/groups/")

        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(
            search_response.json()["data"]["channels"][0]["id"], "test-news"
        )
        self.assertEqual(groups_response.json()["data"]["groups"], ["News"])

    @override_settings(DEBUG=True)
    def test_player_page_and_stream_url_use_database(self):
        player_response = self.client.get("/viulive/watching/test-news/")
        stream_response = self.client.get(
            "/api/viulive/channel/test-news/url/", {"stream": 2}
        )

        self.assertEqual(player_response.status_code, 200)
        self.assertEqual(
            stream_response.json()["data"]["channel"]["url"],
            "https://example.com/backup.m3u8",
        )
