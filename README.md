#### Deploy to Heroku
https://dash.plotly.com/deployment
```
$ heroku login
$ git push heroku master # deploy code to heroku
$ heroku ps:scale web=1  # run the app with a 1 heroku "dyno"
```
