# Applicant Mapping Project

# Architecture

<center>
<img src="https://user-images.githubusercontent.com/6872080/116255141-fa5b5580-a73f-11eb-8f42-f459a42e5b8d.png" width="50%"> </img>
</center>

# API Documentation [here](https://abhijeetdtu.github.io/unccalumni/unccalumni/web/dash.html)

### Technologies used
  - Python
    - Flask
    - Dash
    - Plotnine
   - Heroku

# Running Application Locally

 - Clone the repository
    - `git clone https://github.com/abhijeetdtu/unccalumni`
 - Go to root of the code base
    - `cd unccalumni`
 - Install Dependencies
    - `python -m pip install -r requirements.txt`
 - Run the web application
    - `python -m unccalumni.web.main`
 - Access application in browser @ `localhost:8080`
 
  
# Making Changes
  - Since the application is **Flask**, **Dash** based and uses **Plotnine**, familiarity with these techs will be needed.
  - `unccalumni/data` folder houses all the current data.
    - This also includes Map data like shapefiles
  - `unccalumni/web` houses the web application and all code for visualization
     - `unccalumni/web/dash` has all the dashboards
     
# Deploying to heroku
  - Currently the flask application is hosted on `Heroku`
  - Install and setup Heroku command line as given [here](https://devcenter.heroku.com/articles/heroku-cli#download-and-install)
  - To create an Heroku App
      - `git clone https://github.com/abhijeetdtu/unccalumni` (ignore if already have the code base)
      - Go to root of the code base
          - `cd unccalumni`
      - `heroku create $APPLICATION_NAME` (replace $APPLICATION_NAME with a name of your choice)
      - Push the changes to Heroku : `git push heroku master` 
      - Now you will be able to see your application at `https://$APPLICATION_NAME.herokuapp.com `
      - In case of any issues follow the guide [here](https://dash.plotly.com/deployment)

# Current State
  - Currently the application has 5 dashboards
   
  |Dashboard||
  |---|---|
  |Summary|![image](https://user-images.githubusercontent.com/6872080/116257868-6b037180-a742-11eb-9014-119c8e47a880.png)|
  |Applicant Counts|![image](https://user-images.githubusercontent.com/6872080/116258078-a00fc400-a742-11eb-8461-2cced5569f15.png)|
  |Test Scores|![image](https://user-images.githubusercontent.com/6872080/116258676-24624700-a743-11eb-829f-bf9d52220b2f.png)|
  |Maps|![image](https://user-images.githubusercontent.com/6872080/116258776-3e9c2500-a743-11eb-8238-984bc5f6b9bc.png)|
  |Applicant Background|This is the slowest dashboard that fails to load quite a few times due to Heroku timeouts|
