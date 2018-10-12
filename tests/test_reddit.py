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

from datetime import datetime
from datetime import timedelta
import unittest
from unittest.mock import Mock, patch

from subber import reddit
from subber import util

class TestReddit(unittest.TestCase):
    @patch('subber.reddit._get_similar_users')
    @patch('subber.reddit._get_active_subs')
    @patch('subber.reddit.get_sub_info')
    def test_get_user_recommendations(self, mock_sub_info, mock_active_subs,
                                      mock_similar_users):
        # Mock similar users
        similar_users = ['similar_user1', 'similar_user2', 'similar_user3']
        mock_similar_users.return_value = similar_users

        # Mock active subs
        active_subs = ['r/active_sub1', 'r/active_sub2', 'r/active_sub3',
                       'r/active_sub4']
        mock_active_subs.return_value = active_subs

        # Mock sub info
        sub = {'name': 'sub',
               'title': 'title',
               'age': 3,
               'subscribers': 8692,
               'over18': False,
               'desc': 'desc'}

        mock_sub_info.return_value = sub

        # Test results
        user_param = 'user'
        expected_result = [sub]

        self.assertEqual(reddit.get_user_recommendations(None,
                                                         user_param),
                         expected_result)

        mock_similar_users.assert_called_with(None, user_param)
        mock_active_subs.assert_called_with(None, similar_users[-1])
        mock_sub_info.assert_called_with(None, active_subs[-1][2:])

    @patch('subber.reddit._get_user_comments')
    @patch('subber.reddit._get_user_submissions')
    def test_get_similar_users(self, mock_submissions, mock_comments):
        # Mock parent_comments
        parent_comment_authors = ['user', 'comment_author2',
                                  'comment_author3', 'comment_author4',
                                  'comment_author5', 'comment_author6']

        comments = []
        for author in parent_comment_authors:
            comment_author_obj = Mock()
            comment_author_obj.author.name = author

            comment = Mock()
            comment.parent.return_value = comment_author_obj

            comments.append(comment)

        mock_comments.return_value = comments

        # Mock submissions
        submission_comment_authors = ['user',
                                      'submission_comment_author2',
                                      'submission_comment_author3',
                                      'submission_comment_author4',
                                      'submission_comment_author5',
                                      'submission_comment_author6',
                                      'submission_comment_author7',
                                      'submission_comment_author8']

        submission_comments = []
        for author in submission_comment_authors:
            comment_author_obj = Mock()
            comment_author_obj.author.name = author

            submission_comments.append(comment_author_obj)

        submission_1 = Mock()
        submission_1.comments = submission_comments[:5]

        submission_2 = Mock()
        submission_2.comments = submission_comments[6:]

        mock_submissions.return_value = [submission_1, submission_2]

        # Test results
        expected_result = (parent_comment_authors[1:]) + \
                          (submission_comment_authors[6:7])

        user_param = 'user'
        self.assertEqual(reddit._get_similar_users(None, user_param),
                         expected_result)

        mock_comments.assert_called_with(None, user_param)
        mock_submissions.assert_called_with(None, user_param)

    @patch('subber.reddit._get_user_comments')
    @patch('subber.reddit._get_user_submissions')
    def test_get_active_subs(self, mock_submissions, mock_comments):
        def mock_post_sub_names(mock_data):
            """Mocks the subreddit name of a submission or commment object"""
            posts = []
            for sub in mock_data:
                post = Mock(subreddit_name_prefixed=sub)
                posts.append(post)

            return posts

        # Mock comments
        comment_subs = ['r/sub', 'r/subreddit']
        mock_comments.return_value = mock_post_sub_names(comment_subs)

        # Mock submissions
        submission_subs = ['r/sub', 'r/AskReddit']
        mock_submissions.return_value = mock_post_sub_names(submission_subs)

        expected_result = comment_subs + submission_subs

        # Test results
        user_param = 'user'
        self.assertEqual(reddit._get_active_subs(None, user_param),
                         expected_result)

        mock_comments.assert_called_with(None, user_param)
        mock_submissions.assert_called_with(None, user_param)

    @patch('praw.Reddit')
    @patch('subber.util.utc_epoch_sec_to_years')
    def test_get_sub_info(self, mock_years, mock_session):
        # Mock epoch conversion
        mock_years.return_value = 3

        # Mock subreddit instance
        subreddit = Mock(display_name_prefixed='r/subreddit',
                         title='Title',
                         created=892349754,
                         subscribers=8962,
                         over18=False,
                         public_description='Description')

        mock_session.subreddit.return_value = subreddit

        # Test results
        expected_result = {'name': subreddit.display_name_prefixed,
                           'title': subreddit.title,
                           'age': 3,
                           'subscribers': subreddit.subscribers,
                           'over18': subreddit.over18,
                           'desc': subreddit.public_description}

        sub_param = 'subreddit'
        self.assertEqual(reddit.get_sub_info(mock_session, sub_param),
                         expected_result)

        mock_years.assert_called_with(subreddit.created)
        mock_session.subreddit.assert_called_with(sub_param)


    def test_util_utc_epoch_sec_to_years(self):
        def unix_time_seconds(time):
            epoch = datetime.utcfromtimestamp(0)
            return (time - epoch).total_seconds()

        def unix_time_years(time):
            epoch = datetime.utcfromtimestamp(0)
            return int((time - epoch).total_seconds() / (60*60*24*365))

        time_now = unix_time_seconds(datetime.utcnow())
        one_year = time_now - timedelta(days=365).total_seconds()
        five_years = time_now - (timedelta(days=365).total_seconds() * 5)

        years_epoch = unix_time_years(datetime.utcnow())

        self.assertEqual(util.utc_epoch_sec_to_years(time_now), 0)
        self.assertEqual(util.utc_epoch_sec_to_years(one_year), 1)
        self.assertEqual(util.utc_epoch_sec_to_years(five_years), 5)

        self.assertEqual(util.utc_epoch_sec_to_years('time'), -1)
        self.assertEqual(util.utc_epoch_sec_to_years(0), years_epoch)
        self.assertEqual(util.utc_epoch_sec_to_years(True), years_epoch)


if __name__ == '__main__':
    unittest.main()
