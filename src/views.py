import os
import subprocess
from datetime import datetime
from .communication_skill import estimate_communication

import flask
import numpy as np
import pandas as pd
from flask import render_template, request, session
from werkzeug.utils import secure_filename

from src import app
from src.objective import ObjectiveTest
from src.subjective import SubjectiveTest
from src.utils import backup, relative_ranking
import random
import sqlite3
import speech_recognition as sr

@app.route('/')
@app.route('/home')
def home():
    ''' Renders the home page '''
    print("!Start")
    directory = os.path.join(str(os.getcwd()), "database")
    session["database_path"] = os.path.join(str(os.getcwd()), "database", "database.db")
    conn = sqlite3.connect(session["database_path"])
    print("Opened Database Successfully")
    session["date"] = datetime.now()
    return render_template(
        "index.html",
        date=session["date"].day,
        month=session["date"].month,
        year=session["date"].year
    )


@app.route("/form", methods=['GET', 'POST'])
def form():
    ''' Prompt user to start the test '''
    if request.form["username"] == "":
        session["username"] = "Username"
    else:
        session["username"] = request.form["username"]
    return render_template(
        "form.html",
        username=session["username"]
    )

question_list = list()
answer_list = list()
number = 1
user_ans = list()

@app.route("/generate_test", methods=["GET", "POST"])
def generate_test():
    global number
    question_list.clear()
    answer_list.clear()
    user_ans.clear()
    number = 1
    session["subject_id"] = "0"
    if session["subject_id"] == "0":
        session["subject_name"] = "MOBILE ENGINEERING"
        session["filepath"] = os.path.join(str(os.getcwd()), "corpus", "question.txt")
    else:
        print("Done!")

    session["test_id"] = "1"

    if session["test_id"] == "1":
        directory = os.path.join(str(os.getcwd()), "database")
        session["database_path"] = os.path.join(str(os.getcwd()), "database", "database.db")
        conn = sqlite3.connect(session["database_path"])
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("select question from questions where id={}".format(number))
        rows = cur.fetchall()
        
        question = rows[0]["question"]
        question_list.append(question)

        cur.execute("select answer from answers where id={}".format(number))
        rows = cur.fetchall()
        
        answer = rows[0]["answer"]
        answer_list.append(answer)
        return render_template(
            "subjective_test.html",
            username=session["username"],
            testname=session["subject_name"],
            number=number,
            question=question
        )
    else:
        print("Done!")
        return None

@app.route("/generate_test_next", methods=["GET", "POST"])
def generate_test_next():
    global number
    number += 1
    session["subject_id"] = "0"
    if session["subject_id"] == "0":
        session["subject_name"] = "MOBILE ENGINEERING"
        session["filepath"] = os.path.join(str(os.getcwd()), "corpus", "question.txt")
    else:
        print("Done!")

    session["test_id"] = "1"

    if session["test_id"] == "1":
        directory = os.path.join(str(os.getcwd()), "database")
        session["database_path"] = os.path.join(str(os.getcwd()), "database", "database.db")
        conn = sqlite3.connect(session["database_path"])
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("select question from questions where id={}".format(number))
        rows = cur.fetchall()
        question = rows[0]["question"]
        question_list.append(question)

        cur.execute("select answer from answers where id={}".format(number))
        rows = cur.fetchall()
        answer = rows[0]["answer"]
        answer_list.append(answer)

        if number == 10:
            return render_template(
            "subjective_test_finish.html",
            username=session["username"],
            testname=session["subject_name"],
            number=number,
            question=question
            )
        return render_template(
            "subjective_test_next.html",
            username=session["username"],
            testname=session["subject_name"],
            number=number,
            question=question
        )
    else:
        print("Done!")
        return None

@ app.route("/audioprocess", methods=["GET", "POST"])
def audioprocess():
    audio_data = request.data
    transcript = ""
    print('Data Received')
    with open('audio.wav', 'wb') as f:
        f.write(audio_data)
    recognizer = sr.Recognizer()
    audioFile = sr.AudioFile('audio.wav')
    with audioFile as source:
        data = recognizer.record(source)
    transcript = recognizer.recognize_google(data, key=None)
    print(transcript)
    return transcript

@app.route("/estimate", methods=["GET", "POST"])
def estimate():
    _answer = answer_list[number-1]
    print(_answer)
    _answer = str(_answer).strip().upper()
    _data = str(request.form["answer1"])
    data = _data.strip().upper()
    user_ans.append(data)

    communication = estimate_communication('audio.wav', _data)
    
    default_ans = list()
    for x in answer_list:
        default_ans.append(str(x).strip().upper())
    total_score = 0
    status = None
    if session["test_id"] == "1":
        subjective_generator = SubjectiveTest(session["filepath"])
        if _answer == data:
            answer_score = 10.0
        else:
            answer_score = subjective_generator.evaluate_subjective_answer(_answer, data)
        total_score += answer_score
        answer_score = round(answer_score, 3)
    total_score = round(total_score, 3)

    return render_template(
        "score.html",
        username=session["username"],
        testname=session["subject_name"],
        number=number,
        answer_score=answer_score,
        communication=communication
    )

@ app.route("/output", methods=["GET", "POST"])
def output():
    data = str(request.form["answer1"]).strip().upper()
    user_ans.append(data)
    default_ans = list()
    # Process answers
    for x in answer_list:
        default_ans.append(str(x).strip().upper())
    print(len(default_ans), len(user_ans))
    total_score = 0
    status = None
    if session["test_id"] == "1":
        for i, _ in enumerate(default_ans):
            subjective_generator = SubjectiveTest(session["filepath"])
            if default_ans[i] == user_ans[i]:
                total_score += 10.0
            else:
                total_score += subjective_generator.evaluate_subjective_answer(default_ans[i], user_ans[i])
        total_score = round(total_score, 3)
        if total_score > 50.0:
            status = "Pass"
        else:
            status = "Fail"
    # Backup data
    session["score"] = np.round(total_score, decimals=2)
    session["result"] = status

    directory = os.path.join(str(os.getcwd()), "database")
    session["database_path"] = os.path.join(str(os.getcwd()), "database", "database.db")
    conn = sqlite3.connect(session["database_path"])
    cursor = conn.cursor()
    print(session["date"], '------', session["username"], '------', session["subject_name"], '------', session["subject_id"], '------', session["test_id"], '------', float(session["score"]), '------', session["result"])
    cursor.execute("INSERT INTO students (date, username, subject, subject_id, test_id, score, result) VALUES (?,?,?,?,?,?,?)", (session["date"], session["username"], session["subject_name"], int(session["subject_id"]), int(session["test_id"]), float(session["score"]), session["result"]))
    conn.commit()

    max_score, min_score, mean_score = relative_ranking(session)
    print(max_score, min_score, mean_score)
    question_list.clear()
    answer_list.clear()
    user_ans.clear()
    number = 1

    # Render output
    return render_template(
        "output.html",
        show_score=session["score"],
        username=session["username"],
        subjectname=session["subject_name"],
        status=session["result"],
        max_score=max_score,
        min_score=min_score,
        mean_score=mean_score
    )
