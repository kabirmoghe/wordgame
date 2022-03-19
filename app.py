from flask import Flask, redirect, url_for, render_template, request, session
import game
import readbucketdata
import createData

app = Flask(__name__)
app.secret_key = 'hello'

def reset():
	if "possWords" in session:
		session.pop("possWords")
	session["maxList"] = []
	session["guesses"] = {}
	session["bestGuesses"] = {}
	session["score"] = 0
	session["numGuesses"] =  0
	session["scoreGauge"] = ""
	session["scorePos"] = 0
	session["oldScorePos"] = 0
	session["oldMaxPoints"] = 0
	session["oldBestList"] = ""
	session["status"] = "not done"
	session["level"] = ""
	session["slide"] = ""
	session["totalWords"] = ""

@app.route("/", methods = ["GET", "POST"])
def home():

	session.permanent = True

	word_info = readbucketdata.readbucketdata("letters.csv")
	old_word_info = readbucketdata.readbucketdata("oldletters.csv")

	oldMaxPoints, oldBestWords = old_word_info["maxPoints"][0], eval(old_word_info["bestWords"][0])

	letters, letterPts, maxPoints, bestWords, lid = eval(word_info["letters"][0]), eval(word_info["letterPts"][0]), word_info["maxPoints"][0], eval(word_info["bestWords"][0]), int(word_info["lid"][0])

	session["bestWordsOnly"] = [wordPair[0].title() for wordPair in bestWords]

	session["letters"] = letters
	session["maxPoints"] = int(maxPoints)

	session["oldMaxPoints"] = int(oldMaxPoints)

	if "lid" not in session:
		session["lid"] = lid
		reset()

	elif session["lid"] != lid:
		session["lid"] = lid
		reset()

	if "possWords" not in session:
		session["possWords"] = eval(word_info["possWords"][0])

	possWords = session["possWords"]

	if "score" in session:
		score = session["score"]
	else:
		session["score"] = 0
		score = session["score"]

	if "maxList" not in session:
		session["maxList"] = []

	if "oldBestList" not in session:
		session["oldBestList"] = []

	if "guesses" not in session:
		session["guesses"] = {}

	if "score" not in session:
		session["score"] = 0
 
	if "numGuesses" not in session:
		session["numGuesses"] =  0

	if "scoreGauge" not in session:
		session["scoreGauge"] = ""

	if "scorePos" not in session:
		session["scorePos"] = 0

	if "oldScorePos" not in session:
		session["oldScorePos"] = 0

	if "status" not in session:
		session["status"] = "not done"

	if "level" not in session:
		session["level"] = "nice"

	if "slide" not in session:
		session["slide"] = ""

	if "totalWords" not in session:
		session["totalWords"] = ""

	if "bestGuesses" not in session:
		session["bestGuesses"] = {}

	if (session["maxPoints"] == session["score"]) or (session["numGuesses"] == 10):
		session["status"] = "done"

		return redirect(url_for('done'))

	if session["status"] == "done":
		return redirect(url_for('done'))

	session["totalWords"] = "{} points\n".format(session["maxPoints"])

	if score == maxPoints:
		scoreGauge = "{} You reached ".format(game.score_gauge(score, maxPoints)[0])

	else: 
		scoreGauge = "{} You scored ".format(game.score_gauge(score, maxPoints)[0])

	session["scoreGauge"] = scoreGauge

	session["scorePos"] = game.score_gauge(score, maxPoints)[1]

	session["maxList"] = [("{}, {}".format(bestWords[i][0].title(), bestWords[i][1])) for i in range(len(bestWords))]

	session["oldBestList"] = [("{}, {}".format(oldBestWords[i][0].title(), oldBestWords[i][1])) for i in range(len(oldBestWords))]

	session["totalWords"] = "{} points\n".format(session["maxPoints"])

	session["oldScorePos"] = session["scorePos"]

	check = ""

	if request.method == "POST":

		if ("submit" in request.form):
			session.pop("usr")
			return redirect(url_for("home"))

		tile1 = request.form["1"]
		tile2 = request.form["2"]
		tile3 = request.form["3"]
		tile4 = request.form["4"]
		tile5 = request.form["5"]

		guess = (tile1 + tile2 + tile3 + tile4 + tile5).lower()

		is_word = (guess in possWords)

		if (is_word == False):

			error = "Invalid word"

			guesses = session["guesses"]

			if (guess.title() in guesses):
				error = "Already guessed"

			session["guesses"] = {word: pts for word, pts in sorted(guesses.items(), key=lambda item: item[1], reverse = True)}

			bestGuesses = {}

			if len(session["guesses"]) < 5:
			    bestGuesses = session["guesses"]
			else:
			    for word in list(session["guesses"].keys())[:5]:
			        bestGuesses[word] = session["guesses"][word]

			bestGuesses = {word: pts for word, pts in sorted(bestGuesses.items(), key=lambda item: item[1], reverse = True)}
			session["bestGuesses"] = bestGuesses

			session["level"] = game.score_gauge(session["score"], session["maxPoints"])[2]
			session["slide"] = game.score_gauge(session["score"], session["maxPoints"])[3]

			if ("usr" in session) and (session["usr"] == "kabirmoghe"):
				return render_template("adminGame.html", totalWords = session["totalWords"], letters = letters, guesses = session["guesses"], bestWordsOnly = session["bestWordsOnly"], error = error, score = session["score"], scorePos = session["scorePos"], oldMaxPoints = session["oldMaxPoints"], oldBestList = session["oldBestList"], maxPoints = session["maxPoints"], maxList = session["maxList"], oldScorePos = session["oldScorePos"], slide = session["slide"], bestGuesses = session["bestGuesses"])
			else:
				return render_template("game.html", totalWords = session["totalWords"], letters = letters, guesses = session["guesses"], bestWordsOnly = session["bestWordsOnly"], error = error, score = session["score"], scorePos = session["scorePos"], oldMaxPoints = session["oldMaxPoints"], oldBestList = session["oldBestList"], maxPoints = session["maxPoints"], oldScorePos = session["oldScorePos"], slide = session["slide"], bestGuesses = session["bestGuesses"], status=session["status"])

		else:

			check = "✓"

			pts = possWords[guess]
			guesses = session["guesses"]
			guesses[guess.title()] = pts
			guesses = {word: pts for word, pts in sorted(guesses.items(), key=lambda item: item[1], reverse = True)}

			bestGuesses = {}

			if len(guesses) < 5:
			    bestGuesses = guesses
			else:
			    for word in list(guesses.keys())[:5]:
			        bestGuesses[word] = guesses[word]

			bestGuesses = {word: pts for word, pts in sorted(bestGuesses.items(), key=lambda item: item[1], reverse = True)}

			session["bestGuesses"] = bestGuesses

			session["guesses"] = guesses

			score = sum(bestGuesses.values())

			session["score"] = score

			scorePos = game.score_gauge(score, maxPoints)[1]

			session["scorePos"] = scorePos

			session["level"] = game.score_gauge(session["score"], session["maxPoints"])[2]
			session["slide"] = game.score_gauge(session["score"], session["maxPoints"])[3]

			possWords.pop(guess)
			session["possWords"] = possWords

			session["totalWords"] = "{} points\n".format(session["maxPoints"])

			if score == maxPoints:
				session["scoreGauge"] = "{} You reached ".format(game.score_gauge(score, maxPoints)[0])

			else: 
				session["scoreGauge"] = "{} You scored".format(game.score_gauge(score, maxPoints)[0])

			session["maxList"] = [("{}, {}".format(bestWords[i][0].title(), bestWords[i][1])) for i in range(len(bestWords))]
			session["oldBestList"] = [("{}, {}".format(oldBestWords[i][0].title(), oldBestWords[i][1])) for i in range(len(oldBestWords))]

			session["numGuesses"] = session["numGuesses"] + 1

			if (session["maxPoints"] == session["score"]) or (session["numGuesses"] == 10):
				session["status"] = "done"

				return redirect(url_for('done'))

	session["level"] = game.score_gauge(session["score"], session["maxPoints"])[2]
	session["slide"] = game.score_gauge(session["score"], session["maxPoints"])[3]

	session["oldMaxPoints"], session["oldBestWords"] = int(old_word_info["maxPoints"][0]), eval(old_word_info["bestWords"][0])

	session["guesses"] = {word: pts for word, pts in sorted(session["guesses"].items(), key=lambda item: item[1], reverse = True)}
	session["bestGuesses"] = {word: pts for word, pts in sorted(session["bestGuesses"].items(), key=lambda item: item[1], reverse = True)}

	if ("usr" in session) and (session["usr"] == "kabirmoghe"):
		return render_template("adminGame.html", totalWords = session["totalWords"], scoreGauge = session["scoreGauge"], letters = letters, guesses = session["guesses"], bestWordsOnly = session["bestWordsOnly"] , score = session["score"], scorePos = session["scorePos"], possWords = session["possWords"], lid = session["lid"], oldMaxPoints = session["oldMaxPoints"], oldBestList = session["oldBestList"], maxPoints = session["maxPoints"], maxList = session["maxList"], oldScorePos = session["oldScorePos"], slide = session["slide"], bestGuesses = session["bestGuesses"])
	else:
		return render_template("game.html", totalWords = session["totalWords"], scoreGauge = session["scoreGauge"], letters = letters, guesses = session["guesses"], bestWordsOnly = session["bestWordsOnly"] , score = session["score"], scorePos = session["scorePos"], possWords = session["possWords"], lid = session["lid"], oldMaxPoints = session["oldMaxPoints"], oldBestList = session["oldBestList"], maxPoints = session["maxPoints"], oldScorePos = session["oldScorePos"], slide = session["slide"], bestGuesses = session["bestGuesses"], status=session["status"], check = check)

