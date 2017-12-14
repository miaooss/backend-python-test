from alayatodo import ( app, todo_repo, user_repo )
from flask import (
    g,
    redirect,
    render_template,
    request,
    session
    )
import json


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    user = user_repo.login(username, password)
    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    todo = todo_repo.findById(session['user']['id'], id)
    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    todo = todo_repo.findById(id, session['user']['id'])
    if todo:
        return json.dumps({u"id": todo["id"], u"user_id": todo["user_id"], u"description": todo["description"]})
    else:
        return json.dumps({u"code": 404, u"message": "not found"})


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')

    nbElementByPage = 5
    elementTotal = todo_repo.countAll(session['user']['id'])
    nbPageTotal = int(elementTotal / nbElementByPage) + (21 % nbElementByPage > 0)
    currentPage = 0
    getPage = request.args.get('page')
    if getPage and getPage.isdigit():
        currentPage = int(getPage)
    offset = currentPage * nbElementByPage

    todos = todo_repo.findLimited(session['user']['id'], nbElementByPage, offset)
    return render_template('todos.html', todos=todos, message=session.pop('message', None), nbPageTotal=nbPageTotal, currentPage=currentPage)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    description = request.form.get('description', '')
    if description:
        todo_repo.add(session['user']['id'], description)
        session['message'] = "Your new todo as been correctly added"
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo_repo.delete(session['user']['id'], id)
    session['message'] = "Your todo as been correctly removed"
    return redirect('/todo')


@app.route('/todo/complete/<id>', methods=['GET'])
def todo_complete(id):
    if not session.get('logged_in'):
        return redirect('/login')

    todo_repo.updateStatus(session['user']['id'], id, 1)
    return redirect('/todo')


