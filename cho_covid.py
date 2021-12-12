import requests
from bs4 import BeautifulSoup
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime

#output path
png_path = './output/fig.png'
txt_path = './output/string.txt'

#SIR model
def deriv(y, t, N, beta, gamma):
    S, I, R = y
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I
    dRdt = gamma * I
    return dSdt, dIdt, dRdt


#__main__
now = datetime.now() # current date and time
today = now.strftime("%Y") + now.strftime("%m") + now.strftime("%d")
url = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson'
params ={'serviceKey' : 'ViQvOoJw1W/waMNqrtcmK7U1GlOfKbFtGjwUkbQxj92f8BSLCNIm2VWmJqVfsadRLeFO7SrGaKnZpGGGUkFs2Q==',
    'pageNo' : '1', 'numOfRows' : '1000', 'startCreateDt' : '20200310', 'endCreateDt' : today }
response = requests.get(url=url, params=params)

if response.status_code == 200 :
    soup = BeautifulSoup(response.text, 'html.parser')
    soup_list = soup.find_all('item')

    df_values = []
    [df_values.append([i.statedt.text, i.deathcnt.text, i.decidecnt.text, i.accexamcnt.text]) for i in soup_list]
    df = pd.DataFrame(df_values, columns=['기준일', '사망자 수', '확진자 수', '검사자 수'])

    N = 5*1000*10000
    I0, R0 = int(df.iloc[0,2]) - int(df.iloc[1,2]), int(df.iloc[0,1]) + int(df.iloc[0,3])
    S0 = N - I0 - R0

    beta, gamma, days = 0.2, 1./20, 300
    S_r, D_r = 12.50234, 150.64705
    t = np.linspace(0, days, days)

    y0 = S0, I0, R0
    ret = odeint(deriv, y0, t, args=(N, beta, gamma))
    S, I, R = ret.T

    fig = plt.figure()
    ax = fig.add_subplot(111, axisbelow=True)
    ax.plot(S,label='Susceptible')
    ax.plot(I,label='Infected')
    ax.plot(R,label='Recovered')
    ax.set_xlabel('Time /days')
    ax.set_ylabel('Number')
    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)
    ax.grid(b=True, which='major', c='w', lw=2, ls='-')
    legend = ax.legend()
    legend.get_frame().set_alpha(0.5)

    for spine in ('top', 'right', 'bottom', 'left'):
        ax.spines[spine].set_visible(False)

    #plt.show()
    plt.savefig(png_path, dpi=300)
    df2 = pd.DataFrame([int(I[1]*S_r), int(I[1]), int(I[1]/D_r)], columns=['values'],
                    index=['다음날 예상 검사자 수', '다음날 예상 확진자 수', '다음날 예상 사망자 수'])
    df2.to_csv(txt_path)

else :
    print('response.status_code error')