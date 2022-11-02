import sqlite3 as sql
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px 
import platform
import seaborn as sns
from matplotlib import font_manager, rc
plt.rcParams['axes.unicode_minus']=False
if platform.system()=='Darwin':
    rc('font',family='AppleGothic')
elif platform.system()=='Windows':
    path='C:/Windows/Fonts/malgun.ttf'
    font_name=font_manager.FontProperties(fname=path).get_name()
    rc('font',family=font_name)
else:
    print('Unknown system...')
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def team(request) :
    df=dbtodf("team_graph_app_all_position")
    hist_comparison(df)
    ace_comparison(df)
    ace_scatter(df)
    relative_record_all()
    relative_record_2021()
    clean_sheet()
    upset()
    home_away_all()
    home_away_2021()
    seasonRank()
    scorePercentage()
    roundRank18()
    roundRank05()
    return render(request, 'team_graph_app/Team.html')

def dbtodf(table_name):
    temp='select * from '+str(table_name)
    con=sql.connect('../db.sqlite3')
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

    plt.figure(figsize=(12,12))

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
    return plt.savefig('static/img/hist_comparison.png')

def ace_comparison(csv) :
    skywalkers=csv.loc[csv.구단=='현대캐피탈']
    jumbos=csv.loc[csv.구단=='대한항공']
    stars=csv.loc[csv.구단=='KB손해보험']
    won=csv.loc[csv.구단=='우리카드']
    vixtorm=csv.loc[csv.구단=='한국전력']
    okman=csv.loc[csv.구단=='OK금융그룹']
    bluefangs=csv.loc[csv.구단=='삼성화재']
    aces=pd.concat([skywalkers.head(1),jumbos.head(1),stars.head(1),won.head(1),vixtorm.head(1),okman.head(1),bluefangs.head(1)],axis=0)
    aces.sort_values(by='Rank',inplace=True)

    aces['공격 효율']=(aces['공격 성공']-aces['공격 상대 블락']-aces['공격 범실'])/aces['공격 시도']
    aces['서브 성공률']=aces['서브 성공']/aces['서브 시도']
    aces['세트 성공률']=aces['세트 성공']/aces['세트 시도']
    aces['블로킹 성공률']=aces['블로킹 성공']/aces['블로킹 시도']
    aces['리시브 효율']=(aces['리시브 정확']-aces['리시브 실패'])/aces['리시브 시도']
    aces['디그 성공률']=aces['디그 성공']/aces['디그 시도']
    
    aceName=aces.iloc[0:,1:3]
    aceStat=aces.iloc[0:,25:31]
    aceStat=aceName.join(aceStat)

    categories=['공격 효율','서브 성공률','세트 성공률','블로킹 성공률','리시브 효율','디그 성공률']
    categories=[*categories,categories[0]]

    stat1=aceStat.iloc[0,2:8]
    stat2=aceStat.iloc[1,2:8]
    stat3=aceStat.iloc[2,2:8]
    stat4=aceStat.iloc[3,2:8]
    stat5=aceStat.iloc[4,2:8]
    stat6=aceStat.iloc[5,2:8]
    stat7=aceStat.iloc[6,2:8]
    stat1=[*stat1,stat1[0]]
    stat2=[*stat2,stat2[0]]
    stat3=[*stat3,stat3[0]]
    stat4=[*stat4,stat4[0]]
    stat5=[*stat5,stat5[0]]
    stat6=[*stat6,stat6[0]]
    stat7=[*stat7,stat7[0]]

    label_loc=np.linspace(start=0, stop=2*np.pi, num=len(stat1))

    plt.figure(figsize=(6,6))
    ax=plt.subplot(polar=True)
    plt.xticks(label_loc,labels=categories,fontsize=10)
    plt.yticks([-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1])
    ax.plot(label_loc,stat1,label=str(aceStat.iloc[0,0]),linestyle='dotted',color='#F6AB16')
    ax.fill(label_loc,stat1,color='#F6AB16',alpha=0.2)
    ax.plot(label_loc,stat2,label=str(aceStat.iloc[1,0]),linestyle='dotted',color='#01295D')
    ax.fill(label_loc,stat2,color='#01295D',alpha=0.2)
    ax.plot(label_loc,stat3,label=str(aceStat.iloc[2,0]),linestyle='dotted',color='#E9470B')
    ax.fill(label_loc,stat3,color='#E9470B',alpha=0.2)
    ax.plot(label_loc,stat4,label=str(aceStat.iloc[3,0]),linestyle='dotted',color='#34A2DC')
    ax.fill(label_loc,stat4,color='#34A2DC',alpha=0.2)
    ax.plot(label_loc,stat5,label=str(aceStat.iloc[4,0]),linestyle='dotted',color='#ED1C24')
    ax.fill(label_loc,stat5,color='#ED1C24',alpha=0.2)
    ax.plot(label_loc,stat6,label=str(aceStat.iloc[5,0]),linestyle='--',color='#0082CB')
    ax.fill(label_loc,stat6,color='#0082CB',alpha=0.2)
    ax.plot(label_loc,stat7,label=str(aceStat.iloc[6,0]),linestyle='dotted',color='#007DBD')
    ax.fill(label_loc,stat7,color='#007DBD',alpha=0.2)
    ax.legend()
    return plt.savefig('static/img/ace_comparison.png')

