from flask import Flask, redirect, session, send_from_directory,render_template,request
from db.scripts import do,DBWrapper
from db.queries import get_by_id
from utils.settings import settings

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.key
db = DBWrapper(settings.DBName)

@app.route('/')
def index():
    session["statementID"] = 1
    session["intellectScores"] = {
        "Логический":0,
        "Внутренний":0,
        "Телестный":0,
        "Вербальный":0,
        "Музыкальный":0,
        "Образный":0,
        "Филосовский":0,
        "Социальный":0,
        "Природный":0
    }
    return send_from_directory("./static/html/","main.html")

@app.route('/test')
def test():
    data = do(get_by_id, [session["statementID"]])
    #получить points из формы 
    if not data:
        return redirect('/result')
    question = data[0][1]


    return render_template("test.html",question=question,statementID=session["statementID"])



@app.route("/back")
def back():
    if session["statementID"] < 1: return
    intellect = session["last"]["intellect"]

    session["intellectScores"][intellect] -= session["last"]["answer"]

    if session["intellectScores"][intellect] < 0: session["intellectScores"][intellect] = 0
    session["statementID"] -= 1
    return redirect("/test")

@app.route("/answer")
def next():
    answer = int(request.args.get('value'))
    
    db.connect()
    data = db.get(get_by_id, [session["statementID"]])
    db.disconnect()

    if not data:
        return redirect("/result")
    intellect = data[0][2]
    session["intellectScores"][intellect] += answer

    session["last"] = {"intellect":intellect,"answer":answer}

    if session["intellectScores"][intellect] < 0: session["intellectScores"][intellect] = 0

    session["statementID"] += 1
    return redirect("/test")
    

@app.route('/result')
def result():
    session['statementID'] = 1
    
    return render_template("result.html",labels=list(session["intellectScores"].keys()),data =list(session["intellectScores"].values()))

if __name__ == '__main__':
    app.run(debug=True)
