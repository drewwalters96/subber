import unittest
from unittest.mock import Mock, patch

from subber import reddit


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
               'desc': 'desc'}

        mock_sub_info.return_value = sub

        # Test results
        user_param = 'user'
        expected_result = [sub for u in similar_users for s in active_subs]

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
        parent_comment_authors = ['comment_author1', 'comment_author2',
                                  'comment_author3', 'comment_author4']

        comments = []
        for author in parent_comment_authors:
            comment_author_obj = Mock()
            comment_author_obj.author.name = author

            comment = Mock()
            comment.parent.return_value = comment_author_obj

            comments.append(comment)

        mock_comments.return_value = comments

        # Mock submissions
        submission_comment_authors = ['submission_comment_author1',
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
        expected_result = (parent_comment_authors) + \
                          (submission_comment_authors[:4]) + \
                          (submission_comment_authors[6:])

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
    def test_get_sub_info(self, mock_session):
        # Mock subreddit instance
        subreddit = Mock(display_name_prefixed='r/subreddit',
                         title='Title',
                         public_description_html='<p>Description.</p>')

        mock_session.subreddit.return_value = subreddit

        # Test results
        expected_result = {'name': subreddit.display_name_prefixed,
                           'title': subreddit.title,
                           'desc': subreddit.public_description_html}

        sub_param = 'subreddit'
        self.assertEqual(reddit.get_sub_info(mock_session, sub_param),
                         expected_result)

        mock_session.subreddit.assert_called_with(sub_param)


if __name__ == '__main__':
    unittest.main()
