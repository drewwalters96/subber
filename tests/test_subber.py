import unittest
from unittest.mock import patch

import flask_testing


class TestSubber(flask_testing.TestCase):

    @patch('subber.reddit.Reddit')
    def create_app(self, mock_session):
        # Mock API session on module import
        mock_session.return_value.get_session.return_value = None
        from subber import subber

        return subber.app

    def test_get_form(self):
        self.client.get('/')
        self.assert_template_used('form.html')

    @patch('subber.reddit.get_user_recommendations')
    def test_get_sub_recommendations(self, mock_recommendations):
        # Mock sub recommendations
        mock_recommendations.return_value = [{'name': 'r/test',
                                              'title': 'sub',
                                              'desc': 'a desc'}]

        # Submit username
        form_data = {'username': 'test_username'}
        test_result = self.client.post('/user', data=form_data)

        mock_recommendations.assert_called_with(None, form_data['username'])
        self.assert_template_used('results.html')

        for sub in mock_recommendations():
            assert sub['name'].encode('utf-8') in test_result.data
            assert sub['title'].encode('utf-8') in test_result.data
            assert sub['desc'].encode('utf-8') in test_result.data


if __name__ == '__main__':
    unittest.main()
