# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from unittest.mock import patch

import flask_testing


class TestSubber(flask_testing.TestCase):

    @patch('subber.config.get_config')
    @patch('subber.reddit.Reddit')
    def create_app(self, mock_session, mock_config):
        # Mock session return value
        redditor = {'name': 'u/test',
                    'created': 2545896143}
        mock_session.return_value.redditor.return_value = redditor

        from subber import subber

        return subber.app

    def test_get_form(self):
        self.client.get('/')
        self.assert_template_used('form.html')

    @patch('subber.reddit.get_user_recommendations')
    @patch('subber.subber.session')
    def test_get_sub_recommendations(self,
                                     mock_session,
                                     mock_recommendations):
        # Mock sub recommendations
        mock_recommendations.return_value = [{'name': 'r/test',
                                              'title': 'sub',
                                              'age': 3,
                                              'subscribers': 8692,
                                              'over18': False,
                                              'desc': 'a desc'}]

        # Submit username
        form_data = {'username': 'test_username'}
        test_result = self.client.post('/user', data=form_data)

        mock_recommendations.assert_called_with(mock_session,
                                                form_data['username'])
        self.assert_template_used('results.html')

        for sub in mock_recommendations():
            assert sub['name'].encode('utf-8') in test_result.data
            assert sub['title'].encode('utf-8') in test_result.data

            assert 'Community for {} years'.format(
                    sub['age']).encode('utf-8') in test_result.data

            assert '{:,} subscribers'.format(
                    sub['subscribers']).encode('utf-8') in test_result.data

            assert 'Over 18 community'.encode('utf-8') not in test_result.data
            assert sub['desc'].encode('utf-8') in test_result.data

    @patch('subber.reddit.get_user_recommendations')
    @patch('subber.subber.session')
    def test_get_sub_recommendations_less_than_one_year(self,
                                                        mock_session,
                                                        mock_recommendations):
        # Mock sub recommendations
        mock_recommendations.return_value = [{'name': 'r/test',
                                              'title': 'sub',
                                              'age': 0,
                                              'subscribers': 8692,
                                              'over18': False,
                                              'desc': 'a desc'}]

        # Submit username
        form_data = {'username': 'test_username'}
        test_result = self.client.post('/user', data=form_data)

        mock_recommendations.assert_called_with(mock_session,
                                                form_data['username'])
        self.assert_template_used('results.html')

        for sub in mock_recommendations():
            assert sub['name'].encode('utf-8') in test_result.data
            assert sub['title'].encode('utf-8') in test_result.data

            assert 'Community for less than one year'.encode(
                   'utf-8') in test_result.data

            assert '{:,} subscribers'.format(
                    sub['subscribers']).encode('utf-8') in test_result.data

            assert 'Over 18 community'.encode('utf-8') not in test_result.data
            assert sub['desc'].encode('utf-8') in test_result.data

    @patch('subber.reddit.get_user_recommendations')
    @patch('subber.subber.session')
    def test_get_sub_recommendations_over_18(self,
                                             mock_session,
                                             mock_recommendations):
        # Mock sub recommendations
        mock_recommendations.return_value = [{'name': 'r/test',
                                              'title': 'sub',
                                              'age': 3,
                                              'subscribers': 8692,
                                              'over18': True,
                                              'desc': 'a desc'}]

        # Submit username
        form_data = {'username': 'test_username'}
        test_result = self.client.post('/user', data=form_data)

        mock_recommendations.assert_called_with(mock_session,
                                                form_data['username'])
        self.assert_template_used('results.html')

        for sub in mock_recommendations():
            assert sub['name'].encode('utf-8') in test_result.data
            assert sub['title'].encode('utf-8') in test_result.data

            assert 'Community for {} years'.format(
                    sub['age']).encode('utf-8') in test_result.data

            assert '{:,} subscribers'.format(
                    sub['subscribers']).encode('utf-8') in test_result.data

            assert 'Over 18 community'.encode('utf-8') in test_result.data
            assert sub['desc'].encode('utf-8') in test_result.data


if __name__ == '__main__':
    unittest.main()