def ace_scatter(csv) :
    skywalkers=csv.loc[csv.구단=='현대캐피탈']
    jumbos=csv.loc[csv.구단=='대한항공']
    stars=csv.loc[csv.구단=='KB손해보험']
    won=csv.loc[csv.구단=='우리카드']
    vixtorm=csv.loc[csv.구단=='한국전력']
    okman=csv.loc[csv.구단=='OK금융그룹']
    bluefangs=csv.loc[csv.구단=='삼성화재']
    aces=pd.concat([skywalkers.head(1),jumbos.head(1),stars.head(1),won.head(1),vixtorm.head(1),okman.head(1),bluefangs.head(1)],axis=0)
    aces.sort_values(by='Rank',inplace=True)

    aces['공격 효율']=(aces['공격 성공']-aces['공격 상대 블락']-aces['공격 범실'])/aces['공격 시도']
    aces['서브 성공률']=aces['서브 성공']/aces['서브 시도']
    aces['세트 성공률']=aces['세트 성공']/aces['세트 시도']
    aces['블로킹 성공률']=aces['블로킹 성공']/aces['블로킹 시도']
    aces['리시브 효율']=(aces['리시브 정확']-aces['리시브 실패'])/aces['리시브 시도']
    aces['디그 성공률']=aces['디그 성공']/aces['디그 시도']

    attackParam_y=np.array(aces.iloc[:,8])
    attackParam_x=np.array(aces.iloc[:,25])*100

    serveParam_y=np.array(aces.iloc[:,12])
    serveParam_x=np.array(aces.iloc[:,26])*100

    setParam_y=np.array(aces.iloc[:,15])
    setParam_x=np.array(aces.iloc[:,27])*100

    blockingParam_y=np.array(aces.iloc[:,17])
    blockingParam_x=np.array(aces.iloc[:,28])*100

    receiveParam_y=np.array(aces.iloc[:,20])
    receiveParam_x=np.array(aces.iloc[:,29])

    digParam_y=np.array(aces.iloc[:,23])
    digParam_x=np.array(aces.iloc[:,30])*100

    yParam=[0,0,0,0,0,0,0]
    colorParam=['#F6AB16','#01295D','#E9470B','#34A2DC','#ED1C24','#1D1D1B','#007DBD']

    plt.figure(figsize=(18,3))
    plt.subplot(331)
    plt.scatter(attackParam_x,yParam,c=colorParam,s=attackParam_y,alpha=0.7)
    plt.gca().axes.yaxis.set_visible(False)
    plt.title('공격 효율')
    plt.subplot(332)
    plt.scatter(serveParam_x,yParam,c=colorParam,s=serveParam_y,alpha=0.7)
    plt.gca().axes.yaxis.set_visible(False)
    plt.title('서브 성공률')
    plt.subplot(333)
    plt.scatter(setParam_x,yParam,c=colorParam,s=setParam_y,alpha=0.7)
    plt.gca().axes.yaxis.set_visible(False)
    plt.title('세트 성공률')
    plt.subplot(337)
    plt.scatter(blockingParam_x,yParam,c=colorParam,s=blockingParam_y,alpha=0.7)
    plt.gca().axes.yaxis.set_visible(False)
    plt.title('블로킹 성공률')
    plt.subplot(338)
    plt.scatter(receiveParam_x,yParam,c=colorParam,s=receiveParam_y,alpha=0.7)
    plt.gca().axes.yaxis.set_visible(False)
    plt.title('리시브 효율')
    plt.subplot(339)
    plt.scatter(digParam_x,yParam,c=colorParam,s=digParam_y,alpha=0.7)
    plt.gca().axes.yaxis.set_visible(False)
    plt.title('디그 성공률')
    return plt.savefig('static/img/ace_scatter.png')
    
