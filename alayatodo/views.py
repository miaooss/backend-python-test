from alayatodo import app
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

    sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
    cur = g.db.execute(sql % (username, password))
    user = cur.fetchone()
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
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s' AND user_id='%s'" % (id, session['user']['id']))
    todo = cur.fetchone()
    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    cur = g.db.execute("SELECT * FROM todos WHERE id ='%s' AND user_id='%s'" % (id, session['user']['id']))
    todo = cur.fetchone()
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
    cur = g.db.execute("SELECT COUNT(id) as elementTotal FROM todos WHERE user_id = '%s'" % session['user']['id'])
    elementTotal = cur.fetchone()["elementTotal"]
    nbPageTotal = int(elementTotal / nbElementByPage) + (21 % nbElementByPage > 0)
    currentPage = 0
    getPage = request.args.get('page')
    if getPage and getPage.isdigit():
        currentPage = int(getPage)
    offset = currentPage * nbElementByPage

    cur = g.db.execute("SELECT * FROM todos WHERE user_id = '%s' LIMIT %d, %d" % (session['user']['id'], offset, nbElementByPage))
    todos = cur.fetchall()

    return render_template('todos.html', todos=todos, message=session.pop('message', None), nbPageTotal=nbPageTotal, currentPage=currentPage)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    description = request.form.get('description', '')
    if description:
        g.db.execute(
            "INSERT INTO todos (user_id, description) VALUES ('%s', '%s')"
            % (session['user']['id'], description)
        )
        g.db.commit()
        session['message'] = "Your new todo as been correctly added"
    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("DELETE FROM todos WHERE id ='%s' AND user_id='%s'" % (id, session['user']['id']))
    g.db.commit()
    session['message'] = "Your todo as been correctly removed"
    return redirect('/todo')


@app.route('/todo/complete/<id>', methods=['GET'])
def todo_complete(id):
    if not session.get('logged_in'):
        return redirect('/login')

    g.db.execute("UPDATE todos SET status = %d WHERE id = '%s' AND user_id = '%s'" % (1, id, session['user']['id']))
    g.db.commit()
    return redirect('/todo')


