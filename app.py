from flask import Flask
from flask import jsonify
from flask import request
import shelve
import uuid
import json

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/<name>')
def hello_name(name):
    return jsonify(f'Hello {name}')


@app.route('/people', methods=['GET', 'POST'], defaults={'id': None})
@app.route('/people/<uuid:id>', methods=['GET', 'DELETE', 'PUT'])
def people(id):
    # create new person
    if request.method == 'POST':
        with shelve.open('people.db', writeback=True) as db:
            person = json.loads(request.data)
            person['id'] = str(uuid.uuid4())
            db.setdefault('people', []).append(person)
        return jsonify(person), 201

    # list all people
    elif request.method == 'GET' and id is None:
        with shelve.open('people.db') as db:
            return jsonify(db.setdefault('people', []))

    # read single person
    elif request.method == 'GET':
        with shelve.open('people.db') as db:
            for person in db['people']:
                if person.get('id') == str(id):
                    return jsonify(person)
        return '', 404

    # delete single person
    elif request.method == 'DELETE':
        with shelve.open('people.db', writeback=True) as db:
            people_list: list = db.get('people', [])
            for person in people_list:
                if person.get('id') == str(id):
                    people_list.remove(person)
                    return '', 204

        return '', 404

    elif request.method == 'PUT':
        with shelve.open('people.db', writeback=True) as db:
            people_list: list = db.get('people', [])
            for person in people_list:
                if person.get('id') == str(id):
                    new_data = json.loads(request.data)
                    new_data.pop('id', None)
                    person.update(**new_data)
                    return jsonify(person)

        return '', 404




if __name__ == '__main__':
    app.run()
