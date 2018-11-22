'''
Created on March 20, 2017

@author: Diako Mardanbegi <d.mardanbegi@lancaster.ac.uk>
'''

import seaborn as sns
import matplotlib.patches as patches
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math as math
from pylab import *
import io, os, sys, types
pd.options.mode.chained_assignment = None  # default='warn'
sns.set_style("whitegrid")
mpl.rc("savefig", dpi=150)






def PlotLikertOverConditions(df,nPoint,LikertRangeLabels=None,InverseColor=False):

    df=df.sort_values(by=['condition'], ascending=False)
    if LikertRangeLabels==None:
        LikertRangeLabels=['low','high']


    barwidth=1

    likert_colors= sns.color_palette("coolwarm", nPoint)
    if InverseColor:
        likert_colors=likert_colors[::-1]
    likert_colors=[(1.0,1.0,1.0)]+likert_colors


        
    LikertRange=list(range(1,nPoint+1))

    font1 = {'family': 'sans-serif','color':  'white','weight': 'normal','size': 11,}
    font2 = {'family': 'sans-serif','color':  'white','weight': 'bold','size': 12,}


    Questions=list(df.columns.values)[1:]
    Conditions=df.condition.unique()
    N=len(Questions)

    ## create figure
    fig = plt.figure(figsize=(10, (N+1)*1.5))






    N_participants=pd.pivot_table(df,index=["condition"],values=Questions[0], aggfunc='count')[Questions[0]].mean()



    score_count_all=pd.DataFrame()
    ## iterate through each question
    ax_q_list=[]
    ## reserve one for the likert legend
    ax_q_list.append(plt.subplot2grid((N+1,1), (0,0), colspan=1,rowspan=1))
    ax_q_list[-1].grid('off')
    for Q_i,Q in enumerate(Questions):
        

        ## create axis for each question
        ax_q_list.append(plt.subplot2grid((N+1,1), (Q_i+1,0), colspan=1,rowspan=1))
        ax=ax_q_list[-1]

        
        

        score_count=pd.DataFrame(index=Conditions)
        score_count.loc[:,'Q']=Q
        
        ## create bars for results of each condition
        for C_i,C in enumerate(Conditions):
            
            
            temp=df.loc[ ( df['condition']==C),Q].to_frame()
    # 
            g= lambda x,y: x.loc[y] if y in x.index else 0
            

            for i in range(1,nPoint+1):
    #                 print ('there was %s of %s in Q %s'%(g(temp.loc[cols[q],:].value_counts(),i),i,q))
                score_count.loc[C, i]=g(temp.loc[:,Q].value_counts(),i)

    #         # for debug
    #         score_count.loc[0:1,1]=12
    #         score_count.loc[0:1,[2,3,4,5]]=0
            

            score_count.loc[:, 'middle']=score_count[LikertRange[:nPoint//2]].sum(axis=1)+score_count[nPoint//2+1]*.5
            
            
        score_count.reset_index(inplace=True)  
        score_count=score_count.rename(columns={"index":'C'})
        score_count_all=pd.concat([score_count,score_count_all],ignore_index=True)


    # score_count_all.insert(0, 'shift', (score_count_all.middle - score_count_all.middle.max()).abs())
    score_count_all.insert(0, 'shift',  (score_count_all.middle -N_participants).abs())


    # display(score_count_all)



    for Q_i,Q in enumerate(Questions):
        ax=ax_q_list[Q_i+1]
        
      
        
        
        scores=score_count_all[(score_count_all.Q==Q) ]
        scores.index=scores.C
        scores=scores.drop(['Q','C','middle'], axis=1)
        

    #     display(Q,scores)

        patch_handles=scores.plot.barh(ax=ax,stacked=True, color=likert_colors, legend=False,
                                            width=barwidth,edgecolor='white')#,alpha=1.0-(float(cond)/len(df_conds))*0.7

        
        ## draw percentage text in each patch
        for patch_i, patch in enumerate(patch_handles.get_children()):
            if type(patch)==(matplotlib.patches.Rectangle):
                if patch.get_height()==barwidth :
                    if patch.get_width()>1 and patch.get_facecolor()[0:3]!=likert_colors[0]:#p.get_facecolor()!=(1.0, 1.0, 1.0, 1.0):
    #                     if C_i % 2 == 0:
    #                         patch.set_hatch('\ '*C_i)
    #                     else:
    #                         patch.set_hatch('/ '*C_i)

                        patch_handles.text(
                            patch.get_x()+patch.get_width()/2.,
                            patch.get_y()+ patch.get_height() /(N-1)+0.1,
                            "{0:.0f}%".format(patch.get_width()/(len(df)/len(Conditions)) * 100),
                            ha="center",
                            fontdict=font1)#.set_zorder(-1)
                    if patch.get_facecolor()[0:3]==likert_colors[0]:
                        patch.set_zorder(-11)
                    
        for C_i,C in enumerate(Conditions):
            ax.plot([0,N_participants],[C_i,C_i],':k',zorder=-10,alpha=1.0,linewidth=0.5)



        

    tmp={}
    for i in LikertRange:
        tmp.update({i:[N_participants*2/nPoint]})
    barwidth=0.2
    patch_handles=pd.DataFrame(tmp).plot.barh(ax=ax_q_list[0],stacked=True, color=likert_colors[1:], legend=False,
                                        width=barwidth,edgecolor='white')#,alpha=1.0-(float(cond)/len(df_conds))*0.7
    ## draw LikertRangeLabels
    for patch_i, patch in enumerate(patch_handles.get_children()):
        if type(patch)==(matplotlib.patches.Rectangle):
            if patch.get_height()==barwidth :
                if patch.get_width()>1 and patch.get_facecolor()[0:3]==likert_colors[1]:

                    patch_handles.text(
                        patch.get_x()+patch.get_width()/2.,
                        patch.get_y()+ patch.get_height()/2.-0.2*barwidth ,
                        LikertRangeLabels[0],
                        ha="center",
                        fontdict=font2)#.set_zorder(-1)
                elif patch.get_width()>1 and patch.get_facecolor()[0:3]==likert_colors[-1]:

                    patch_handles.text(
                        patch.get_x()+patch.get_width()/2.,
                        patch.get_y()+ patch.get_height()/2.-0.2*barwidth ,
                        LikertRangeLabels[1],
                        ha="center",
                        fontdict=font2)#.set_zorder(-1)




    ax_q_list[0].plot([N_participants,N_participants],[-1,1],'k')


    for ax_i,ax in enumerate(ax_q_list):
        ax.set_ylabel('')
        ax.tick_params(top='off', bottom='off', left='off', right='off', labelleft='off' if ax_i==0 else 'on', labelbottom='off')
        if ax_i!=0:
            ax.set_title(Questions[ax_i-1],rotation=0,fontsize=14)

        ax.grid('off')
        ax.set_xlim(0-1,N_participants*2+1)
        

        for spine in ax.spines.values():
            spine.set_visible(False) #Indentation updated..



    plt.tight_layout()

    plt.savefig('example.png')
    plt.show()