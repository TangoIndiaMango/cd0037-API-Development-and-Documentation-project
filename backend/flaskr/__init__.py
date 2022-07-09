import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from random import randrange
import json

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    cors = CORS(app, resources={
        r"/*": {
            "origins": "*"
        }
    })
#cors setup to allow all
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """# done

    @app.after_request
    def after_request(response):
        #Setting Access-Control headers

        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response    
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """#done


    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """#done
    @app.route("/categories", methods=['GET'])
    #endpoint to get all categories
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        #querying them to display by ID
                
        return jsonify(
            {
                "success": True,
                "categories": {category.id: category.type for category in categories},
                "Total categories": len(Category.query.all())
            }
        )


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    #done
    @app.route("/questions", methods=['GET'])
    def retrieve_questions():
        #Gets all the questions, returns all categories, success status and total number of questions
        selection = Question.query.order_by(Question.id).all()
        questions_by_page = paginate_questions(request, selection)
        #fetching the categories
        categories = Category.query.order_by(Category.id).all()

        if len(questions_by_page) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": questions_by_page,
                "total_questions": len(Question.query.all()),
                "categories":{category.id: category.type for category in categories},
            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    #done
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        #endpoint to delete a question by ID
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            
            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    #done
    @app.route("/questions", methods=["POST"])
    def create_question():
        #endpoint to post a new question
        #responses: 
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()

            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(405)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """#done
    @app.route("/questions/search", methods=["POST"])
    def get_question_by_search():
        #endpoint to get question by a search term
        body = request.get_json()
        search_term = body.get("searchTerm, None")
        
        try:
            questions = Question.query.filter(Question.question.ilike("%{}%".format(search_term)))

            return jsonify(
                {
                    "success": True,
                    "questions": [question.format() for question in questions]

            })
        except:
            abort(400)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    #done
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        #Endpoint to get questions based on category.
        
        try: 
            questions = Question.query.filter_by(category=category_id).all()
            selected = [question.format() for question in questions]

            return jsonify({
                "questions": selected,
                "total questions": len(questions),
                "current category": category_id
            })
        except:
            abort(500)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    #done
    @app.route("/quizzes", methods=["POST"])
    def retrieve_quizzes():
        data = request.get_json()
        category = data.get('quiz_category')
        previous_questions = data.get('previous_questions')
        rand_questions = None

        try:
            if category is None or category['id'] == 0:
                all_questions = Question.query.all()
                formatted_question = [question.format() for question in all_questions]
            else:
                filtered_question = Question.query.filter(Question.category == category['id']).all()
                formatted_question = [question.format() for question in filtered_question]
                       
            rand_questions = []
            for question in formatted_question:
                if question['id'] not in previous_questions:
                    rand_questions.append(question)
               
            if (len(rand_questions) > 0):
                questions = random.choice(rand_questions)
                # random.choice(rand_questions)

            return jsonify({
                'success': True,
                'question': questions,
                'previous_questions': previous_questions
            })  
            
        except:
            abort(422)

            
    # def retrieve_question_for_quiz():
    #       #Endpoint to get questions to play the quiz.
    #       #This endpoint takes category and previous question parameters
    #       #Returns random questions within the given category,

    #     data = dict(request.form or request.json or request.data)
    #     #request.get_json()
    #     previous_questions = data.get('previous_questions')
    #     category = data.get('quiz_category')


    #     # if not category or previous_questions:
    #     #         return jsonify(
    #     #             {
    #     #                 "success": False,
    #     #                 "error": 400,
    #     #             }
    #     #         )
        
    #     try:
    #         if category is None or category['id'] == 0:
    #             all_questions = Question.query.all()
    #                 #filter_by(category=category['id']).all()()
    #             formatted_questions = [question.format() for question in all_questions]
                    
    #                 #json.dump(formatted_questions)

    #         else:
    #             all_questions = Question.query.filter_by(Question.category ==category['id']).all()
    #             formatted_questions = [question.format() for question in all_questions]
    #             #Question.query.filter(Question.category.in_(previous_questions)).all()


    #         rand_question = []
    #         for question in formatted_questions:
    #             if question['id'] not in previous_questions:
    #                 rand_question.append(question)

    #             if (len(rand_question) > 0):
    #                 questions = random.choice(rand_question)


    #             return jsonify(
    #                 {
    #                 "success": True,
    #                 "question": questions,
    #                 "previous questions": previous_questions
    #             })
    #     except:
    #         abort(404)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            {
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify(
            {
            "success": False,
            "error": 422,
            "message": "Unprocessable entity"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify(
            {
            "success": False,
            "error": 500,
            "message": "Internal Server error"
        }), 500


    return app

