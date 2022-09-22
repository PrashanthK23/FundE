# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json

from flask import Flask, request, jsonify


from config import properties
import pandas as pd
import numpy as np
import collections
app = Flask(__name__)

@app.route('/api/v1/searchadvisor', methods=['GET', 'POST'])
def search_advisor():
    print('start')
    content = request.json
    print(content)
    df_clients=content
    #df_clients = getClientdata()
    df_advisors = getAdvisors()
    filtered_Advisors, percentage, match_list = filteredAdvisors(df_clients, df_advisors)
    advisor_score, percentage, match_list = rankAdvisors(df_clients, filtered_Advisors, percentage, match_list)
    response = {}
    # for each_advisor in advisor_score:
    #     response[each_advisor] = {'advisor_score': advisor_score[each_advisor]}
    # for each_advisor in percentage:
    #     if each_advisor in response:
    #         temp_dict = response[each_advisor]
    #         temp_dict.update({'percentage': percentage[each_advisor]})
    #         response[each_advisor] = temp_dict
    #     else:
    #         response[each_advisor] = {'advisor_score': 0, 'percentage': percentage[each_advisor]}
    # for each_advisor in match_list:
    #     if each_advisor in response:
    #         temp_dict = response[each_advisor]
    #         temp_dict.update({'match_list': match_list[each_advisor]})
    #         response[each_advisor] = temp_dict
    #     else:
    #         response[each_advisor] = {'advisor_score': 0, 'percentage': 0, 'match_list': match_list[each_advisor]}
    # response = sorted(response.items(), key=lambda x: x[1]['advisor_score'], reverse=True)
    response=[]
    for each_advisor in advisor_score:
        if each_advisor in percentage and each_advisor in match_list:
            response.append({'advisor':{'advisor_id':each_advisor,'match_list':match_list[each_advisor],'advisor_score': advisor_score[each_advisor]},'percentage':percentage[each_advisor]})
        else:
            response.append({'advisor': {'advisor_id': each_advisor,'match_list':[],'advisor_score': advisor_score[each_advisor]},
                             'percentage': 0})
    return response


# Press the green button in the gutter to run the script.
def getClientdata():
    df_clients=pd.DataFrame()
    request_json={
  "id": 1,
  "content": " Divorce Specialist Credit Counselling Business Succession Planning French Cantonese Bengali Woman 249999",
  "formData": {
    "areaOfSpecialties": [
      {
        "label": "Divorce Specialist",
        "value": "Divorce Specialist"
      },
      {
        "label": "Credit Counselling",
        "value": "Credit Counselling"
      },
      {
        "label": "Business Succession Planning",
        "value": "Business Succession Planning"
      }
    ],
    "languages": [
      {
        "label": "French",
        "value": "French"
      },
      {
        "label": "Cantonese",
        "value": "Cantonese"
      },
      {
        "label": "Bengali",
        "value": "Bengali"
      }
    ],
    "identity": "Woman",
    "whyNewAdvisor": "I'd like to get another advisor's perspective",
    "advisorAvailability": "yes",
    "totalInvestableAssets": "$100,000 - $249,999",
    "comment": ""
  }
}


    return request_json


def getAdvisors():
    return pd.read_csv('./data/advisor.csv')


def getclientChoice(client, each_column):
    if each_column=='LANGUAGE':
        clientList= list(each_lan['value'] for each_lan in client['formData']['languages'])
    elif each_column=='sex':
        clientList= [client['formData']['identity']]
    elif each_column=='expertise':
        clientList= list(each_lan['value'] for each_lan in client['formData']['areaOfSpecialties'])
    return clientList

def filteredAdvisors(client, df_advisors):
    percentage={}
    match_list={}
    filter_columns=properties.filters
    print(client['formData'])
    print(client['formData']['identity'])
    if client['formData']['identity']=='D':
        filter_columns.remove('sex')
    for each_column in filter_columns:
        clientList=getclientChoice(client,each_column)
        filtered_Advisors=df_advisors[df_advisors[each_column].isin(clientList)]

        for each_advisor in filtered_Advisors.advisorid.unique():
            if each_advisor in percentage:
                percentage[each_advisor]=percentage[each_advisor]+20
                match_list[each_advisor]=match_list[each_advisor]+[each_column]
            else:
                percentage[each_advisor] =20
                match_list[each_advisor] = [each_column]
    return filtered_Advisors,percentage,match_list


def get_client_list(each_pro, client):
    if each_pro == 'assets':
        client_list = [client['formData']['totalInvestableAssets']]
        return client_list
    else:
        return None


def rankAdvisors(client, filtered_Advisors,percentage,match_list):
    advisor_score={}
    if client['formData']['advisorAvailability']=='yes':
        cli_lat =43.731
        cli_lon =79.762
        for ind,each_advisor in filtered_Advisors[['advisorid','lat','lon']].drop_duplicates().iterrows():
            adv_lat=each_advisor.lat
            adv_lon=each_advisor.lat
            distance=np.sqrt(((adv_lat-cli_lat)**2)+((adv_lon-cli_lon)**2))
            advisorid=each_advisor.advisorid
            advisor_score[advisorid]=distance
        mean=sum(advisor_score.values()) / len(advisor_score)
        for each_key in advisor_score:
            advisor_score[each_key]=10-(advisor_score[each_key]/mean)
            if advisor_score[each_key]<5:
                if each_key in percentage:
                    percentage[each_key] = percentage[each_key] + 5
                else:
                    percentage[each_key] = 5
            else:
                if each_key in percentage:
                    percentage[each_key]=percentage[each_key]+15
                    match_list[each_key] = match_list[each_key]+['nearest place']
                else:
                    percentage[each_key] =15
                    match_list[each_key] = ['nearest place']
    for each_advisor in filtered_Advisors.advisorid.unique():
        for each_pro in properties.weightage:
            advisor_list=list(filtered_Advisors[filtered_Advisors.advisorid==each_advisor][each_pro])
            client_list=get_client_list(each_pro,client)
            similar_count=len(set(advisor_list)&set(client_list))
            if each_advisor in advisor_score:
                advisor_score[each_advisor]=advisor_score[each_advisor]+(properties.weightage[each_pro]*similar_count)
            else:
                advisor_score[each_advisor]=properties.weightage[each_pro]*similar_count
            if similar_count>0:
                if each_advisor in percentage:
                    percentage[each_advisor] = percentage[each_advisor] + ((similar_count/len(client_list))*20)
                    match_list[each_advisor] = match_list[each_advisor]+[each_pro]
                else:
                    percentage[each_advisor] = (similar_count/len(client_list))*20
                    match_list[each_advisor] = [each_pro]

    return advisor_score,percentage,match_list

if __name__ == '__main__':
    print('in main')
    app.run(host='0.0.0.0', port=81)