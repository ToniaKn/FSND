import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr.app import create_app
from models import setup_db, Category, Question


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "test_trivia"
        self.database_path = "postgres://{}:{}@{}/{}".format('user', 'pass', 'localhost:5432',
                                                             self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'xxxxxxxxxxxx',
            'answer': 'xxxxxxxxxxxxx',
            'difficulty': 5,
            'category': 1}

        self.searchTerm = {'searchTerm': 'xxxx'}

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_categories(self):
        category = Category(type='Science')
        category.insert()

        res = self.client().get('/categories')

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        category.delete()

    def test_get_questions(self):
        question = Question(**self.new_question)
        question.insert()

        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

        question.delete()

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_questions(self):
        question = Question(**self.new_question)
        question.insert()
        question_id = question.id

        res = self.client().delete('/questions/' + str(question_id))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)
        self.assertEqual(data['deleted'], question_id)


    def test_404_if_question_does_not_exist(self):
        res = self.client().delete('/questions/50000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_post_question(self):
        res = self.client().post('/question', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

        question = Question.query.filter(Question.id == data['created']).one_or_none()
        question.delete()

    def test_404_if_question_creation_not_allowed(self):

        res = self.client().post('/question/4', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_search_question(self):
        question = Question(**self.new_question)
        question.insert()

        res = self.client().post('/questions', json=self.searchTerm)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

        question.delete()

    def test_get_category_questions(self):
        question = Question(**self.new_question)
        question.insert()
        question_category = question.category

        res = self.client().get('/categories/' + str(question_category) + '/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

        question.delete()

    def test_get_category_questions_when_empty(self):
        question = Question(**self.new_question)
        question.insert()
        question_category = 1000

        res = self.client().get('/categories/' + str(question_category) + '/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['questions'], [])
        self.assertEqual(data['total_questions'], 0)

        question.delete()

    def test_play_quiz(self):
        question = Question(**self.new_question)
        question.insert()
        category_id = question.category

        res = self.client().post('/quizzes', json={'quiz_category': {'id': category_id, 'type': 'science'},
                                                   'previous_questions': []})

        data = json.loads(res.data)
        self.assertTrue(data['question'])

        question.delete()

    def test_play_quiz_when_all_questions_are_answered(self):
        question = Question(**self.new_question)
        question.insert()
        category_id = question.category
        question_id = question.id

        res = self.client().post('/quizzes', json={'quiz_category': {'id': category_id, 'type': 'science'},
                                                   'previous_questions': [question_id]})

        data = json.loads(res.data)
        self.assertEqual(data['question'], None)

        question.delete()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
