"""make_charts.py — Regenerates the 5-6 decision-useful charts from outputs/metrics_full_series.csv.
Run: python src/compute_metrics.py && python src/make_charts.py"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

YEARS=['FY20','FY21','FY22','FY23','FY24','FY25']
COS=['Marico Limited','Dabur India Limited','Hindustan Unilever Limited']
SHORT={'Marico Limited':'Marico','Dabur India Limited':'Dabur','Hindustan Unilever Limited':'HUL'}
COL={'Marico Limited':'#1f77b4','Dabur India Limited':'#2ca02c','Hindustan Unilever Limited':'#d62728'}
df=pd.read_csv('outputs/metrics_full_series.csv')
plt.rcParams.update({'axes.grid':True,'grid.alpha':0.3,'figure.dpi':150,'axes.spines.top':False,'axes.spines.right':False})
x=np.arange(6)
def g(co,m):
    s=df[df.company==co].set_index('fiscal_year')[m]; return [s.get(y,np.nan) for y in YEARS]
def shade(ax):
    ax.axvspan(-0.5,2.5,color='#1f77b4',alpha=.05); ax.axvspan(2.5,3.5,color='#ff7f0e',alpha=.10); ax.axvspan(3.5,5.5,color='#2ca02c',alpha=.07)

fig,axes=plt.subplots(1,3,figsize=(13,4.2))
for ax,co in zip(axes,COS):
    for m,st in [('DIO','-o'),('DSO','-s'),('DPO','-^')]: ax.plot(x,g(co,m),st,label=m,ms=4)
    ax.bar(x,g(co,'CCC'),width=.5,alpha=.35,color='grey',label='CCC'); ax.axhline(0,color='k',lw=.8); shade(ax)
    ax.set_title(SHORT[co],fontweight='bold'); ax.set_xticks(x); ax.set_xticklabels(YEARS,rotation=45)
axes[0].set_ylabel('Days'); axes[0].legend(fontsize=8)
fig.suptitle('Working Capital Cycle per Company'); fig.tight_layout(); fig.savefig('outputs/charts/chart1_working_capital_cycle.png',bbox_inches='tight'); plt.close()

fig,ax=plt.subplots(figsize=(8,4.5))
for co in COS: ax.plot(x,g(co,'CCC'),'-o',color=COL[co],label=SHORT[co])
ax.axhline(0,color='k',lw=.8); shade(ax); ax.set_xticks(x); ax.set_xticklabels(YEARS); ax.set_ylabel('CCC (days)'); ax.legend()
ax.set_title('Cash Conversion Cycle Across Companies',fontweight='bold'); fig.tight_layout(); fig.savefig('outputs/charts/chart2_ccc_cross_company.png',bbox_inches='tight'); plt.close()

fig,axes=plt.subplots(1,3,figsize=(13,4.2))
for ax,(m,t) in zip(axes,[('GrossMargin','Gross Margin'),('EBITDAMargin','EBITDA Margin'),('NetMargin','Net Margin')]):
    for co in COS: ax.plot(x,np.array(g(co,m))*100,'-o',color=COL[co],label=SHORT[co],ms=4)
    shade(ax); ax.set_title(t,fontweight='bold'); ax.set_xticks(x); ax.set_xticklabels(YEARS,rotation=45); ax.set_ylabel('%')
axes[0].legend(fontsize=8); fig.suptitle('Profitability Margin Trends'); fig.text(0.5,-0.02,'EBITDA margin is project-defined (built from PBEIT; see data dictionary), not a company-reported figure.',ha='center',fontsize=7.5,style='italic'); fig.tight_layout(); fig.savefig('outputs/charts/chart3_margin_trends.png',bbox_inches='tight'); plt.close()

fig,axes=plt.subplots(1,2,figsize=(11,4.9))
for ax,(m,t) in zip(axes,[('ROCE','ROCE (project-defined: EBIT / avg. capital employed)'),('ROA','ROA')]):
    for co in COS:
        y=np.array(g(co,m))*100
        if co=='Hindustan Unilever Limited':
            # Structural break: FY20 sits on the pre-GSK-CH-merger capital base — plot it as a
            # visually distinct, disconnected artifact point, and the comparable series from FY21 on.
            ax.plot(x[:1],y[:1],'o',color=COL[co],mfc='white',mew=1.6,ms=7)
            ax.plot(x[1:],y[1:],'-o',color=COL[co],label=SHORT[co])
            ax.plot(x[:2],y[:2],':',color=COL[co],lw=1.1,alpha=.6)
            ax.axvline(0.5,color=COL[co],ls='--',lw=1,alpha=.7)
            if m=='ROCE':
                ax.annotate('HUL FY20 = pre-merger capital base\n(GSK-CH consolidates FY21:\ntotal assets ₹20,153 → ₹68,757 cr)',
                            xy=(0,y[0]),xytext=(0.7,y[0]-6),fontsize=7.5,color=COL[co],
                            arrowprops=dict(arrowstyle='->',color=COL[co],lw=.8))
                ax.axhspan(20,22,color=COL[co],alpha=.08)
                ax.text(5.45,21,'HUL ex-FY20 sensitivity:\nflat ~20–22% FY22–FY25',fontsize=7.5,color=COL[co],va='center')
        else:
            ax.plot(x,y,'-o',color=COL[co],label=SHORT[co])
    shade(ax); ax.set_title(t,fontweight='bold',fontsize=10); ax.set_xticks(x); ax.set_xticklabels(YEARS); ax.set_ylabel('%')
axes[0].set_xlim(-0.5,7.6); axes[0].legend(fontsize=8)
fig.suptitle('Return Metrics — HUL FY20 flagged: GSK-CH merger structural break (not a quick-commerce effect)')
fig.text(0.5,-0.02,'ROCE and EBITDA-based figures are project-defined computed metrics (see data dictionary), not company-reported ratios.',ha='center',fontsize=7.5,style='italic')
fig.tight_layout(); fig.savefig('outputs/charts/chart4_roce_roa.png',bbox_inches='tight'); plt.close()

metrics=[('CCC','CCC (days)',1),('DSO','DSO (days)',1),('EBITDAMargin','EBITDA Margin (%)',100),('NetMargin','Net Margin (%)',100),('ROCE','ROCE (%)',100),('RevGrowth','Revenue Growth (%)',100)]
fig,axes=plt.subplots(2,3,figsize=(13,7.5)); w=.35
for ax,(m,t,s) in zip(axes.flat,metrics):
    pre=[np.mean([g(co,m)[YEARS.index(y)] for y in ['FY20','FY21','FY22']])*s for co in COS]
    post=[np.mean([g(co,m)[YEARS.index(y)] for y in ['FY24','FY25']])*s for co in COS]
    xx=np.arange(3); ax.bar(xx-w/2,pre,w,label='Pre (FY20-22)',color='#7f9fc4'); ax.bar(xx+w/2,post,w,label='Post (FY24-25)',color='#3c6e47')
    ax.axhline(0,color='k',lw=.8); ax.set_xticks(xx); ax.set_xticklabels([SHORT[c] for c in COS]); ax.set_title(t,fontweight='bold',fontsize=10)
axes[0,0].legend(fontsize=8); fig.suptitle('Pre vs Post Period Averages'); fig.text(0.5,-0.01,'EBITDA margin and ROCE are project-defined computed metrics (see data dictionary). HUL ROCE pre-period average includes the pre-GSK-CH-merger FY20 base — see Chart 4.',ha='center',fontsize=7.5,style='italic'); fig.tight_layout(); fig.savefig('outputs/charts/chart5_pre_vs_post.png',bbox_inches='tight'); plt.close()

fig,ax=plt.subplots(figsize=(9,4.5)); w=.25
for i,co in enumerate(COS): ax.bar(x+(i-1)*w,np.array(g(co,'RevGrowth'))*100,w,color=COL[co],label=SHORT[co])
ax.axhline(0,color='k',lw=.8); shade(ax); ax.set_xticks(x); ax.set_xticklabels(YEARS); ax.set_ylabel('YoY %'); ax.legend()
ax.set_title('Revenue Growth',fontweight='bold'); fig.tight_layout(); fig.savefig('outputs/charts/chart6_revenue_growth.png',bbox_inches='tight'); plt.close()
print('charts regenerated')