@app.route("/done", methods = ["GET", "POST"])
def done():

	if ("status" not in session) or (session["status"] != "done"):
		return redirect(url_for("home"))

	session["error"] = ""

	lid = int(readbucketdata.readbucketdata("letters.csv")["lid"][0])

	if "lid" not in session:
		session["lid"] = lid
		reset()
		return redirect(url_for("home"))

	elif session["lid"] != lid:
		session["lid"] = lid
		reset()
		return redirect(url_for('home'))

	if "guesses" in session:
		session["guesses"] = {word: pts for word, pts in sorted(session["guesses"].items(), key=lambda item: item[1], reverse = True)}
		session["bestGuesses"] = {word: pts for word, pts in sorted(session["bestGuesses"].items(), key=lambda item: item[1], reverse = True)}
	else:
		reset()
		return redirect(url_for('home'))

	if ("usr" in session) and (session["usr"] == "kabirmoghe"):
		return render_template("adminFinished.html", totalWords = session["totalWords"], scoreGauge = session["scoreGauge"], letters = session["letters"], guesses = session["guesses"], bestWordsOnly = session["bestWordsOnly"], score = session["score"], scorePos = session["scorePos"], maxPoints = session["maxPoints"], maxList = session["maxList"], oldMaxPoints = session["oldMaxPoints"], oldBestList = session["oldBestList"], level = session["level"], lid = session["lid"], oldScorePos = session["oldScorePos"], slide = session["slide"], bestGuesses = session["bestGuesses"])
	else:
		return render_template("finished.html", totalWords = session["totalWords"], scoreGauge = session["scoreGauge"], letters = session["letters"], guesses = session["guesses"], bestWordsOnly = session["bestWordsOnly"], score = session["score"], scorePos = session["scorePos"], maxPoints = session["maxPoints"], maxList = session["maxList"], oldMaxPoints = session["oldMaxPoints"], oldBestList = session["oldBestList"], level = session["level"], lid = session["lid"], oldScorePos = session["oldScorePos"], slide = session["slide"], bestGuesses = session["bestGuesses"], status=session["status"])

@app.route("/login", methods = ["GET", "POST"])
def login():

	if request.method == "POST":
		if (request.form["usr"] == "kabirmoghe") and (request.form["pwd"] == "Daod10Bgr6"):

			session["usr"] = "kabirmoghe"

			return redirect(url_for('home'))
		else:
			return render_template("invalidLogin.html", lid = session["lid"])

	return render_template("login.html", lid = session["lid"])

@app.route("/feedback", methods = ["GET", "POST"])
def feedback():

	lid = readbucketdata.readbucketdata("letters.csv")["lid"][0]

	return render_template("feedback.html", lid = lid)

@app.route("/data", methods = ["GET", "POST"])
def data():

	lid = readbucketdata.readbucketdata("letters.csv")["lid"][0]

	if "usr" not in session:
		return redirect(url_for('home'))

	else:

		if request.method == "POST":

			createData.main()

			return redirect(url_for("home"))

		return render_template("data.html", lid = lid)


if __name__ == '__main__':
    app.run(debug = True)