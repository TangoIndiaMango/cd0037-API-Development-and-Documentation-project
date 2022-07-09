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
        self.database_path = "postgres://{}:{}@{}/{}".format(
            'postgres', '1000', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "Who was the first president of Kenya?",
            "category": 4,
            "answer": "President Kenyatta",
            "difficulty": 1
        }
        self.quiz_422 = {
            "quiz_category": {},
            "previous_questions": {}
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    
    
    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # def test_retrieve_categories(self):
    #     res = self.client().get('/categories')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertTrue(data["categories"])
    #     self.assertTrue(len(data["Total categories"]))
    

    # def test_retrieve_questions(self):
    #     res = self.client().get("/questions")
    #     data = json.loads(res.data)
        
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertTrue(data["categories"])
    #     self.assertTrue(data["questions"])
    #     self.assertTrue(data["total_questions"])

    # def test_retrieve_questions_pagination(self):
    #     res = self.client().get('/questions?page=2')
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
    #     self.assertTrue(data["categories"])
    #     self.assertTrue(data["questions"])
    #     self.assertTrue(data["success"], True)

    # def test_404_sent_requesting_beyond_valid_page(self):
    #     res = self.client().get("/questions?page=7")
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data["success"], False)
    #     self.assertEqual(data["message"], "resource not found")

    def test_successful_create_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        question = Question.query.get(data["created"])

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(question)
    
    def test_400_badadd_question_request(self):
        res = self.client().post("/questions", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["error"], 405)

    def test_delete_question(self):
        question = Question(
            question=self.new_question["question"],
            answer=self.new_question["answer"],
            difficulty=self.new_question["difficulty"],
            category=self.new_question["category"],
        )
        question.insert()
        question_id = question.id

        res = self.client().delete("/questions/" + str(question_id))
        data = json.loads(res.data)

        question = Question.query.get(question_id)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsNone(question)

    # def test_retrieve_categories(self):
    #     res = self.client().get("/categories")
    #     data = json.loads(res.data)
        
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertTrue(data["categories"])
    #     self.assertTrue(data["total_categories"])

    # def test_404_sent_requesting_beyond_valid_categoryId(self):
    #     res = self.client().get("/categories/7/questions")
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data["success"], False)
    #     self.assertEqual(data["message"], "resource not found")

    def test_quizzes(self):
        quiz = {
            "quiz_category": {"id": 1, "type": "Science"},
            "previous_questions": [20, 21]
        }
        res = self.client().post("/quizzes", json=quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertNotEqual(data['question']['id'], 20)
        self.assertNotEqual(data['question']['id'], 21)
    
    def test_422_unprocessable_retrieving_quizzes(self):
        res = self.client().post("/quizzes", json=self.quiz_422)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], "unprocessable")
        self.assertTrue(data['error'])


    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()