## README

The outbreak of US started at about 3/1. This program uses 7 day window rolling horizon R0 estimation and prediction. So the results starts from 3/7.

The newer days has higher weight during minimizing the fitting error. The fitted R0 can be less than 0 when there is significant drop in confirmed cases in some days. In that case R0 is forced to be 0 and the decision variable is changed to infectious number. Proper filtering of the data may reduce the periodical fluctuation of the R0 estimation. 

The entry of the code is forecastAll.py, and the results for states over 5000 confirmed cases is stored in summary.json.
