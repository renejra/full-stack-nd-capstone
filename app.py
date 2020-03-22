import os
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from models import setup_db, Strategy, Bot
import json, requests
from auth import requires_auth, AuthError

def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    '''
    Strategies Routes
    Setting up routes for getting, posting, patching and deleting strategies
    '''

    @app.route('/')
    def greet():
        response = {
            'message': 'Welcome to Trading Bot App! Public endpoints are /strategies and /bots, use JWT tokens provided for all other ones.'
        }
        return jsonify(response), 200

    @app.route('/strategies')
    def get_strategies():
        strategies = Strategy.query.all()
        response = []
        for strategy in strategies:
            record = {
                'id' : strategy.id,
                'name' : strategy.name,
            }
            response.append(record)
        return jsonify(response), 200

    @app.route('/strategies-detail')
    @requires_auth('get:strategies')
    def get_strategies_detail(payload):
        strategies = Strategy.query.all()
        response = []
        for strategy in strategies:
            record = {
                'id' : strategy.id,
                'name' : strategy.name,
                'params' : [par for par in strategy.params],
            }
            response.append(record)
        return jsonify(response), 200
    
    @app.route('/strategies/create', methods = ['POST'])
    @requires_auth('post:strategies')
    def post_strategy(payload):
        body = request.get_json()
        count = Strategy.query.count()

        try:
            record = Strategy(
                id = body.get('id'),
                name = body.get('name'),
                params = body.get('params').split(', ')
            )
            record.insert()

            response = {
                'success' : True,
                'id' : record.id,
                'name' : record.name,
                'params' : record.params,
            }

            return jsonify(response), 200

        except Exception:
            abort(400)

    @app.route('/strategies/<int:strategy_id>', methods = ['PATCH'])
    @requires_auth('patch:strategies')
    def edit_strategy(payload, strategy_id):
        body = request.get_json()
        strategy = Strategy.query.filter(Strategy.id == strategy_id).one_or_none()
        
        try:
            if body.get('name') is not None:
                strategy.name = body.get('name')
            
            if body.get('params') is not None:
                strategy.params = body.get('params').split(', ')

            strategy.update()

            response = {
                'success' : True,
                'name' : strategy.name,
                'params' : strategy.params
            }

            return jsonify(response), 200

        except Exception:
            abort(400)

    @app.route('/strategies/<int:strategy_id>', methods = ['DELETE'])
    @requires_auth('delete:strategies')
    def delete_strategy(payload, strategy_id):
        strategy = Strategy.query.filter(Strategy.id == strategy_id).one_or_none()

        try:
            strategy.delete()

            response = {
                'success' : True,
                'strategy' : f'Strategy with ID {strategy_id} was deleted'
            }

            return jsonify(response), 200

        except Exception:
            abort(400)


    '''
    Bots Routes
    Setting up routes for getting, posting, patching and deleting bots
    '''

    @app.route('/bots')
    def get_bots():
        bots = Bot.query.all()
        response = []
        for bot in bots:
            record = {
                'id' : bot.id,
                'name' : bot.name,
                'active' : bot.active,
            }
            response.append(record)

        return jsonify(response), 200

    @app.route('/bots-detail')
    @requires_auth('get:bots')    
    def get_bots_details(payload):
        bots = Bot.query.all()
        response = []
        for bot in bots:
            strategy = Strategy.query.filter(Strategy.id == bot.strategy_id).one_or_none()
            record = {
                'id' : bot.id,
                'name' : bot.name,
                'active' : bot.active,
                'strategy' : strategy.name,
                'strategy_id' : bot.strategy_id,
                'timeframe' : bot.timeframe,
                'params' : [ par for par in strategy.params ],
                'param_values' : [ val for val in bot.param_values ],
            }
            response.append(record)

        return jsonify(response), 200
    
    @app.route('/bots/create', methods = ['POST'])
    @requires_auth('post:bots')
    def post_bot(payload):
        body = request.get_json()
        count = Bot.query.count()

        try:
            record = Bot(
                id = body.get('id'),
                name = body.get('name'),
                active = body.get('active'),
                strategy_id = body.get('strategy_id'),
                timeframe = body.get('timeframe'),
                param_values = body.get('param_values').split(', ')
            )
            record.insert()

            response = {
                'success' : True,
                'id' : record.id,
                'name' : record.name,
                'active' : record.active,
                'param_values' : record.param_values,
                'timeframe' : record.timeframe,
                'strategy_id' : record.strategy_id
            }

            return jsonify(response), 200

        except Exception:
            abort(400)
    
    @app.route('/bots/<int:bot_id>', methods = ['PATCH'])
    @requires_auth('patch:bots')
    def edit_bot(payload, bot_id):
        body = request.get_json()
        bot = Bot.query.filter(Bot.id == bot_id).one_or_none()

        try:
            if body.get('name') is not None:
                bot.name = body.get('name')
        
            if body.get('active') is not None:
                bot.active = body.get('active')

            if body.get('strategy_id') is not None:
                bot.strategy_id = body.get('strategy_id')
            
            if body.get('timeframe') is not None:
                bot.timeframe = body.get('timeframe')

            if body.get('param_values') is not None:
                bot.param_values = body.get('param_values').split(', ')
            
            bot.update()

            response = {
                'success' : True,
                'id' : bot.id,
                'name' : bot.name,
                'active' : bot.active,
                'strategy_id' : bot.strategy_id,
                'timeframe' : bot.timeframe,
                'param_values' : [ val for val in bot.param_values ]
            }

            return jsonify(response), 200
        
        except Exception:
            abort(400)

    @app.route('/bots/<int:bot_id>', methods = ['DELETE'])
    @requires_auth('delete:bots')
    def delete_bot(payload, bot_id):
        bot = Bot.query.filter(Bot.id == bot_id).one_or_none()

        try:
            bot.delete()

            response = {
                'success' : True,
                'bot' : f'Bot with ID {bot_id} was deleted'
            }

            return jsonify(response), 200

        except Exception:
            abort(400)

    '''
    Error Handlers
    '''
    
    @app.errorhandler(400)
    def badrequest(error):
        return jsonify({
                        "success": False, 
                        "error": 400,
                        "message": "bad request"
                        }), 400


    @app.errorhandler(401)
    def notauthorized(error):
        return jsonify({
                        "success": False, 
                        "error": 401,
                        "message": "not authorized"
                        }), 401


    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
                        "success": False, 
                        "error": 403,
                        "message": "forbidden"
                        }), 403


    @app.errorhandler(404)
    def notfound(error):
        return jsonify({
                        "success": False, 
                        "error": 404,
                        "message": "resource not found"
                        }), 404


    @app.errorhandler(405)
    def notallowed(error):
        return jsonify({
                        "success": False, 
                        "error": 405,
                        "message": "method not allowed"
                        }), 405

    @app.errorhandler(500)
    def servererror(error):
        return jsonify({
                        "success": False, 
                        "error": 500,
                        "message": "server error"
                        }), 500


    @app.errorhandler(AuthError)
    def autherror(error):
        print(error)
        return jsonify({
            'success': False,
            'error': error.status_code,
            'message': error.error['description']
        }), error.status_code

    return app

app = create_app()

if __name__ == '__main__':
    app.run()