def relative_record_all():
    df = dbtodf('team_graph_app_relative_record_all')
    fig = px.bar(df, x="상대팀", y="경기수",  color="경기결과", text = '경기수')
    return fig.write_image('static/img/relative_record_all.png')

def relative_record_2021():
    df = dbtodf('team_graph_app_relative_record_2021')
    fig = px.bar(df, x="상대팀", y="경기수",  color="경기결과", text = '경기수')
    return fig.write_image('static/img/relative_record_2021.png')

def clean_sheet():
    df = dbtodf('team_graph_app_clean_sheet')
    fig = px.bar(df, x="세트 스코어", y='합계', color="상대팀", text="상대팀")
    return fig.write_image('static/img/clean_sheet.png') 

def upset():
    df = dbtodf('team_graph_app_upset')
    fig = px.bar(df, x="세트 스코어", y='합계', color="상대팀", text="상대팀")
    return fig.write_image('static/img/upset.png')

def home_away_all():
    df = dbtodf('team_graph_app_home_away_all')
    fig = px.histogram(df, x="홈/어웨이", y="경기수",
                 color='경기결과', barmode='group', histfunc = 'sum', text_auto=True,
                 height=400)
    fig.write_image('static/img/home_away_all.png')
    
def home_away_2021():
    df = dbtodf('team_graph_app_home_away_2021')
    fig = px.histogram(df, x="홈/어웨이", y="경기수",
                 color='경기결과', barmode='group', histfunc = 'sum', text_auto=True,
                 height=400)
    fig.write_image('static/img/home_away_2021.png')

def seasonRank():
    df=dbtodf('team_graph_app_seasonrank')

    plt.figure(figsize=(20,5))
    plt.plot(df['시즌'], df['순위'],label='HYUNDAI',marker='o')

    plt.gca().invert_yaxis()   #y축 반대로
    plt.xlabel('Season League')         
    plt.ylabel('Rank')
    # plt.title('시즌 순위',fontsize=25)
    plt.legend()
    return plt.savefig('static/img/seasonRank.png')  

def scorePercentage():
    df=dbtodf('team_graph_app_score_percentage')
    plt.figure(figsize=(18,5))
    category=['공격','블로킹','서브']
    colors=['pink','gold','cyan']

    plt.subplot(1,4,1)
    plt.pie(df['2018-19'],labels=category,autopct='%.1f%%',colors=colors,shadow=True)
    plt.title("2018-19 득점 비율",fontsize=15)

    plt.subplot(1,4,2)
    plt.pie(df['2019-20'],labels=category,autopct='%.1f%%',colors=colors,shadow=True)
    plt.title("2019-20 득점 비율",fontsize=15)

    plt.subplot(1,4,3)
    plt.pie(df['2020-21'],labels=category,autopct='%.1f%%',colors=colors,shadow=True)
    plt.title("2020-21 득점 비율",fontsize=15)

    plt.subplot(1,4,4)
    plt.pie(df['2021-22'],labels=category,autopct='%.1f%%',colors=colors,shadow=True)
    plt.title("2021-22 득점 비율",fontsize=15)
    return plt.savefig('static/img/score_percentage.png')

def roundRank18():
    df=dbtodf('team_graph_app_roundrank_count_18_22')
    df=df.set_index('랭크')
    plt.subplot(1,1,1)
    sns.heatmap(df,annot=True,fmt='d',cmap='Reds')
    # plt.title('라운드 별 순위 빈도(2018~2022)', fontsize=20)
    plt.xlabel('Round', fontsize=14)
    plt.ylabel('Rank', fontsize=14)

    return plt.savefig('static/img/roundRank18_22.png')

def roundRank05():
    df=dbtodf('team_graph_app_roundrank_count_05_18')
    df=df.set_index('랭크')
    plt.subplot(1,1,1)
    sns.heatmap(df,annot=True,fmt='d',cmap='Reds')
    # plt.title('라운드 별 순위 빈도(2005~2018)', fontsize=20)
    plt.xlabel('Round', fontsize=14)
    plt.ylabel('Rank', fontsize=14)

    return plt.savefig('static/img/roundRank05_18.png')