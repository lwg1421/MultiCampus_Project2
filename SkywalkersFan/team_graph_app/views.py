import sqlite3 as sql
import pandas as pd
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def team(request) :
    return render(request, 'team_graph_app/.test.html')

def dbtodf(table_name):
    temp='select * from '+str(table_name)
    con=sql.connect('./SkywalkersFan/db.sqlite3')
    cur=con.cursor()
    query=cur.execute(temp)
    cols=[column[0] for column in query.description]
    result=pd.DataFrame.from_records(data=query.fetchall(),columns=cols)
    con.close()
    return result

def hist_comparison(csv) :
    skywalkers=csv.loc[csv.구단=='현대캐피탈']
    jumbos=csv.loc[csv.구단=='대한항공']
    stars=csv.loc[csv.구단=='KB손해보험']
    won=csv.loc[csv.구단=='우리카드']
    vixtorm=csv.loc[csv.구단=='한국전력']
    okman=csv.loc[csv.구단=='OK금융그룹']
    bluefangs=csv.loc[csv.구단=='삼성화재']
    
    colorParam=['#F6AB16','#01295D','#E9470B','#34A2DC','#ED1C24','#1D1D1B','#007DBD']

    plt.figure(figsize=(8,8))

    plt.subplot(241)
    plt.hist(skywalkers['톱랭킹포인트'],bins=6,color=colorParam[5],label='현대캐피탈 22명')
    plt.ylim([0,15])
    plt.title('현대캐피탈 22명')
    plt.subplot(242)
    plt.hist(jumbos['톱랭킹포인트'],bins=6,color=colorParam[6],label='대한항공 19명')
    plt.ylim([0,15])
    plt.title('대한항공 19명')
    plt.subplot(243)
    plt.hist(stars['톱랭킹포인트'],bins=6,color=colorParam[0],label='KB손해보험 20명')
    plt.ylim([0,15])
    plt.title('KB손해보험 20명')
    plt.subplot(244)
    plt.hist(won['톱랭킹포인트'],bins=6,color=colorParam[3],label='우리카드 20명')
    plt.ylim([0,15])
    plt.title('우리카드 20명')
    plt.subplot(245)
    plt.hist(vixtorm['톱랭킹포인트'],bins=6,color=colorParam[4],label='한국전력 18명')
    plt.ylim([0,15])
    plt.title('한국전력 18명')
    plt.subplot(246)
    plt.hist(okman['톱랭킹포인트'],bins=6,color=colorParam[2],label='OK금융그룹 19명')
    plt.ylim([0,15])
    plt.title('OK금융그룹 19명')
    plt.subplot(247)
    plt.hist(bluefangs['톱랭킹포인트'],bins=6,color=colorParam[1],label='삼성화재 18명')
    plt.ylim([0,15])
    plt.title('삼성화재 18명')
    plt.show()