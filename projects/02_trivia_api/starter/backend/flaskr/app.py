import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


def paginate_books(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    books = [book.format() for book in selection]
    current_books = books[start:end]

    return current_books


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={"*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
        return response

    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        categories_formatted = [category.format() for category in categories]

        all_categories = {}
        for c in categories_formatted:
            all_categories[c['id']] = c['type']

        return jsonify({
            'success': True,
            'categories': all_categories
        })

    QUESTIONS_PER_PAGE = 10

    @app.route('/questions')
    def get_questions():

        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        selection = Question.query.all()
        questions = [q.format() for q in selection]
        current_questions = questions[start:end]

        categories = Category.query.all()
        categories_formatted = [category.format() for category in categories]

        all_categories = {}
        for c in categories_formatted:
            all_categories[c['id']] = c['type']

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': None,
            'categories': all_categories
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        try:
            question = Question.query.filter(Question.id == question_id).first()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })

        except:
            abort(404)

    @app.route('/question', methods=['POST'])
    def post_question():

        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)

        try:
            question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty,
                                category=new_category)
            question.insert()
            return jsonify({
                'success': True,
                'created': question.id
            })

        except:
            abort(405)

    @app.route('/questions', methods=["POST"])
    def search_question():
        body = request.get_json()

        search_item = body.get('searchTerm')
        questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_item))).all()

        if questions is None:
            return jsonify({
                'questions': None,
                'total_questions': 0
            })

        else:
            result_questions = [q.format() for q in questions]
            return jsonify({
                'questions': result_questions,
                'total_questions': len(result_questions)
            })

    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):

        questions = Question.query.filter(Question.category == str(category_id)).all()
        result_questions = [q.format() for q in questions]

        return jsonify({
            'questions': result_questions,
            'total_questions': len(result_questions)
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():

        body = request.get_json()
        category = body.get('quiz_category')
        previous_questions = body.get('previous_questions')
        category_id = category['id']
        if category_id != 0:
            questions = Question.query.filter(Question.category == category_id).filter(
                ~Question.id.in_(previous_questions)).all()
        else:
            questions = Question.query.filter(~Question.id.in_(previous_questions)).all()

        result_questions = [q.format() for q in questions]

        try:
            question = random.choice(result_questions)
            return jsonify({
                'question': question
            })

        except IndexError:
            return jsonify({
                'question': None
            })

    '''  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    return app
