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

def PlotLikertOverConditions(tb,nPoint,customLikertRange=None,tb2=None,customLikertRange2=None):
    # This functions gets a table of questions and their responces in likert scale (1:positive N:negative) as coulmns, as well as a another column indicating the condition of the responce
    # This function can also get another table for general questions after all conditions
    
    
    Qs=tb.columns.tolist()
    CustomLikertLabels_orderd_by_y_axis=[]
    
    df=tb.copy(deep=True)
    likert_colors= sns.color_palette("coolwarm", nPoint)
    likert_colors=[(1.0,1.0,1.0)]+likert_colors

    
    font1 = {'family': 'sans-serif','color':  'white','weight': 'normal','size': 10,}
    font2 = {'family': 'sans-serif','color':  'grey','weight': 'normal','size': 8,}
    LikertRange=[1,2,3,4,5]
    fig, ax = plt.subplots(1, 1,figsize=(10,8))
    
    
    ##--------------------------------------------------------------------
    ##Seperate into conditions and count the scores for each
    df_conds=[]
    middles_all=[]
#     df.loc[:,'condition']=df['condition'].astype(np.int32)
    
    barwidth=0.2
    def SHIFT(N,i):
        return float(i)*barwidth*1.0-(float(N)-1)*barwidth
        
   
    conds=[]
    for cond in df['condition'].unique():
        conds.append(cond)
        temp=df[df['condition']==cond]
        temp.drop('condition', axis=1,inplace=True)
        temp=pd.DataFrame(temp.stack())
        temp=pd.DataFrame(temp.unstack(0))


        g= lambda x,y: x.loc[y] if y in x.index else 0
        temp2=temp.copy(deep=True)
        for q in range(1,len(Qs)):
            for i in range(1,nPoint+1):
    #             print 'there was %s of %s in Q %s'%(g(temp.loc[Qs[q],:].value_counts(),i),i,q)
                temp2.loc[Qs[q], i]=g(temp.loc[Qs[q],:].value_counts(),i)
        
        temp2.drop(0, axis=1,inplace=True)
        temp2.columns = temp2.columns.droplevel(level=1)
