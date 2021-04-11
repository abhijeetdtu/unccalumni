from unccalumni.web.dash.Basic import Basic
from unccalumni.web.dash.Scores import Scores
from unccalumni.web.dash.Maps import Maps
from unccalumni.web.dash.MultiMelt import MultiMelt
from unccalumni.web.dash.Summary import Summary
from flask import render_template
from flask import Flask
app = Flask(__name__)

dash_endpoints = {
"/dash/summary/":[Summary , "Summary"],
"/dash/basic/":[Basic , "Applicant Counts"],
"/dash/scores/":[Scores , "Test Scores"],
"/dash/multimelt/":[MultiMelt , "Applicant Background"],
"/dash/maps/":[Maps , "Maps"]

    # "/dash/wordtrend/" : [WordTrend , "Word Trend"],
    # "/dash/wordprop/" : [WordProportion , "Word Proportions"],
    # "/dash/wordcorr/" : [WordCorrelations , "Word Correlations"],
    # "/dash/termdist/" : [TermDistMetric , "Term Distance"],
    # "/dash/trendrank/" : [TrendRank , "Word Rank Trend"]
}

def initialize_dash(app):
    return [v[0](k , app) for k,v in dash_endpoints.items()]

initialize_dash(app)

@app.route('/')
def hello_world():
    dash_urls = [[k,v[1]] for k,v in dash_endpoints.items()]
    return render_template('landing.html' , dash_urls = dash_urls)


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=8080)
