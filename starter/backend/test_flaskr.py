import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path ="postgresql://{}:{}@{}/{}".format('postgres', 'postgres','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'new_question':'Who is the current president of U.S.A',
            'new_answer':'Donald Trump',
            'new_category': 4,
            'new_dificulty':'2'
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])

    def test_404_get_questions_error(self):
        response = self.client().get('/questions?page=150')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not found')

    def test_post_new_question(self):
        response = self.client().post('/questions/new', 
            json=self.new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created_question'])
        self.assertTrue(data['questions'])
    
    def test_422_new_question_error(self):
        response = self.client().post('/questions/new',
            json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Request')
    
    def test_delete_question(self):
        response = self.client().delete('/questions/2')
        data = json.loads(response.data)

        question_test = Question.query.filter(Question.id==2).one_or_none()

        print(question_test)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 2)
        self.assertTrue(data['questions'])
        self.assertEqual(question_test, None)
    
    def test_422_if_question_does_not_exist(self):
        response = self.client().delete('/questions/150')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Request')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()