#         print temp2
        df_conds.append( temp2)
        middles_all.append(temp2[LikertRange[:len(LikertRange)//2]].sum(axis=1)+temp2[len(LikertRange)//2+1]*.5)

    
    ##--------------------------------------------------------------------
    ## general questions
    df_conds_generals=[]
    middles_all_generals=[]
    ## here we add general questions as well if there is any!
    if type(tb2)==pd.core.frame.DataFrame:
        temp=tb2.copy(deep=True)
        temp2=tb2.T.copy(deep=True)
        
        for gQ, g_col in temp.iteritems():
            g= lambda x,y: x.loc[y] if y in x.index else 0
            for i in range(1,nPoint+1):
                temp2.loc[gQ, i]=g(g_col.astype(np.int32,inplace=True).value_counts(),i)
                
        temp2=temp2.loc[:,range(1,nPoint+1)] 
#         print temp2
        df_conds_generals= temp2
        middles_all_generals=temp2[LikertRange[:len(LikertRange)//2]].sum(axis=1)+temp2[len(LikertRange)//2+1]*.5


    ##--------------------------------------------------------------------
        
    ## add shift column to each table
    if len(np.array(middles_all_generals))==0: 
        longest= max(map(max,  np.array(middles_all)) )
    else:
        longest= max(max(map(max,  np.array(middles_all)) ),max(np.array(middles_all_generals)) ) 
        
        
    
    patches_already_moved=[]
    for cond,df_c in enumerate(df_conds):

        df_c.insert(0, '', (middles_all[cond] - longest).abs())
        complete_longest=int(longest+(df_c[:].sum(axis=1).max()-longest))#in our case is 16

        patch_handles = []
        
        patch_handles.append(df_c.plot.barh(ax=ax,stacked=True, color=likert_colors, legend=False,
                                            width=barwidth,edgecolor='white'))#,alpha=1.0-(float(cond)/len(df_conds))*0.7

        shift=SHIFT(len(df_conds),cond)
        
        for j in range(len(patch_handles)):
            for i, p in enumerate(patch_handles[j].get_children()):
                
                
                if type(p)==(matplotlib.patches.Rectangle):
                    
                    if p.get_height()==barwidth and not (p in patches_already_moved):
#                         print (p in patches_already_moved),
                        
                        p.set_xy((p.get_x(),p.get_y()+shift))
                    
 
                        if p.get_width()>1 and p.get_facecolor()[0:3]!=likert_colors[0]:#p.get_facecolor()!=(1.0, 1.0, 1.0, 1.0):
#                             if cond % 2 == 0:
#                                 p.set_hatch('\ '*cond)
#                             else:
#                                 p.set_hatch('/ '*cond)
                                
                            patch_handles[j].text(
                                p.get_x()+p.get_width()/2.,
                                p.get_y()+ p.get_height() /(len(Qs)-1),
                                "{0:.0f}%".format(p.get_width()/(len(tb)/len(tb['condition'].unique())) * 100),
                                ha="center",
                                fontdict=font1)#.set_zorder(-1)

        
        
        patches_already_moved=patches_already_moved+patch_handles[j].get_children()

    yticks=list(ax.get_yticks())
#     print customLikertRange
    CustomLikertLabels_orderd_by_y_axis=[customLikertRange[key] if (customLikertRange!=None and customLikertRange.get(key)) 
                                         else ['very low','very high'] 
                                         for key in (ax.get_yticks()+1)]
 
    
    if type(tb2)==pd.core.frame.DataFrame:
        CustomLikertLabels_orderd_by_y_axis=[customLikertRange2[key] if (customLikertRange2!=None and customLikertRange2.get(key)) 
                                         else ['very low','very high'] 
                                         for key in range(1,len(df_conds_generals)+1)][::-1]+CustomLikertLabels_orderd_by_y_axis
        
        
        ## Plotting general questions
        def SHIFT2(i):
            i=i+0.1
            extra=0.5
            return -1.3 -(i*(2*(barwidth)+extra))

        df_conds_generals.insert(0, '', (middles_all_generals - longest).abs())
        for i in range(0,len(df_conds_generals)):
            y=SHIFT2(i-0.1)
            yticks=[y]+ yticks
            y=y+barwidth/2.0
            ax.plot([-5,df_conds_generals.iloc[i,0]],[y,y],linestyle=':', color='grey', alpha=.2,linewidth=1)
            


        patch_handles = []
        patch_handles.append(df_conds_generals.plot.barh(ax=ax,stacked=True, color=likert_colors, legend=False,
                                            width=barwidth,edgecolor='white'))   

        for j in range(len(patch_handles)):
            for i, p in enumerate(patch_handles[j].get_children()):


                if type(p)==(matplotlib.patches.Rectangle):

                    if p.get_height()==barwidth and not (p in patches_already_moved):
                        shift=SHIFT2(p.get_y())

                        p.set_xy((p.get_x(),shift))
                        if p.get_width()>1 and p.get_facecolor()[0:3]!=likert_colors[0]:#p.get_facecolor()!=(1.0, 1.0, 1.0, 1.0):

                            patch_handles[j].text(
                                p.get_x()+p.get_width()/2.,
                                shift+ p.get_height() /(len(Qs)-1),
                                "{0:.0f}%".format(p.get_width()/(len(tb)/len(tb['condition'].unique())) * 100),
                                ha="center",
                                fontdict=font1)#.set_zorder(-1)



        patches_already_moved=patches_already_moved+patch_handles[j].get_children()

        
    z = ax.axvline(longest, linestyle='-', color='black', alpha=.5,linewidth=1)
    z.set_zorder(-1)  
#     print longest


    plt.xlim(-5, complete_longest+5)
    ymin=-1*len(df_conds_generals)-1
    plt.ylim(ymin,len(Qs)-1.5)
    
    xvalues = range(0, complete_longest,10)
    xlabels = []#[str(x-longest) for x in xvalues]
    plt.xticks(xvalues, xlabels)
    plt.xlabel('Percentage', fontsize=12,horizontalalignment='left')
    ax.xaxis.set_label_coords(float(longest)/(complete_longest+5),-0.01)

    general_Qs=[] if  len(df_conds_generals)==0 else df_conds_generals.index.values.tolist() #+['']
    ylabels =general_Qs +Qs[1:]

    plt.yticks(yticks, ylabels)
    
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(12) 


    ## adding condition indicators on the y axis
    for cond,df_c in enumerate(df_conds): 
        shift=SHIFT(len(df_conds),cond)
        for row in  range(0,len(df_c)):
            
            y=row+shift
            x=ax.get_xlim()[0]+0.5
#             x=ax.get_xlim()[0]+1.3
            ax.text(
                x,
                y-barwidth/4.0,
#                 str(cond),
#                 'C ' + str(cond+1),
                conds[cond],
                ha="center",
                fontdict=font2)
            ax.plot([x+0.7,df_c.iloc[row,0]],[y,y],linestyle=':', color='grey', alpha=.2,linewidth=1)

            

    plt.grid('off')
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
#     print yticks
    ## adding Likert range legend 
    for i,y_tick in enumerate(yticks):

        v=CustomLikertLabels_orderd_by_y_axis[i]
        x=-12
        
        y=yticks[i]-0.4
        ax.text(x,y, v[0],fontsize = 8,zorder = 6, color = 'white',horizontalalignment='right',
                    bbox={'edgecolor':'none','facecolor':likert_colors[1], 'alpha':1.0, 'pad':2})  
        
        middle_colors=likert_colors[1:-1]
        for ci,c in enumerate(middle_colors):
            x=x+0.3
            ax.text(x,y,' ',fontsize = 8,zorder = 6, color = 'white',horizontalalignment='right',
                    bbox={'edgecolor':'none','facecolor':middle_colors[ci], 'alpha':1.0, 'pad':2})  
            
            
        ax.text(x+0.2,y,v[1],fontsize = 8,zorder = 6, color = 'white',horizontalalignment='left',
                    bbox={'edgecolor':'none','facecolor':likert_colors[-1], 'alpha':1.0, 'pad':2})  
    plt.tight_layout()
    plt.savefig('example.png')
    plt.show()