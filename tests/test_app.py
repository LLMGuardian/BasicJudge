import unittest
from unittest.mock import Mock, patch

from flask import json

from src.app import app


class ProcessRequestTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("requests.post")
    def test_successful_request(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "69"}
        mock_post.return_value = mock_response

        data = {
            "prompt": "What is the sky color?",
            "chat": "The previous chat context.",
        }

        response = self.app.post(
            "/process", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": True})

    @patch("requests.post")
    def test_successful_request_malicious(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "1"}
        mock_post.return_value = mock_response

        data = {
            "prompt": "What is the sky color?",
            "chat": "The previous chat context.",
        }

        response = self.app.post(
            "/process", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": False})

    @patch("requests.post")
    def test_missing_response_field(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        data = {
            "prompt": "What is the sky color?",
            "chat": "The previous chat context.",
        }

        response = self.app.post(
            "/process", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json,
            {
                "error": "Internal server error. Missing 'response' field in external API response"
            },
        )

    @patch("requests.post")
    def test_no_number_in_response(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Invalid response text"}
        mock_post.return_value = mock_response

        data = {
            "prompt": "What is the sky color?",
            "chat": "The previous chat context.",
        }

        response = self.app.post(
            "/process", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json,
            {
                "error": "Internal server error. No number in the range [0, 100] found in response"
            },
        )

    @patch("requests.post")
    def test_invalid_number_in_response(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "-1"}
        mock_post.return_value = mock_response

        data = {
            "prompt": "What is the sky color?",
            "chat": "The previous chat context.",
        }

        response = self.app.post(
            "/process", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json,
            {
                "error": "Internal server error. No number in the range [0, 100] found in response"
            },
        )

    def test_invalid_input(self):
        data = {"chat": "The previous chat context."}

        response = self.app.post(
            "/process", data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json, {"error": "Invalid input, 'prompt' and 'chat' are required"}
        )


if __name__ == "__main__":
    unittest.main()
