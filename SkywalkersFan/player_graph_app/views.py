from http.client import HTTPResponse
import sqlite3 as sql
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse

import pandas as pd

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
 
from math import pi
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

# 한글 폰트 사용을 위해서 세팅
from matplotlib import font_manager, rc
font_path = "C:/Windows/Fonts/NGULIM.TTF"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

# Create your views here.
def player(request) :
    return HttpResponse('player page')

def dbtodf(table_name):
    temp='select * from '+str(table_name)
    con=sql.connect('./SkywalkersFan/db.sqlite3')
    cur=con.cursor()
    query=cur.execute(temp)
    cols=[column[0] for column in query.description]
    result=pd.DataFrame.from_records(data=query.fetchall(),columns=cols)
    con.close()
    return result




# 그래프 그리는 함수들 만들기


# 레이더차트
def Player_RaderChart_One(csv,name):

    # 불러온 csv파일에서 [player_name	공격 성공률	공격 효율	세트 성공률	서브 성공률	블로킹 성공률	리시브 효율	디그 성공률] 컬럼만 가져옴
    df = csv.iloc[:,[0,-7,-3,-5,-6,-4,-2,-1]]

    # 기준점 생성 
    # 이 기준점보다 바깥에 있으면 잘하는 편이라는걸 표현하기 위해 기준점 생성
    # 순서대로 공격 성공률, 공격 효율, 세트 성공률, 서브 성공률, 블로킹 성공률, 리시브 효율, 디그 성공률 
    standard = [0.2,0.2,0.3,0.1,0.15,0.15,0.15,0.2]

    # 레이더 차트 그리기
    labels = df.columns[1:]
    num_labels = len(labels)
        
    angles = [x/float(num_labels)*(2*pi) for x in range(num_labels)] ## 각 등분점
    angles += angles[:1] ## 시작점으로 다시 돌아와야하므로 시작점 추가
        
    my_palette = plt.cm.get_cmap("Set2", len(df.index))
    
    fig = plt.figure(figsize=(7,7))
    fig.set_facecolor('white')
    
    dt = df.loc[(df["player_name"]==name)]

    data = dt.drop(columns = ["player_name"]).iloc[0].tolist()
    data += data[:1]
        
    ax = plt.subplot(1,1,1, polar=True)
    ax.set_theta_offset(pi / 2) ## 시작점
    ax.set_theta_direction(-1) ## 그려지는 방향 시계방향
        
    plt.xticks(angles[:-1], labels, fontsize=13) ## x축 눈금 라벨
    ax.tick_params(axis='x', which='major', pad=15) ## x축과 눈금 사이에 여백을 준다.
    
    ax.set_rlabel_position(0) ## y축 각도 설정(degree 단위)
    plt.yticks([0,0.2,0.4,0.6,0.8,1.0],['0','0.2','0.4','0.6','0.8','1'], fontsize=15) ## y축 눈금 설정
    plt.ylim(-0.75,1)
        
    # 선수 데이터 그리기
    ax.plot(angles, data, color="blue", linewidth=2, linestyle='solid') ## 레이더 차트 출력
    #ax.fill(angles, data, color="skyblue", alpha=0.4) ## 도형 안쪽에 색을 채워준다.

    # 기준점 그리기
    ax.plot(angles, standard, color="red", linewidth=2, linestyle='solid') ## 레이더 차트 출력
    #ax.fill(angles, standard, color="pink", alpha=0.4) ## 도형 안쪽에 색을 채워준다.


    for g in ax.yaxis.get_gridlines(): ## grid line 
        g.get_path()._interpolation_steps = len(labels)
        
    spine = Spine(axes=ax,
            spine_type='circle',
            path=Path.unit_regular_polygon(len(labels)))
        
    ## Axes의 중심과 반지름을 맞춰준다.
    spine.set_transform(Affine2D().scale(.5).translate(.5, .5)+ax.transAxes)
                
    ax.spines = {'polar':spine} ## frame의 모양을 원에서 폴리곤으로 바꿔줘야한다.

    plt.title("21-22시즌 기록"+" ["+ name +"]",fontsize=25) 
    ax.legend([name,"standard"],fontsize = 15,loc = (0,0.1))


# 추세선 그래프 
def Player_RecordChart_One(csv,name):
    # 선수별 최근 5년(데이터가 있다면) 분야별 추세선 그래프
    # for player in csv["player_name"].unique().tolist()[:] :
        dt = csv.loc[(csv["player_name"]==name)]

        plt.figure(figsize=(9,14),facecolor = "white")

        plt.subplot(4,2,1)
        plt.plot(dt.loc[:,"season"],dt.loc[:,"score"],"--or")
        plt.title("득점", fontsize=15)
        plt.xlabel("시즌")

        plt.subplot(4,2,2)
        plt.plot(dt.loc[:,"season"],dt.loc[:,"attack_succes_percent"],"--or")
        plt.title("공격 성공률", fontsize=15)
        plt.xlabel("시즌")
        # plt.ylabel("공격 성공률")

        plt.subplot(4,2,3)
        plt.plot(dt.loc[:,"season"],dt.loc[:,"bloocking_avg"],"--or")
        plt.title("블로킹 AVG(set)", fontsize=15)
        plt.xlabel("시즌")
        # plt.ylabel("블로킹 AVG(set)")

        plt.subplot(4,2,4)
        plt.plot(dt.loc[:,"season"],dt.loc[:,"serve_avg"],"--or")
        plt.title("서브 AVG(set)", fontsize=15)
        plt.xlabel("시즌")
        # plt.ylabel("서브 AVG(set)")

        plt.subplot(4,2,5)
        plt.plot(dt.loc[:,"season"],dt.loc[:,"set_avg"],"--or")
        plt.title("세트 AVG(set)", fontsize=15)
        plt.xlabel("시즌")
        # plt.ylabel("세트 AVG(set)")
        
        plt.subplot(4,2,6)
        plt.plot(dt.loc[:,"season"],dt.loc[:,"reveive_eff"],"--or")
        plt.title("리시브 효율", fontsize=15)
        plt.xlabel("시즌")
        # plt.ylabel("리시브 효율")
        
        plt.subplot(4,2,7)
        plt.plot(dt.loc[:,"season"],dt.loc[:,"dig_avg"],"--or")
        plt.title("디그 AVG(set)", fontsize=15)
        plt.xlabel("시즌")
        # plt.ylabel("디그 AVG(set)")

        plt.subplot(4,2,8)
        plt.plot(dt.loc[:,"season"],dt.loc[:,"mistake"],"--or")
        plt.title("범실", fontsize=15)
        plt.xlabel("시즌")


        # subplot 전체 제목 설정
        plt.suptitle(name+"선수 시즌별 기록",fontsize=25)

        plt.subplots_adjust(hspace=0.7,wspace=0.3)
        plt.show()

