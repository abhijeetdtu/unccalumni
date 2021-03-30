from unccalumni.web.dash.Basic import Basic
from flask import render_template
from flask import Flask
app = Flask(__name__)

dash_endpoints = {
"/dash/basic/":[Basic , "Basic"]
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
    app.run(debug=True)
