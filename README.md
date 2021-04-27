# unccalumni

# Architecture

<center>
<img src="https://user-images.githubusercontent.com/6872080/116255141-fa5b5580-a73f-11eb-8f42-f459a42e5b8d.png" width="50%"> </img>
</center>

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
