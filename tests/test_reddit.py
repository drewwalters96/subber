import unittest

from unittest import mock
from subber import reddit


class TestReddit(unittest.TestCase):
    """Unit tests for the Reddit module"""
    @mock.patch('subber.reddit._get_similar_users')
    @mock.patch('subber.reddit._get_active_subs')
    def test_get_user_recommendations(self, mock_active_subs,
                                      mock_similar_users):
        # Mock similar users
        similar_users = ['similar_user1', 'similar_user2', 'similar_user3']
        mock_similar_users.return_value = similar_users

        # Mock active subs
        active_subs = ['active_sub1', 'active_sub2', 'active_sub3',
                       'active_sub4']
        mock_active_subs.return_value = active_subs

        # Test results
        user_param = 'user'

        expected_result = active_subs
        self.assertEqual(reddit.get_user_recommendations(None,
                                                         user_param),
                         expected_result)

        mock_similar_users.assert_called_with(None, user_param)
        mock_active_subs.assert_called_with(None, similar_users[-1])

    @mock.patch('subber.reddit._get_user_comments')
    @mock.patch('subber.reddit._get_user_submissions')
    def test_get_similar_users(self, mock_submissions, mock_comments):
        # Mock parent_comments
        parent_comment_authors = ['comment_author1', 'comment_author2',
                                  'comment_author3', 'comment_author4']

        comments = []
        for author in parent_comment_authors:
            comment_author_obj = mock.Mock()
            comment_author_obj.author.name = author

            comment = mock.Mock()
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
            comment_author_obj = mock.Mock()
            comment_author_obj.author.name = author

            submission_comments.append(comment_author_obj)

        submission_1 = mock.Mock()
        submission_1.comments = submission_comments[:5]

        submission_2 = mock.Mock()
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

    @mock.patch('subber.reddit._get_user_comments')
    @mock.patch('subber.reddit._get_user_submissions')
    def test_get_active_subs(self, mock_submissions, mock_comments):
        def mock_post_sub_names(mock_data):
            """Mocks the subreddit name of a submission or commment object"""
            posts = []
            for sub in mock_data:
                post = mock.Mock(subreddit_name_prefixed=sub)
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

    @mock.patch('praw.Reddit')
    def test_get_sub_info(self, mock_session):
        # Mock subreddit instance
        subreddit = mock.Mock(name='r/subreddit', title='Title',
                              description='Description of the subreddit.')

        mock_session.subreddit.return_value = subreddit

        # Test results
        expected_result = {'sub': {'name': 'r/subreddit',
                                   'title': 'Title',
                                   'desc': 'Description of the subreddit.'}}

        sub_param = 'subreddit'
        self.assertEqual(reddit.get_sub_info(mock_session, sub_param),
                         expected_result)

        mock_session.subreddit.assert_called_with(sub_param)


if __name__ == '__main__':
    unittest.main()
