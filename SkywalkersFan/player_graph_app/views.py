import sqlite3 as sql
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import plotly.express as px 
import platform
from django.shortcuts import render
from django.http import HttpResponse
from math import pi
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

# 현재 현대캐피탈 선수명단
h_cap_lst = ['김명관', '김선호', '김형진', '문성민', '박경민', '박상하', '박주형', '박준혁', '송원근', '송준호', '여오현', '이원중', '이준승', '전광인', '차영석', '최민호', '최은석', '펠리페', '함형진', '허수봉', '홍동선', '히메네즈']

# 한글 폰트 사용을 위해서 세팅
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


# Create your views here.
def player(request) :
    libero()
    setter()
    center()
    left()
    right()
    for name in h_cap_lst:
        Player_RaderChart_One(name)
        Player_RecordChart_One(name)    
    return render(request, 'player_graph_app/player_list_test.html')

# 선수 이름을 주고받고 싶음
# 선수 클릭할 때 파일 있는지 확인해서 함수 실행되도록
# 선수 클릭할 때 매개변수로 이름을 받아서 그래프를 그리기
def get_player(request, word) :
    context=make_context(word)
    return render(request,'player_graph_app/player_info_test.html', {'context':context})

def make_context(word) :
    df=dbtodf('player_graph_app_player_data')
    temp=df.T.to_dict()
    for i in range(0,22):
        if temp[i]['player_name']==word:
            context=temp[i]
            break
    return context

def dbtodf(table_name):
    temp='select * from '+str(table_name)
    con=sql.connect('../db.sqlite3')
    cur=con.cursor()
    query=cur.execute(temp)
    cols=[column[0] for column in query.description]
    result=pd.DataFrame.from_records(data=query.fetchall(),columns=cols)
    con.close()
    return result


# 그래프 그리는 함수들 만들기


# 레이더차트
def Player_RaderChart_One(name):

    df = dbtodf('player_graph_app_player_data')
    # 불러온 csv파일에서 [player_name	공격 성공률	공격 효율	세트 성공률	서브 성공률	블로킹 성공률	리시브 효율	디그 성공률] 컬럼만 가져옴
    df = df.iloc[:,[0,-7,-3,-5,-6,-4,-2,-1]]

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

    # plt.title("21-22시즌 기록"+" ["+ name +"]",fontsize=25) 
    ax.legend([name,"standard"],fontsize = 15,loc = (0,0.1))
    plt.savefig('static/img/'+name+'_레이더.png')


# 추세선 그래프 
def Player_RecordChart_One(name):
    # 선수별 최근 5년(데이터가 있다면) 분야별 추세선 그래프
    # for player in csv["player_name"].unique().tolist()[:] :
        df = dbtodf('player_graph_app_player_season_data')
        dt = df.loc[(df["player_name"]==name)]

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
        # plt.suptitle(name+"선수 시즌별 기록",fontsize=25)

        plt.subplots_adjust(hspace=0.7,wspace=0.3)
        plt.savefig('static/img/'+name+'_추세선.png')
        

