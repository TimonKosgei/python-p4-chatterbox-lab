from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import asc
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(asc(Message.created_at)).all()
        response =  jsonify([message.to_dict() for message in messages])
        return make_response(response, 200)
    if request.method == 'POST':
        data = request.get_json()
        body  = data.get('body')
        username = data.get('username')
        if not body or not username:
            return make_response(jsonify({"error": "Both body and username are required"}), 400)

        new_message = Message(body=body, username=username) 
        db.session.add(new_message)
        db.session.commit()
        response = jsonify(new_message.to_dict())
        return make_response(response, 201)

@app.route('/messages/<int:id>', methods = ['PATCH','DELETE'])
def messages_by_id(id):
    if request.method == 'PATCH':
        message = Message.query.filter(Message.id == id).first()
        data = request.get_json()
        body = data.get('body')

        if not body:
            return make_response(jsonify({"error":"Body is required"}), 400)
        if not message:
            return make_response(jsonify({"error":"Message not found"}), 404)
        
        message.body = body
        db.session.commit()

        return make_response(jsonify(message.to_dict()),200)
    
    if request.method == 'DELETE':
        message = Message.query.filter(Message.id == id).first()
        db.session.delete(message)
        db.session.commit()
        return make_response(jsonify({"message":"Message deleted"}), 200)

if __name__ == '__main__':
    app.run(port=4000, debug=True)
