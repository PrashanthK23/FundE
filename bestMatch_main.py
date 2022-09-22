# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from config import properties
import pandas as pd
import numpy as np
import collections
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
def getClientdata():
    return pd.read_csv('./data/client.csv')


def getAdvisors():
    return pd.read_csv('./data/advisor.csv')


def filteredAdvisors(client, df_advisors):
    filter_columns=properties.filters
    if client.sex.iloc[0]=='D':
        filter_columns.remove('sex')
    for each_column in filter_columns:
        filtered_Advisors=df_advisors[df_advisors[each_column]==client[each_column].iloc[0]]
    return filtered_Advisors


def rankAdvisors(client, filtered_Advisors):
    advisor_score={}
    if client.area.iloc[0]=='Yes':
        cli_lat =client.lat.iloc[0]
        cli_lon =client.lon.iloc[0]
        for ind,each_advisor in filtered_Advisors[['advisorid','lat','lon']].drop_duplicates().iterrows():
            adv_lat=each_advisor.lat
            adv_lon=each_advisor.lat
            distance=np.sqrt(((adv_lat-cli_lat)**2)+((adv_lon-cli_lon)**2))
            advisorid=each_advisor.advisorid
            advisor_score[advisorid]=distance
        mean=sum(advisor_score.values()) / len(advisor_score)
        for each_key in advisor_score:
            advisor_score[each_key]=10-(advisor_score[each_key]/mean)
    for each_advisor in filtered_Advisors.advisorid.unique():
        for each_pro in properties.weightage:
            if client[each_pro].iloc[0] in list(filtered_Advisors[filtered_Advisors.advisorid==each_advisor][each_pro]):
                if each_advisor in advisor_score:
                    advisor_score[each_advisor]=advisor_score[each_advisor]+properties.weightage[each_pro]


    return collections.OrderedDict(advisor_score)

if __name__ == '__main__':
    df_clients=getClientdata()
    df_advisors=getAdvisors()
    while 1==1:
        clientid=int(input('enter the clientid:'))
        if clientid=='-1':
            break
        filtered_Advisors=filteredAdvisors(df_clients[df_clients['clientid']==clientid],df_advisors)
        advisor_score=rankAdvisors(df_clients[df_clients['clientid']==clientid],filtered_Advisors)
        print(advisor_score)