def libero():
    
    df = dbtodf("player_graph_app_libero_player")
    libero = df
    libero["공격 성공률"] = libero["공격 성공"]/libero["공격 시도"]
    libero["공격 효율"] = (libero["공격 성공"] - libero["공격 상대 블락"] - libero["공격 범실"])/libero["공격 시도"]
    libero["서브 성공률"] = libero["서브 성공"]/libero["서브 시도"]
    libero["세트 성공률"] = libero["세트 성공"]/libero["세트 시도"]
    libero["블로킹 성공률"] = libero["블로킹 성공"]/libero["블로킹 시도"]
    libero["리시브 효율"] = (libero["리시브 정확"]-libero["리시브 실패"])/libero["리시브 시도"]
    libero["디그 성공률"] = libero["디그 성공"]/libero["디그 시도"]

    top_libero = libero.iloc[:,[1,2,-1,-3,-4]]
    top_libero = top_libero.fillna(0)
    # top_libero.iloc[15,3]= 0

    # 2021 KOVO 리베로 선수들 중 디그 성공률로 순위를 표현한 데이터프레임
    top_libero_dig = top_libero.sort_values(by = "디그 성공률",ascending = False)
    top_libero_dig["순위"] = np.arange(1,len(top_libero_dig)+1)
    top_libero_dig.set_index("순위",inplace = True)

    # 2021 KOVO 리베로 선수들 중 블로킹 성공률로 순위를 표현한 데이터프레임
    top_libero_blocking = top_libero.sort_values(by = "블로킹 성공률",ascending = False)
    top_libero_blocking["순위"] = np.arange(1,len(top_libero_blocking)+1)
    top_libero_blocking.set_index("순위",inplace = True)

    # 2021 KOVO 리베로 선수들 중 세트 성공률로 순위를 표현한 데이터프레임
    top_libero_set = top_libero.sort_values(by = "세트 성공률",ascending = False)
    top_libero_set["순위"] = np.arange(1,len(top_libero_set)+1)
    top_libero_set.set_index("순위",inplace = True)

    # 디그 성공률로 순위 매긴 데이터프레임에서 디그성공률 값만 가져와 리스트로 생성
    # 추후 디그 성공률 산점도에 x축으로 넣어줄 값임
    dig_suc = top_libero_dig["디그 성공률"].tolist()
    blocking_suc = top_libero_dig["블로킹 성공률"].tolist()
    set_suc = top_libero_dig["세트 성공률"].tolist()

    # 한글 폰트 깨짐 방지 
    # rc('font', family='AppleGothic') 
    # plt.rcParams['axes.unicode_minus'] = False

    libero.set_index('Rank', inplace=True)
    libero_lst = libero['선수명'].tolist()     # 반복문 리스트 내 데이터 비교를 위한 리스트화 작업. 

    for i, player in enumerate(h_cap_lst):

        if player in libero_lst:

            # 그래프 작성하려면 y축 값도 있긴 해야해서 y값 리스트 생성
            y_dig = np.zeros(len(dig_suc)) + 1.8

            # y축 삭제하기위해 ax 설정
            ax = plt.gca()

            # 모든 선수 점 찍기
            plt.scatter(dig_suc,y_dig,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_libero_dig.loc[top_libero_dig["선수명"]==player,"디그 성공률"],1.8,s=150,c ="r")

            plt.ylim()
            plt.xlabel('디그 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/libero_'+str(player)+'_dig_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            # plt.axis("off")

        else:
            pass

    for i, player in enumerate(h_cap_lst):

        if player in libero_lst:

            y_set = np.zeros(len(set_suc))+0
            ax = plt.gca()
            plt.scatter(set_suc,y_set,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_libero_set.loc[top_libero_set["선수명"]==player,"세트 성공률"],0,s=150,c ="r")

            plt.ylim()
            plt.xlabel('세트 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/libero_'+str(player)+'_set_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            # plt.axis("off")

        else :
            pass        

def setter():
    
    df = dbtodf("player_graph_app_setter_player")
    setter = df    
    setter["공격 성공률"] = setter["공격 성공"]/setter["공격 시도"]
    setter["공격 효율"] = (setter["공격 성공"] - setter["공격 상대 블락"] - setter["공격 범실"])/setter["공격 시도"]
    setter["서브 성공률"] = setter["서브 성공"]/setter["서브 시도"]
    setter["세트 성공률"] = setter["세트 성공"]/setter["세트 시도"]
    setter["블로킹 성공률"] = setter["블로킹 성공"]/setter["블로킹 시도"]
    setter["리시브 효율"] = (setter["리시브 정확"]-setter["리시브 실패"])/setter["리시브 시도"]
    setter["디그 성공률"] = setter["디그 성공"]/setter["디그 시도"]

    top_setter = setter.iloc[:,[1,2,-7,-6,-5,-4,-3,-1]]
    top_setter = top_setter.fillna(0)
    # top_setter.iloc[15,3]= 0

    # 2021 KOVO 세터 선수들 중 디그 성공률로 순위를 표현한 데이터프레임
    top_setter_dig = top_setter.sort_values(by = "디그 성공률",ascending = False)
    top_setter_dig["순위"] = np.arange(1,len(top_setter_dig)+1)
    top_setter_dig.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 블로킹 성공률로 순위를 표현한 데이터프레임
    top_setter_blocking = top_setter.sort_values(by = "블로킹 성공률",ascending = False)
    top_setter_blocking["순위"] = np.arange(1,len(top_setter_blocking)+1)
    top_setter_blocking.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 세트 성공률로 순위를 표현한 데이터프레임
    top_setter_set = top_setter.sort_values(by = "세트 성공률",ascending = False)
    top_setter_set["순위"] = np.arange(1,len(top_setter_set)+1)
    top_setter_set.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 공격 성공률로 순위를 표현한 데이터프레임
    top_setter_at = top_setter.sort_values(by = "공격 성공률",ascending = False)
    top_setter_at["순위"] = np.arange(1,len(top_setter_at)+1)
    top_setter_at.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 공격 효율로 순위를 표현한 데이터프레임
    top_setter_at_e = top_setter.sort_values(by = "공격 효율",ascending = False)
    top_setter_at_e["순위"] = np.arange(1,len(top_setter_at_e)+1)
    top_setter_at_e.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 서브 성공률로 순위를 표현한 데이터프레임
    top_setter_serve = top_setter.sort_values(by = "서브 성공률",ascending = False)
    top_setter_serve["순위"] = np.arange(1,len(top_setter_serve)+1)
    top_setter_serve.set_index("순위",inplace = True)


    # 디그 성공률로 순위 매긴 데이터프레임에서 디그성공률 값만 가져와 리스트로 생성
    # 추후 디그 성공률 산점도에 x축으로 넣어줄 값임
    dig_suc = top_setter_dig["디그 성공률"].tolist()
    blocking_suc = top_setter_blocking["블로킹 성공률"].tolist()
    set_suc = top_setter_set["세트 성공률"].tolist()
    at_suc = top_setter_at['공격 성공률'].tolist()
    at_e = top_setter_at_e['공격 효율'].tolist()
    serve_suc = top_setter_serve['서브 성공률'].tolist()

    # 한글 폰트 깨짐 방지 
    # rc('font', family='AppleGothic') 
    # plt.rcParams['axes.unicode_minus'] = False

    setter.set_index('Rank', inplace=True)
    setter_lst = setter['선수명'].tolist()     # 반복문 리스트 내 데이터 비교를 위한 리스트화 작업. 

    for i, player in enumerate(h_cap_lst):

        if player in setter_lst:

            # 그래프 작성하려면 y축 값도 있긴 해야해서 y값 리스트 생성
            y_dig = np.zeros(len(dig_suc)) + 1.5

            # y축 삭제하기위해 ax 설정
            ax = plt.gca()

            # 모든 선수 점 찍기
            plt.scatter(dig_suc,y_dig,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_setter_dig.loc[top_setter_dig["선수명"]==player,"디그 성공률"],1.5,s=150,c ="r")

            plt.ylim()
            plt.xlabel('디그 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/setter_'+str(player)+'_dig_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else:
            pass

    for i, player in enumerate(h_cap_lst):

        if player in setter_lst:

            y_blocking = np.zeros(len(blocking_suc)) + 0.7
            ax = plt.gca()
            plt.scatter(blocking_suc,y_blocking,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_setter_blocking.loc[top_setter_blocking["선수명"]==player,"블로킹 성공률"],0.7,s=150,c ="r")

            plt.ylim()
            plt.xlabel('블로킹 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/setter_'+str(player)+'_blocking_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else:
             pass

    for i, player in enumerate(h_cap_lst):

        if player in setter_lst:

            y_set = np.zeros(len(set_suc))
            ax = plt.gca()
            plt.scatter(set_suc,y_set,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_setter_set.loc[top_setter_set["선수명"]==player,"세트 성공률"],0,s=150,c ="r")

            plt.ylim()
            plt.xlabel('세트 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/setter_'+str(player)+'_set_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass

    for i, player in enumerate(h_cap_lst):

        if player in setter_lst:

            y_at = np.zeros(len(at_suc))
            ax = plt.gca()
            plt.scatter(at_suc,y_at,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_setter_at.loc[top_setter_at["선수명"]==player,"공격 성공률"],0,s=150,c ="r")

            plt.ylim()
            plt.xlabel('공격 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/setter_'+str(player)+'_at_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass    

    for i, player in enumerate(h_cap_lst):

        if player in setter_lst:

            y_at_e = np.zeros(len(at_e))
            ax = plt.gca()
            plt.scatter(at_e,y_at_e,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_setter_at_e.loc[top_setter_at_e["선수명"]==player,"공격 효율"],0,s=150,c ="r")

            plt.ylim()
            plt.xlabel('공격 효율')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/setter_'+str(player)+'_at_e.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass     

    for i, player in enumerate(h_cap_lst):

        if player in setter_lst:

            y_serve = np.zeros(len(serve_suc)) + 0.35
            ax = plt.gca()
            plt.scatter(serve_suc,y_serve,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_setter_serve.loc[top_setter_serve["선수명"]==player,"서브 성공률"],0.35,s=150,c ="r")

            plt.ylim()
            plt.xlabel('서브 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/setter_'+str(player)+'_serve_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass    

def center():
    
    df = dbtodf("player_graph_app_center_player")
    center = df  
    center["공격 성공률"] = center["공격 성공"]/center["공격 시도"]
    center["공격 효율"] = (center["공격 성공"] - center["공격 상대 블락"] - center["공격 범실"])/center["공격 시도"]
    center["서브 성공률"] = center["서브 성공"]/center["서브 시도"]
    center["세트 성공률"] = center["세트 성공"]/center["세트 시도"]
    center["블로킹 성공률"] = center["블로킹 성공"]/center["블로킹 시도"]
    center["리시브 효율"] = (center["리시브 정확"]-center["리시브 실패"])/center["리시브 시도"]
    center["디그 성공률"] = center["디그 성공"]/center["디그 시도"]

    top_center = center.iloc[:,[1,2,-7,-6,-5,-4,-3,-2,-1]]
    top_center = top_center.fillna(0)
    # top_center.iloc[15,3]= 0

    # 2021 KOVO 세터 선수들 중 디그 성공률로 순위를 표현한 데이터프레임
    top_center_dig = top_center.sort_values(by = "디그 성공률",ascending = False)
    top_center_dig["순위"] = np.arange(1,len(top_center_dig)+1)
    top_center_dig.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 블로킹 성공률로 순위를 표현한 데이터프레임
    top_center_blocking = top_center.sort_values(by = "블로킹 성공률",ascending = False)
    top_center_blocking["순위"] = np.arange(1,len(top_center_blocking)+1)
    top_center_blocking.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 세트 성공률로 순위를 표현한 데이터프레임
    top_center_set = top_center.sort_values(by = "세트 성공률",ascending = False)
    top_center_set["순위"] = np.arange(1,len(top_center_set)+1)
    top_center_set.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 공격 성공률로 순위를 표현한 데이터프레임
    top_center_at = top_center.sort_values(by = "공격 성공률",ascending = False)
    top_center_at["순위"] = np.arange(1,len(top_center_at)+1)
    top_center_at.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 공격 효율로 순위를 표현한 데이터프레임
    top_center_at_e = top_center.sort_values(by = "공격 효율",ascending = False)
    top_center_at_e["순위"] = np.arange(1,len(top_center_at_e)+1)
    top_center_at_e.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 서브 성공률로 순위를 표현한 데이터프레임
    top_center_serve = top_center.sort_values(by = "서브 성공률",ascending = False)
    top_center_serve["순위"] = np.arange(1,len(top_center_serve)+1)
    top_center_serve.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 리시브 효율로 순위를 표현한 데이터프레임
    top_center_receive_e = top_center.sort_values(by = "리시브 효율",ascending = False)
    top_center_receive_e["순위"] = np.arange(1,len(top_center_receive_e)+1)
    top_center_receive_e.set_index("순위",inplace = True)


    # 디그 성공률로 순위 매긴 데이터프레임에서 디그성공률 값만 가져와 리스트로 생성
    # 추후 디그 성공률 산점도에 x축으로 넣어줄 값임
    dig_suc = top_center_dig["디그 성공률"].tolist()
    blocking_suc = top_center_blocking["블로킹 성공률"].tolist()
    set_suc = top_center_set["세트 성공률"].tolist()
    at_suc = top_center_at['공격 성공률'].tolist()
    at_e = top_center_at_e['공격 효율'].tolist()
    serve_suc = top_center_serve['서브 성공률'].tolist()
    receive_e = top_center_receive_e['리시브 효율'].tolist()

    # 한글 폰트 깨짐 방지 
    # rc('font', family='AppleGothic') 
    # plt.rcParams['axes.unicode_minus'] = False

    center.set_index('Rank', inplace=True)
    center_lst = center['선수명'].tolist()     # 반복문 리스트 내 데이터 비교를 위한 리스트화 작업. 

    for i, player in enumerate(h_cap_lst):

        if player in center_lst:

            # 그래프 작성하려면 y축 값도 있긴 해야해서 y값 리스트 생성
            y_dig = np.zeros(len(dig_suc)) + 0.45

            # y축 삭제하기위해 ax 설정
            ax = plt.gca()

            # 모든 선수 점 찍기
            plt.scatter(dig_suc,y_dig,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_center_dig.loc[top_center_dig["선수명"]==player,"디그 성공률"],0.45,s=150,c ="r")

            plt.ylim()
            plt.xlabel('디그 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/center_'+str(player)+'_dig_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else:
            pass

    for i, player in enumerate(h_cap_lst):

        if player in center_lst:

            y_blocking = np.zeros(len(blocking_suc)) + 0.2
            ax = plt.gca()
            plt.scatter(blocking_suc,y_blocking,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_center_blocking.loc[top_center_blocking["선수명"]==player,"블로킹 성공률"],0.2,s=150,c ="r")

            plt.ylim()
            plt.xlabel('블로킹 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/center_'+str(player)+'_blocking_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else:
             pass

    for i, player in enumerate(h_cap_lst):

        if player in center_lst:

            y_set = np.zeros(len(set_suc)) + 0.7
            ax = plt.gca()
            plt.scatter(set_suc,y_set,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_center_set.loc[top_center_set["선수명"]==player,"세트 성공률"],0.7,s=150,c ="r")

            plt.ylim()
            plt.xlabel('세트 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/center_'+str(player)+'_set_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass

    for i, player in enumerate(h_cap_lst):

        if player in center_lst:

            y_at = np.zeros(len(at_suc)) + 0.3
            ax = plt.gca()
            plt.scatter(at_suc,y_at,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_center_at.loc[top_center_at["선수명"]==player,"공격 성공률"],0.3,s=150,c ="r")

            plt.ylim()
            plt.xlabel('공격 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/center_'+str(player)+'_at_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass    

    for i, player in enumerate(h_cap_lst):

        if player in center_lst:

            y_at_e = np.zeros(len(at_e)) + 0.35
            ax = plt.gca()
            plt.scatter(at_e,y_at_e,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_center_at_e.loc[top_center_at_e["선수명"]==player,"공격 효율"],0.35,s=150,c ="r")

            plt.ylim()
            plt.xlabel('공격 효율')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/center_'+str(player)+'_at_e.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass     

    for i, player in enumerate(h_cap_lst):

        if player in center_lst:

            y_serve = np.zeros(len(serve_suc)) + 0.15
            ax = plt.gca()
            plt.scatter(serve_suc,y_serve,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_center_serve.loc[top_center_serve["선수명"]==player,"서브 성공률"],0.15,s=150,c ="r")

            plt.ylim()
            plt.xlabel('서브 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/center_'+str(player)+'_serve_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass

    for i, player in enumerate(h_cap_lst):

        if player in center_lst:

            y_receive_e = np.zeros(len(receive_e)) + 2.5
            ax = plt.gca()
            plt.scatter(receive_e,y_receive_e,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_center_receive_e.loc[top_center_receive_e["선수명"]==player,"리시브 효율"],2.5,s=150,c ="r")

            plt.ylim()
            plt.xlabel('리시브 효율')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/center_'+str(player)+'_receive_e.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass        

def left():
        
    df = dbtodf("player_graph_app_left_player")
    left = df        
    left["공격 성공률"] = left["공격 성공"]/left["공격 시도"]
    left["공격 효율"] = (left["공격 성공"] - left["공격 상대 블락"] - left["공격 범실"])/left["공격 시도"]
    left["서브 성공률"] = left["서브 성공"]/left["서브 시도"]
    left["세트 성공률"] = left["세트 성공"]/left["세트 시도"]
    left["블로킹 성공률"] = left["블로킹 성공"]/left["블로킹 시도"]
    left["리시브 효율"] = (left["리시브 정확"]-left["리시브 실패"])/left["리시브 시도"]
    left["디그 성공률"] = left["디그 성공"]/left["디그 시도"]

    top_left = left.iloc[:,[1,2,-7,-6,-5,-4,-3,-2,-1]]
    top_left = top_left.fillna(0)

    # 2021 KOVO 세터 선수들 중 디그 성공률로 순위를 표현한 데이터프레임
    top_left_dig = top_left.sort_values(by = "디그 성공률",ascending = False)
    top_left_dig["순위"] = np.arange(1,len(top_left_dig)+1)
    top_left_dig.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 블로킹 성공률로 순위를 표현한 데이터프레임
    top_left_blocking = top_left.sort_values(by = "블로킹 성공률",ascending = False)
    top_left_blocking["순위"] = np.arange(1,len(top_left_blocking)+1)
    top_left_blocking.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 세트 성공률로 순위를 표현한 데이터프레임
    top_left_set = top_left.sort_values(by = "세트 성공률",ascending = False)
    top_left_set["순위"] = np.arange(1,len(top_left_set)+1)
    top_left_set.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 공격 성공률로 순위를 표현한 데이터프레임
    top_left_at = top_left.sort_values(by = "공격 성공률",ascending = False)
    top_left_at["순위"] = np.arange(1,len(top_left_at)+1)
    top_left_at.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 공격 효율로 순위를 표현한 데이터프레임
    top_left_at_e = top_left.sort_values(by = "공격 효율",ascending = False)
    top_left_at_e["순위"] = np.arange(1,len(top_left_at_e)+1)
    top_left_at_e.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 서브 성공률로 순위를 표현한 데이터프레임
    top_left_serve = top_left.sort_values(by = "서브 성공률",ascending = False)
    top_left_serve["순위"] = np.arange(1,len(top_left_serve)+1)
    top_left_serve.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 리시브 효율로 순위를 표현한 데이터프레임
    top_left_receive_e = top_left.sort_values(by = "리시브 효율",ascending = False)
    top_left_receive_e["순위"] = np.arange(1,len(top_left_receive_e)+1)
    top_left_receive_e.set_index("순위",inplace = True)


    # 디그 성공률로 순위 매긴 데이터프레임에서 디그성공률 값만 가져와 리스트로 생성
    # 추후 디그 성공률 산점도에 x축으로 넣어줄 값임
    dig_suc = top_left_dig["디그 성공률"].tolist()
    blocking_suc = top_left_blocking["블로킹 성공률"].tolist()
    set_suc = top_left_set["세트 성공률"].tolist()
    at_suc = top_left_at['공격 성공률'].tolist()
    at_e = top_left_at_e['공격 효율'].tolist()
    serve_suc = top_left_serve['서브 성공률'].tolist()
    receive_e = top_left_receive_e['리시브 효율'].tolist()

    # 한글 폰트 깨짐 방지 
    # rc('font', family='AppleGothic') 
    # plt.rcParams['axes.unicode_minus'] = False

    left.set_index('Rank', inplace=True)
    left_lst = left['선수명'].tolist()     # 반복문 리스트 내 데이터 비교를 위한 리스트화 작업. 

    for i, player in enumerate(h_cap_lst):

        if player in left_lst:

            # 그래프 작성하려면 y축 값도 있긴 해야해서 y값 리스트 생성
            y_dig = np.zeros(len(dig_suc)) + 0.45

            # y축 삭제하기위해 ax 설정
            ax = plt.gca()

            # 모든 선수 점 찍기
            plt.scatter(dig_suc,y_dig,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_left_dig.loc[top_left_dig["선수명"]==player,"디그 성공률"],0.45,s=150,c ="r")

            plt.ylim()
            plt.xlabel('디그 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/left_'+str(player)+'_dig_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else:
            pass

    for i, player in enumerate(h_cap_lst):

        if player in left_lst:

            y_blocking = np.zeros(len(blocking_suc)) + 0.3
            ax = plt.gca()
            plt.scatter(blocking_suc,y_blocking,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_left_blocking.loc[top_left_blocking["선수명"]==player,"블로킹 성공률"],0.3,s=150,c ="r")

            plt.ylim()
            plt.xlabel('블로킹 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/left_'+str(player)+'_blocking_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else:
             pass

    for i, player in enumerate(h_cap_lst):

        if player in left_lst:

            y_set = np.zeros(len(set_suc)) + 0.7
            ax = plt.gca()
            plt.scatter(set_suc,y_set,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_left_set.loc[top_left_set["선수명"]==player,"세트 성공률"],0.7,s=150,c ="r")

            plt.ylim()
            plt.xlabel('세트 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/left_'+str(player)+'_set_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass

    for i, player in enumerate(h_cap_lst):

        if player in left_lst:

            y_at = np.zeros(len(at_suc)) + 0.3
            ax = plt.gca()
            plt.scatter(at_suc,y_at,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_left_at.loc[top_left_at["선수명"]==player,"공격 성공률"],0.3,s=150,c ="r")

            plt.ylim()
            plt.xlabel('공격 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/left_'+str(player)+'_at_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass    

    for i, player in enumerate(h_cap_lst):

        if player in left_lst:

            y_at_e = np.zeros(len(at_e)) + 0.45
            ax = plt.gca()
            plt.scatter(at_e,y_at_e,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_left_at_e.loc[top_left_at_e["선수명"]==player,"공격 효율"],0.45,s=150,c ="r")

            plt.ylim()
            plt.xlabel('공격 효율')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/left_'+str(player)+'_at_e.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass     

    for i, player in enumerate(h_cap_lst):

        if player in left_lst:

            y_serve = np.zeros(len(serve_suc)) + 0.3
            ax = plt.gca()
            plt.scatter(serve_suc,y_serve,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_left_serve.loc[top_left_serve["선수명"]==player,"서브 성공률"],0.3,s=150,c ="r")

            plt.ylim()
            plt.xlabel('서브 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/left_'+str(player)+'_serve_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass

    for i, player in enumerate(h_cap_lst):

        if player in left_lst:

            y_receive_e = np.zeros(len(receive_e)) + 0.7
            ax = plt.gca()
            plt.scatter(receive_e,y_receive_e,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_left_receive_e.loc[top_left_receive_e["선수명"]==player,"리시브 효율"],0.7,s=150,c ="r")

            plt.ylim()
            plt.xlabel('리시브 효율')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/left_'+str(player)+'_receive_e.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass 

def right():        
        
    df = dbtodf("player_graph_app_right_player")
    right = df      
    right["공격 성공률"] = right["공격 성공"]/right["공격 시도"]
    right["공격 효율"] = (right["공격 성공"] - right["공격 상대 블락"] - right["공격 범실"])/right["공격 시도"]
    right["서브 성공률"] = right["서브 성공"]/right["서브 시도"]
    right["세트 성공률"] = right["세트 성공"]/right["세트 시도"]
    right["블로킹 성공률"] = right["블로킹 성공"]/right["블로킹 시도"]
    right["리시브 효율"] = (right["리시브 정확"]-right["리시브 실패"])/right["리시브 시도"]
    right["디그 성공률"] = right["디그 성공"]/right["디그 시도"]

    top_right = right.iloc[:,[1,2,-7,-6,-5,-4,-3,-2,-1]]
    top_right = top_right.fillna(0)

    # 2021 KOVO 세터 선수들 중 디그 성공률로 순위를 표현한 데이터프레임
    top_right_dig = top_right.sort_values(by = "디그 성공률",ascending = False)
    top_right_dig["순위"] = np.arange(1,len(top_right_dig)+1)
    top_right_dig.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 블로킹 성공률로 순위를 표현한 데이터프레임
    top_right_blocking = top_right.sort_values(by = "블로킹 성공률",ascending = False)
    top_right_blocking["순위"] = np.arange(1,len(top_right_blocking)+1)
    top_right_blocking.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 세트 성공률로 순위를 표현한 데이터프레임
    top_right_set = top_right.sort_values(by = "세트 성공률",ascending = False)
    top_right_set["순위"] = np.arange(1,len(top_right_set)+1)
    top_right_set.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 공격 성공률로 순위를 표현한 데이터프레임
    top_right_at = top_right.sort_values(by = "공격 성공률",ascending = False)
    top_right_at["순위"] = np.arange(1,len(top_right_at)+1)
    top_right_at.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 공격 효율로 순위를 표현한 데이터프레임
    top_right_at_e = top_right.sort_values(by = "공격 효율",ascending = False)
    top_right_at_e["순위"] = np.arange(1,len(top_right_at_e)+1)
    top_right_at_e.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 서브 성공률로 순위를 표현한 데이터프레임
    top_right_serve = top_right.sort_values(by = "서브 성공률",ascending = False)
    top_right_serve["순위"] = np.arange(1,len(top_right_serve)+1)
    top_right_serve.set_index("순위",inplace = True)

    # 2021 KOVO 세터 선수들 중 리시브 효율로 순위를 표현한 데이터프레임
    top_right_receive_e = top_right.sort_values(by = "리시브 효율",ascending = False)
    top_right_receive_e["순위"] = np.arange(1,len(top_right_receive_e)+1)
    top_right_receive_e.set_index("순위",inplace = True)


    # 디그 성공률로 순위 매긴 데이터프레임에서 디그성공률 값만 가져와 리스트로 생성
    # 추후 디그 성공률 산점도에 x축으로 넣어줄 값임
    dig_suc = top_right_dig["디그 성공률"].tolist()
    blocking_suc = top_right_blocking["블로킹 성공률"].tolist()
    set_suc = top_right_set["세트 성공률"].tolist()
    at_suc = top_right_at['공격 성공률'].tolist()
    at_e = top_right_at_e['공격 효율'].tolist()
    serve_suc = top_right_serve['서브 성공률'].tolist()
    receive_e = top_right_receive_e['리시브 효율'].tolist()

    # 한글 폰트 깨짐 방지 
    # rc('font', family='AppleGothic') 
    # plt.rcParams['axes.unicode_minus'] = False

    right.set_index('Rank', inplace=True)
    right_lst = right['선수명'].tolist()     # 반복문 리스트 내 데이터 비교를 위한 리스트화 작업. 

    for i, player in enumerate(h_cap_lst):

        if player in right_lst:

            # 그래프 작성하려면 y축 값도 있긴 해야해서 y값 리스트 생성
            y_dig = np.zeros(len(dig_suc)) + 1.3

            # y축 삭제하기위해 ax 설정
            ax = plt.gca()

            # 모든 선수 점 찍기
            plt.scatter(dig_suc,y_dig,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_right_dig.loc[top_right_dig["선수명"]==player,"디그 성공률"],1.3,s=150,c ="r")

            plt.ylim()
            plt.xlabel('디그 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/right_'+str(player)+'_dig_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else:
            pass

    for i, player in enumerate(h_cap_lst):

        if player in right_lst:

            y_blocking = np.zeros(len(blocking_suc)) + 0.55
            ax = plt.gca()
            plt.scatter(blocking_suc,y_blocking,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_right_blocking.loc[top_right_blocking["선수명"]==player,"블로킹 성공률"],0.55,s=150,c ="r")

            plt.ylim()
            plt.xlabel('블로킹 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/right_'+str(player)+'_blocking_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else:
             pass

    for i, player in enumerate(h_cap_lst):

        if player in right_lst:

            y_set = np.zeros(len(set_suc)) + 1.7
            ax = plt.gca()
            plt.scatter(set_suc,y_set,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_right_set.loc[top_right_set["선수명"]==player,"세트 성공률"],1.7,s=150,c ="r")

            plt.ylim()
            plt.xlabel('세트 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/right_'+str(player)+'_set_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass

    for i, player in enumerate(h_cap_lst):

        if player in right_lst:

            y_at = np.zeros(len(at_suc)) + 0.55
            ax = plt.gca()
            plt.scatter(at_suc,y_at,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_right_at.loc[top_right_at["선수명"]==player,"공격 성공률"],0.55,s=150,c ="r")

            plt.ylim()
            plt.xlabel('공격 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/right_'+str(player)+'_at_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass    

    for i, player in enumerate(h_cap_lst):

        if player in right_lst:

            y_at_e = np.zeros(len(at_e)) + 1.2
            ax = plt.gca()
            plt.scatter(at_e,y_at_e,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_right_at_e.loc[top_right_at_e["선수명"]==player,"공격 효율"],1.2,s=150,c ="r")

            plt.ylim()
            plt.xlabel('공격 효율')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/right_'+str(player)+'_at_e.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass     

    for i, player in enumerate(h_cap_lst):

        if player in right_lst:

            y_serve = np.zeros(len(serve_suc)) + 0.3
            ax = plt.gca()
            plt.scatter(serve_suc,y_serve,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_right_serve.loc[top_right_serve["선수명"]==player,"서브 성공률"],0.3,s=150,c ="r")

            plt.ylim()
            plt.xlabel('서브 성공률')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/right_'+str(player)+'_serve_suc.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass

    for i, player in enumerate(h_cap_lst):

        if player in right_lst:

            y_receive_e = np.zeros(len(receive_e)) + 3
            ax = plt.gca()
            plt.scatter(receive_e,y_receive_e,c = "black")

            # 이거 참고해서 조건문으로 해당 선수만 가져오면 될 듯
            plt.scatter(top_right_receive_e.loc[top_right_receive_e["선수명"]==player,"리시브 효율"],3,s=150,c ="r")

            plt.ylim()
            plt.xlabel('리시브 효율')
            plt.ylabel('Y-Axis')
            plt.axis('scaled')

            # y축 삭제
            ax.axes.yaxis.set_visible(False)
            plt.savefig('static/img/right_'+str(player)+'_receive_e.png')
            plt.clf()       # 그래프를 초기화한다.
            #plt.axis("off")

        else :
            pass        



