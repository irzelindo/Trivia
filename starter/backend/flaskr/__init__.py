import os
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
CATEGORIES_PER_PAGE = 5

def questios_per_page(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = QUESTIONS_PER_PAGE * page
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  return current_questions


def categories_per_page(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * CATEGORIES_PER_PAGE
  end = CATEGORIES_PER_PAGE * page
  categories = [category.format() for category in selection]
  current_categories = categories[start:end]
  return current_categories

def retrieve_questions(request):
  questions = Question.query.order_by(Question.id).all()
  current_questions = questios_per_page(request, questions)
  return questions, current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  '''
  @DEFINING ERROR handlers functions
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Resource Not found"
        }), 404
        
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad Request"
        }), 400

  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "Unprocessable Request"
        }), 422

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    try:
      categories = Category.query.order_by(Category.id).all()
      current_categories = [category.type for category in categories]

      if len(categories) == 0:
            abort(404)
      else: 
        return jsonify({
          'success': True,
          'status_code': 200,
          'status_code_message': 'OK',
          'categories': current_categories,
          'total_categories': len(categories)
        })

    except:
      abort(404)  


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  '''

  @app.route('/questions')
  def get_questions():
    try:
      questions, current_questions = retrieve_questions(request)
      #questions = questios_per_page(request, selection)
      selection = Category.query.order_by(Category.id).all()
      categories = [category.type for category in selection]

      if len(current_questions) == 0:
            abort(404)
      else: 
        return jsonify({
          'success': True,
          'status_code': 200,
          'status_code_message': 'OK',
          'questions': current_questions,
          'total_questions': len(questions),
          'current_category': len(categories),
          'categories': categories
        })

    except:
      abort(404)  

  '''
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)
      else:
        question.delete()
        questions, current_questions = retrieve_questions(request)

      return jsonify({
        'success': True,
        'status_code': 200,
        'status_code_message': 'OK',
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(questions)
      })
    except:
      abort(422)

  '''
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  '''
  @app.route('/questions/new', methods=['POST'])
  def create_question():
    body = request.get_json()

    if body:
      new_question = body.get('question')
      new_answer = body.get('answer')
      new_category = body.get('category')
      new_dificulty = body.get('difficulty')

      try:
        question = Question(question=new_question, answer=new_answer,
          category=new_category, difficulty=new_dificulty)
        
        question.insert()

        questions, current_questions = retrieve_questions(request)

        return jsonify({
          'success': True,
          'status_code': 201,
          'status_code': 'Created',
          'created_question': question.id,
          'questions': current_questions,
          'total_questions': len(questions)
        })  
      except:
        abort(422)      
    else:
      abort(422) 

  
  '''
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    body = request.get_json()
    search_term = '%{}%'.format(body.get('searchTerm'))
    #print(search_term)
    try:
      filtered_questions = Question.query.filter(Question.question.like(search_term)).all()
      current_questions = [question.format() for question in filtered_questions]
      
      questions, x = retrieve_questions(request)

      #print(current_questions)

      return jsonify({
        'success': True,
        'status_code': 200,
        'status_code_message': 'Ok',
        'current_category': 2,
        'questions': current_questions,
        'total_questions': len(questions)
      })
    
    except:
      abort(400)


  '''
  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def questions_by_categories(category_id):
    #print(category_id)
    try:
      category_questions = Question.query.filter(Question.category == category_id).all()
      current_questions = [question.format() for question in category_questions]
      if category_questions is None:
        abort(404)
      else:
        questions, x = retrieve_questions(request)

        return jsonify({
            'success': True,
            'status_code': 200,
            'status_code_message': 'OK',
            'current_category': category_id-1,
            'questions': current_questions,
            'total_questions': len(questions)
          })

    except:
      abort(422)


  '''
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    category = body.get('quiz_category').get('id') 
    print(category) 
    prev_question = body.get('previous_questions')
    print(prev_question)
    category_questions = Question.query.filter(Question.category==category).all()
    questions = [question.format() for question in category_questions]
    random_number = int(random.random()*len(questions))
    current_question = questions[random_number]
    check = True
    try:
      while check:
        print(current_question.get('id'))
        if current_question.get('id') not in prev_question:
          return jsonify({
            'success': True,
            'status_code': 200,
            'status_code_message': 'OK',
            'question': current_question
          })
        else:
          if len(questions) > len(prev_question):
            random_number = int(random.random()*len(questions))
            current_question = questions[random_number]
          else:
            check = False
      
      return jsonify({
        'success': True,
        'status_code': 200,
        'status_code_message': 'OK',
        'question': current_question
      })
    except:
      abort(400)


  '''
  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
 
  return app

    