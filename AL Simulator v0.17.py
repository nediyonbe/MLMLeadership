# -*- coding: utf-8 -*-
"""
In this version
    Clawback rates are added
    Interface updated
CHECK: In SL G1 Active count restricted Reps are taken into account 
    >>> Is it the same logic for QPA and Bad Debt related Commission adjustment calculations?
Spyder Editor"""

import pandas as pd
import numpy as np
import math
import ctypes #for messages to the user
import time #for folder name
print('test')

# =============================================================================
# FUNCTIONS
#Abort program e.g. if validation is not ok
def validate_logic():
    compteur = 0
    #VALIDATE QUALIFIERS ARE MEANINGFUL
    #PS, TS, G1 Active criteria should follow a non-decreasing pattern with increasing titles
    for k in range(2, max(Entries_TS_Dict.keys())+1):
        if (Entries_PS_Dict[k].get() < Entries_PS_Dict[k - 1].get()):
            compteur = compteur + 1
            lacheur('Personal Sales', k)
            break
        elif (Entries_TS_Dict[k].get() < Entries_TS_Dict[k - 1].get()):
            compteur = compteur + 1
            lacheur('Team Sales', k)
            break
        elif(Entries_G1Act_Dict[k].get() < Entries_G1Act_Dict[k - 1].get()):
            compteur = compteur + 1
            lacheur('G1 Active', k)
            break

    #an input file must have been selected
    if len(en_browse_input.get()) == 0:
        ctypes.windll.user32.MessageBoxW(0, 'You have not selected an input file.\n',
                                            'Oops', 0)
    #at least one of the output options should be selected
    if EntryCharts.get() + EntryStatus.get() == 0:
        ctypes.windll.user32.MessageBoxW(0, 'You have not selected any operation.\n Select at least one of the following: \n '
                                            'a) Export simulation results \n ' #EntryStatus
                                            'b) Provide charts \n ', #EntryCharts
                                            'Oops', 0)
    if EntryStatus.get() == 1 and len(en_browse.get()) == 0:
        ctypes.windll.user32.MessageBoxW(0,'You have not selected directory for simulation results.\n '
                                           'Opt out of exporting simulation results or select a directory \n ',
                                           'Oops', 0)
    if compteur == 0 \
            and len(en_browse_input.get()) > 0 \
            and ((EntryStatus.get() == 1 and len(en_browse.get()))
                 or EntryStatus.get() == 0):
        diviner()
            
def lacheur(criterion, title_id):
    ctypes.windll.user32.MessageBoxW(0, 'The ' + criterion + ' requirement of title ' + str(title_id) + ' cannot be lower than that of ' + str(title_id - 1) + '.\n Aborting now', 'Oops', 0)

# Enable/Disable Entries
def EnableDisableEntry():
    if EntryStatus.get() == 0:
        #BrowseLabel.configure(state='disabled')
        dirBut.configure(state='disabled')
    else:
        #BrowseLabel.configure(state='normal')
        dirBut.configure(state='normal')

def EnableDisableCent():
    if EntryStatusCent.get() == 0:
        ComboComm.configure(state='disabled')
        CentralCommLabel.configure(state='disabled')
    else:
        ComboComm.configure(state='normal')
        CentralCommLabel.configure(state='normal')

def EnableDisableNest():
    if EntryStatusNesting.get() == 0:
        ComboNest.configure(state='disabled')
        nesty_rep_label.configure(state='disabled')
    else:
        ComboNest.configure(state='normal')
        nesty_rep_label.configure(state='normal')
        
#validate user entries -  Check if value is integer
def check_int(inp):
    try:
        int(inp) == float(inp)
    except (TypeError, ValueError):
        return False
    else:
        if int(inp) == float(inp):
            return True
        else:
            return False 
#Ask user for directory e.g. for saving the output files
def askdirectory():
  dirname = filedialog.askdirectory()
  if dirname:
    en_browse.set(dirname)

def ask_input_file():
  dirname = filedialog.askopenfilename(title = 'Select File (MUST BE TAB SEPARATED)', filetypes = (('TSV Files', '*.tsv'), ('CSV Files', '*,csv'), ('Text Files', '*.txt')))
  if dirname:
      en_browse_input.set(dirname)

#Define grace count and badge title update function
def update_badge_grace(DF_In_Process, Paid_Level_In_Process, Grace_For_Can, Grace_For_Titles):
    #	IF (PaidTitle > BadgeTitle_PC) OR (PaidTitle = BadgeTitle_PC AND PaidTitle > 0) THEN
        #BadgeTitle = PaidTitle
    DF_In_Process.loc[
        (DF_In_Process['PAID_LEVEL_SIM'] == Paid_Level_In_Process) 
        &
        ((DF_In_Process['PAID_LEVEL_SIM'] > DF_In_Process['BADGE_LEVEL_PC']) |
        ((DF_In_Process['PAID_LEVEL_SIM'] == DF_In_Process['BADGE_LEVEL_PC']) & (DF_In_Process['PAID_LEVEL_SIM'] > 0))),
        'BADGE_LEVEL_SIM'] = DF_In_Process['PAID_LEVEL_SIM']
        #Grace_Count = 3
    DF_In_Process.loc[
        (DF_In_Process['PAID_LEVEL_SIM'] == Paid_Level_In_Process) 
        &
        ((DF_In_Process['PAID_LEVEL_SIM'] > DF_In_Process['BADGE_LEVEL_PC']) |
        ((DF_In_Process['PAID_LEVEL_SIM'] == DF_In_Process['BADGE_LEVEL_PC']) & (DF_In_Process['PAID_LEVEL_SIM'] > 0))),
        'GRACE_COUNT_SIM'] = Grace_For_Titles
    	# IF (PaidTitle < BadgeTitle_PC) OR (PaidTitle = 0) THEN
            # IF Grace_Count_PC > 0 THEN
                # BadgeTitle = BadgeTitle_PC
    DF_In_Process.loc[
        (DF_In_Process['PAID_LEVEL_SIM'] == Paid_Level_In_Process)
        &
        ((DF_In_Process['PAID_LEVEL_SIM'] < DF_In_Process['BADGE_LEVEL_PC']) | (DF_In_Process['PAID_LEVEL_SIM'] == 0))
        &
        (DF_In_Process['GRACE_COUNT_PC'] > 0),
        'BADGE_LEVEL_SIM'] = DF_In_Process['BADGE_LEVEL_PC']
                # Grace_Count = Grace_Count_PC - 1
    DF_In_Process.loc[
        (DF_In_Process['PAID_LEVEL_SIM'] == Paid_Level_In_Process)
        &        
        ((DF_In_Process['PAID_LEVEL_SIM'] < DF_In_Process['BADGE_LEVEL_PC']) | (DF_In_Process['PAID_LEVEL_SIM'] == 0))
        &
        (DF_In_Process['GRACE_COUNT_PC'] > 0),
        'GRACE_COUNT_SIM'] = DF_In_Process['GRACE_COUNT_PC'] - 1
            # ELIF Grace_Count_PC  = 0 THEN
                # IF BadgeTitle_PC > 1 THEN
                    # BadgeTitle = BadgeTitle_PC - 1
    DF_In_Process.loc[
        (DF_In_Process['PAID_LEVEL_SIM'] == Paid_Level_In_Process)
        &
        ((DF_In_Process['PAID_LEVEL_SIM'] < DF_In_Process['BADGE_LEVEL_PC']) | (DF_In_Process['PAID_LEVEL_SIM'] == 0))
        &
        (DF_In_Process['GRACE_COUNT_PC'] == 0)
        &
        (DF_In_Process['BADGE_LEVEL_PC'] > 1),
        'BADGE_LEVEL_SIM'] = DF_In_Process['BADGE_LEVEL_PC'] - 1        
                    # Grace_Count = 3
    DF_In_Process.loc[
        (DF_In_Process['PAID_LEVEL_SIM'] == Paid_Level_In_Process)
        &
        ((DF_In_Process['PAID_LEVEL_SIM'] < DF_In_Process['BADGE_LEVEL_PC']) | (DF_In_Process['PAID_LEVEL_SIM'] == 0))
        &
        (DF_In_Process['GRACE_COUNT_PC'] == 0)
        &
        (DF_In_Process['BADGE_LEVEL_PC'] > 1),
        'GRACE_COUNT_SIM'] = Grace_For_Titles        
                # ELIF BadgeTitle_PC = 1 THEN
                    # BadgeTitle = BadgeTitle_PC - 1
    DF_In_Process.loc[
        (DF_In_Process['PAID_LEVEL_SIM'] == Paid_Level_In_Process)
        &
        ((DF_In_Process['PAID_LEVEL_SIM'] < DF_In_Process['BADGE_LEVEL_PC']) | (DF_In_Process['PAID_LEVEL_SIM'] == 0))
        &
        (DF_In_Process['GRACE_COUNT_PC'] == 0)
        &
        (DF_In_Process['BADGE_LEVEL_PC'] == 1),
        'BADGE_LEVEL_SIM'] = DF_In_Process['BADGE_LEVEL_PC'] - 1    
                    # Grace_Count = 26
    DF_In_Process.loc[
        (DF_In_Process['PAID_LEVEL_SIM'] == Paid_Level_In_Process)
        &
        ((DF_In_Process['PAID_LEVEL_SIM'] < DF_In_Process['BADGE_LEVEL_PC']) | (DF_In_Process['PAID_LEVEL_SIM'] == 0))
        &
        (DF_In_Process['GRACE_COUNT_PC'] == 0)
        &
        (DF_In_Process['BADGE_LEVEL_PC'] == 1),
        'GRACE_COUNT_SIM'] = Grace_For_Can       
                # ELIF BadgeTitle_PC = 0 THE
                    # REMOVE >>> TAG REMOVED ONES
    
    # THE BLOCK BELOW IDENTIFIES THE BADGE TITLE FOR THOSE WITH NO PRIOR CAMPAIGN DATA.
    # BADGE TITLE = -2 for Reps
    # NOTE THAT THIS BLOCK MUST BE AT THE END OF THE FUNCTION.                
    #IF (BadgeTitle_PC IS NULL OR BadgeTitle_PC = -2) THEN
        #BadgeTitle = PaidTitle
    DF_In_Process.loc[
        (DF_In_Process['PAID_LEVEL_SIM'] == Paid_Level_In_Process) 
        &
        ((DF_In_Process['BADGE_LEVEL_PC'].isnull()) | (DF_In_Process['BADGE_LEVEL_PC'] == -2)),
        'BADGE_LEVEL_SIM'] = DF_In_Process['PAID_LEVEL_SIM']
    #IF (BadgeTitle_PC IS NULL OR BadgeTitle_PC = -2) AND PaidTitle > 0 THEN    
        # Grace Count = 3
    DF_In_Process.loc[
        (DF_In_Process['PAID_LEVEL_SIM'] == Paid_Level_In_Process) 
        &
        ((DF_In_Process['BADGE_LEVEL_PC'].isnull()) | (DF_In_Process['BADGE_LEVEL_PC'] == -2)) & (DF_In_Process['PAID_LEVEL_SIM'] > 0),
        'GRACE_COUNT_SIM'] = Grace_For_Titles
    # IF (BadgeTitle_PC IS NULL OR BadgeTitle_PC = -2) AND PaidTitle = 0 THEN
        #Grace Count = 26
    DF_In_Process.loc[
        (DF_In_Process['PAID_LEVEL_SIM'] == Paid_Level_In_Process) 
        &
        ((DF_In_Process['BADGE_LEVEL_PC'].isnull()) | (DF_In_Process['BADGE_LEVEL_PC'] == -2)) & (DF_In_Process['PAID_LEVEL_SIM'] == 0),
        'GRACE_COUNT_SIM'] = Grace_For_Can

#Define the function to calculate downlines after each title calculation
# If the input for the Higher_Equal parameter is 
    #'equal' calculates the downline count in that badge title
    # 'higherandequal' calculates the downline count in that badge title AND HIGHER 
def update_downlines(DF_In_Process, Badge_Level_In_Process):  
    sl_G1_Dwn = DF_In_Process[(DF_In_Process['BADGE_LEVEL_SIM'] == Badge_Level_In_Process)].groupby(['UPLINE1']).size()
    sl_G1_Dwn = sl_G1_Dwn.to_frame() #the result above is a series. Make it a DF for the upcoming JOIN
    sl_G1_Dwn = sl_G1_Dwn.rename(columns={0: 'G1_' + str(Badge_Level_In_Process)}) #the calculated field is not named. Name it properly
    return sl_G1_Dwn
def topline_calculator(DF_In_Process, campaign_list_input):
    for campy in campaign_list_input:
        #Those with an upline ID as 1, 21 or NULL are in G1 to the house and their TOPLINE ID is themselves (the ehad of the leg)
        DF_In_Process.loc[
            (DF_In_Process['UPLINE_ACCOUNT_NUMBER'].isin([1,21])) | (DF_In_Process['UPLINE_ACCOUNT_NUMBER'].isnull()),
            'GENERATION']= 1
        DF_In_Process.loc[
            (DF_In_Process['UPLINE_ACCOUNT_NUMBER'].isin([1, 21])) | (DF_In_Process['UPLINE_ACCOUNT_NUMBER'].isnull()),
            'TOPLINE_ACCOUNT_NUMBER'] = DF_In_Process['ACCOUNT_NUMBER']

        TOPLINE_df = DF_In_Process[(DF_In_Process['GENERATION'] == 1) & (DF_In_Process['ACCOUNT_NUMBER'] > 500)][['ACCOUNT_NUMBER','BADGE_LEVEL','UPLINE_ACCOUNT_NUMBER','GENERATION']]
        #make the topline the same as the ID for G1
        TOPLINE_df['TOPLINE_ACCOUNT_NUMBER'] = TOPLINE_df['ACCOUNT_NUMBER']

        loopy = 0
        geny = 1
        while loopy == 0:
            # count the number of rows with gen + 1

            gen_count = len(DF_In_Process[DF_In_Process['GENERATION'] == geny])
            if gen_count == 0:
                loopy = 1

            DF_topline_ids_to_become_upline = TOPLINE_df[TOPLINE_df['GENERATION'] == geny]['ACCOUNT_NUMBER']
            DF_to_Join = DF_In_Process[(DF_In_Process['YYYYCC'] == campy) &
                                       (DF_In_Process['UPLINE_ACCOUNT_NUMBER'].isin(DF_topline_ids_to_become_upline))]
            [['ACCOUNT_NUMBER', 'BADGE_LEVEL', 'UPLINE_ACCOUNT_NUMBER']]
            DF_to_Insert = pd.merge(DF_to_Join, TOPLINE_df[['ACCOUNT_NUMBER', 'TOPLINE_ACCOUNT_NUMBER']],
                                    how='left', left_on=['UPLINE_ACCOUNT_NUMBER'], right_on=['ACCOUNT_NUMBER'])
            DF_to_Insert = DF_to_Insert[
                ['ACCOUNT_NUMBER_x', 'BADGE_LEVEL', 'UPLINE_ACCOUNT_NUMBER', 'TOPLINE_ACCOUNT_NUMBER_y']]
            DF_to_Insert.rename(
                columns={'ACCOUNT_NUMBER_x': 'ACCOUNT_NUMBER', 'TOPLINE_ACCOUNT_NUMBER_y': 'TOPLINE_ACCOUNT_NUMBER'},
                inplace=True)
            DF_to_Insert['GENERATION'] = geny + 1
            TOPLINE_df = pd.concat([TOPLINE_df, DF_to_Insert])

            #TOPLINE_df.head()
            #print('gen = 1 items')
            #TOPLINE_df[TOPLINE_df['GENERATION'] == 1]['TOPLINE_ACCOUNT_NUMBER'].head()
            for toppy in TOPLINE_df[TOPLINE_df['GENERATION'] == geny]['TOPLINE_ACCOUNT_NUMBER'].drop_duplicates(
                    inplace=False).sort_values():
                print("topline: %d: " % (toppy))
                counter = 0
                for i in TOPLINE_df[(TOPLINE_df['GENERATION'] == geny) & (TOPLINE_df['TOPLINE_ACCOUNT_NUMBER'] == toppy)][
                    'ACCOUNT_NUMBER'].sort_values():
                    counter = counter + 1
                    DF_In_Process.loc[
                        DF_In_Process['UPLINE_ACCOUNT_NUMBER'] == i,
                        'GENERATION'] = geny + 1
                    DF_In_Process.loc[
                        DF_In_Process['UPLINE_ACCOUNT_NUMBER'] == i,
                        'TOPLINE_ACCOUNT_NUMBER'] = toppy
                    #print("topline: %d id: %d generation: %d counter: %d" % (toppy, i, geny, counter))
            geny = geny + 1

def Upline_By_G_To_House(DF_In_Process, campaign_list_input):
    camp_counter = 0
    for campy in campaign_list_input:
        camp_counter = camp_counter + 1
        # Get the max generation for your loop
        gen_max = DF_In_Process['GENERATION'].max()
        DF_uplines = DF_In_Process[['ACCOUNT_NUMBER', 'UPLINE_ACCOUNT_NUMBER']]
        DF_uplines = DF_uplines.rename(columns={"UPLINE_ACCOUNT_NUMBER": "UPLINE1"})
        column_dict = {'ACCOUNT_NUMBER_x': 'ACCOUNT_NUMBER'}
        for g in range(2, int(gen_max) + 1):
            column_dict['UPLINE' + str(g - 1) + '_x'] = 'UPLINE' + str(g - 1)
            column_dict['UPLINE1_y'] = 'UPLINE' + str(g)
            DF_uplines = pd.merge(DF_uplines, DF_uplines[['ACCOUNT_NUMBER', 'UPLINE1']],
                                  how='left', left_on=['UPLINE' + str(g - 1)], right_on=['ACCOUNT_NUMBER'])
            DF_uplines = DF_uplines.drop(['ACCOUNT_NUMBER_y'],
                                         axis=1)  # DF_uplines[['ACCOUNT_NUMBER_x', 'UPLINE'+str(g-1)+'_x', 'UPLINE'+str(g-1)+'_y']]
            DF_uplines = DF_uplines.rename(columns=column_dict)
            # columns={'ACCOUNT_NUMBER_x': 'ACCOUNT_NUMBER', 'UPLINE'+str(g-1)+'_x': 'UPLINE'+str(g-1), 'UPLINE1_y': 'UPLINE' + str(g)})

        for g in range(int(gen_max), 0, -1):  # loop in reverse order: includes the max gen and stops after iterating over 1
            for u in range(1, g):  # 1 - 2- 3 - 4
                # print("g: %d, u: %d" % (g, u))
                DF_uplines.loc[DF_uplines['UPLINE' + str(g)] == 1, 'G' + str(int(g - u)) + '_TO_HOUSE_UPLINE'] = DF_uplines[
                    'UPLINE' + str(u + 1)]

        DF_In_Process.set_index(['ACCOUNT_NUMBER'], inplace=True)
        DF_uplines.set_index(['ACCOUNT_NUMBER'], inplace=True)
        DF_In_Process = pd.merge(DF_In_Process, DF_uplines, how='left', left_index=True, right_index=True)

        if camp_counter == 1:
            DF_temp = pd.DataFrame().reindex_like(DF_In_Process)
        DF_temp = pd.concat([DF_temp, DF_In_Process])

    return DF_temp

# ==========================FUNCTIONS=============================================
# =============================================================================
# MAIN CALCULATION BLOCK
# =============================================================================
def diviner():
    ## IMPORT REP DATA
    #fields = ['YYYYCC', 'ACCOUNT_NUMBER', 'ACCOUNT_KEY', 'STATUS_CODE', 'DISTRICT_NUMBER', 'DIVISION_NAME', 'UPLINE_ACCOUNT_NUMBER',
    #  'LOA', 'QV', 'CV', 'BAD_DEBT', 'PAID_LEVEL', 'BADGE_LEVEL', 'BADGE_LEVEL_PC', 'GRACE_COUNT', 'GRACE_COUNT_PC']
    #rep_data = pd.read_csv('C:/Users/Public/Documents/Python Scripts/rep_data3_status_1_6.tsv',sep='\t')
    #rep_data = pd.read_csv('C:/Users/gurkaali/Documents/AL Deep Dive/AL Simulator/rep_data2_single_campaign.tsv', sep='\t')

    rep_data = pd.read_csv(en_browse_input.get(), sep='\t')
    rep_data = rep_data.loc[rep_data['STATUS_CODE'].isin([2, 3])]

    #make all null uplines = 1 i.e. the HOUSE
    rep_data.loc[(rep_data['UPLINE_ACCOUNT_NUMBER'] <= 21) | (rep_data['UPLINE_ACCOUNT_NUMBER'].isnull()), 'UPLINE_ACCOUNT_NUMBER'] = 1

    campaign_list = rep_data['YYYYCC'].unique()
    campaign_list.sort()

    #Calculate toplines (person at the top of the leg) & generations!!!!!!!!!!!!
    topline_calculator(rep_data, campaign_list)
    rep_data = Upline_By_G_To_House(rep_data, campaign_list)

    #show column names for check:
    for c in list(rep_data):
        print(c)

    #for practical purposes
    rep_data.to_csv('C:/Users/gurkaali/Desktop/output_rep_dataframe', sep='\t', encoding='utf-8')
    print('DONE for now')

    if EntryStatusNesting.get():
        rep_data['Nested_To_SL'] = 0
        rep_data['Nesting_Campaign'] = 0

    # Create the 1st campaign's dataframe
    rep_dict = {}
    sl_dict = {}
    #rep_dict[1] is the df for your first campaign in the imported table
    #iterate over campaigns you had sorted in alist up above. 
    #for loop's iteration order is controlled by whatever object it's iterating over. 
    #Iterating over an ordered collection like a list is guaranteed to iterate over elements in the list's order, 
    #but iterating over an unordered collection like a set makes almost no order guarantees
    for c in range(1,len(campaign_list)+1):
        print('Campaign in process:', c)
        #for the first campaign data you must keep the Prior Campaign Grace Count and Badge Title info
        #for the following campaigns you will use the simulation values of the prior campaign
        if c == 1:
            rep_dict[c] = rep_data[rep_data['YYYYCC']==campaign_list[c-1]]
            #rep_dict[c].set_index(['ACCOUNT_NUMBER'], inplace = True) #change index to the Rep ID
            #print(rep_dict[c].index.name)

        else:
            rep_temp = rep_data[rep_data['YYYYCC']==campaign_list[c-1]]
            rep_temp.set_index(['ACCOUNT_NUMBER'], inplace = True) #change index to the Rep ID
            del rep_temp['BADGE_LEVEL_PC']
            del rep_temp['GRACE_COUNT_PC']
            rep_temp_2 = pd.merge(rep_temp, sl_dict[c-1][['BADGE_LEVEL_SIM','GRACE_COUNT_SIM']], left_index=True, right_index=True, how='left')
            rep_temp_2 = rep_temp_2.rename(columns={'BADGE_LEVEL_SIM': 'BADGE_LEVEL_PC', 'GRACE_COUNT_SIM': 'GRACE_COUNT_PC'})

            # if nesting is selected, the upline of some reps have been updated for the previous campaign. Copy"em
            if EntryStatusNesting.get():
                # get a list of all nested Reps from the PC (including those nested in earlier campaigns)
                nested_before = rep_dict[c-1][(rep_dict[c-1]['Nested_To_SL'] == 1)]
                nested_before_rep_list = nested_before.index.values # index column is the ACCOUNT_NUMBER field
                for nn in nested_before_rep_list:
                    #print('PC Nested Rep Data being copied for Rep: ', nn)
                    # in case the Rep is removed in the current C, move on to the next one
                    if nn not in rep_temp_2.index:
                        continue
                    nested_pc_details = nested_before.loc[nn]  # this gives a one row series
                    # set the values within the current campaign for the Rep being processed - Rep info is in the index field of the table(in the rep_temp2 table)
                    rep_temp_2.loc[nn, ['Nesting_Campaign']] = nested_pc_details['Nesting_Campaign']
                    rep_temp_2.loc[nn, ['Nested_To_SL']] = nested_pc_details['Nested_To_SL']
                    # Check if the upline in PC is present as SL in this C
                    upline1_pc = nested_pc_details['UPLINE']
                    upline2_pc = nested_pc_details['UPLINE2']
                    upline3_pc = nested_pc_details['UPLINE3']
                    upline1_pc = int(upline1_pc) if np.isnan(upline1_pc) == False else upline1_pc
                    upline2_pc = int(upline2_pc) if np.isnan(upline2_pc) == False else upline2_pc
                    upline3_pc = int(upline3_pc) if np.isnan(upline3_pc) == False else upline3_pc
                    # Assign the titles as Rep by default. You will retrieve them only when the upline ID > 1 (i.e. not the house)
                    # so for a leader id = 1 the ifelif-else block further below gives an error if you do not make this assignment
                    upline1_pc_title = -1
                    upline2_pc_title = -1
                    upline3_pc_title = -1
                    #print('upline:', upline1_pc)
                    if upline1_pc > 1:
                        if upline1_pc in rep_temp_2.index:
                            upline1_pc_title = rep_temp_2.loc[int(upline1_pc), ['BADGE_LEVEL']]
                    if upline2_pc > 1:
                        if upline2_pc in rep_temp_2.index:
                            upline2_pc_title = rep_temp_2.loc[int(upline2_pc), ['BADGE_LEVEL']]
                    if upline3_pc > 1:
                        if upline3_pc in rep_temp_2.index:
                            upline3_pc_title = rep_temp_2.loc[int(upline3_pc), ['BADGE_LEVEL']]
                    # Assign the same Upline in current Campaign if she is still a leader.
                    if upline1_pc in rep_temp_2.index:
                        rep_temp_2.loc[nn, ['UPLINE_ACCOUNT_NUMBER']] = upline1_pc
                    else:
                        upline_to_be = 0
                        if upline2_pc == 1:
                            upline_to_be = upline2_pc
                        elif upline2_pc > 1:
                            if (upline2_pc_title.item() >= 0 and upline2_pc in rep_temp_2.index):
                                upline_to_be = upline2_pc
                            else:
                                upline_to_be = upline3_pc
                        rep_temp_2.loc[nn, [
                            'UPLINE_ACCOUNT_NUMBER']] = upline_to_be  # in the very unlikely/rare event that all 3 uplines are removed assign the Rep to the house. for estimation purposes that is fine

            rep_dict[c] = rep_temp_2

        # IF NESTING IS TO BE APPLIED
        if EntryStatusNesting.get():
            # find eligible leaders: title gr than or eq to 1
            sl_potential = rep_data[(rep_data['YYYYCC'] == campaign_list[c - 1]) & (rep_data['PAID_LEVEL'] >= 1)]
            sl_potential = sl_potential[['ACCOUNT_NUMBER','DISTRICT_NUMBER','PAID_LEVEL']]
            sl_potential_districts = sl_potential['DISTRICT_NUMBER'].unique() # sl_potential_districts is an array
            nesty_reps = rep_dict[c]
            pd.options.mode.chained_assignment = None # default='warn' # to awoid the SettingWithCopyWarning
            #nesty_reps['Nested_To_SL'] = 0 # use this column to tag nested Reps (as 1)
            for d in sl_potential_districts: #.sort('DISTRICT_NUMBER'):
                print('The district for which the nesting is being conducted: ', d)
                #loop only through Reps without a leader + who herself is not a leader + in district d
                nesty_reps_d = nesty_reps[(nesty_reps['DISTRICT_NUMBER'] == d) &
                                          (nesty_reps['BADGE_LEVEL'] < 0) & #0 is for Candidates
                                          (nesty_reps['UPLINE_ACCOUNT_NUMBER'] == 1) &
                                          (nesty_reps['TIER_LEVEL'].isin([10, 20]))] #10: New, 20: Bronze, 30: Silver, Gold: 40, 50: PC, 60: HS, 70: DHM, 80: PCC
                nesty_reps_d_list = nesty_reps_d.index.values.tolist()  # this gives the index column ONLY
                #print('Number of Reps waiting to be nested: ', len(nesty_reps_d_list))
                # get the number of eligible SLs in that district
                sl_eligible_count = len(sl_potential[(sl_potential['DISTRICT_NUMBER'] == d)])
                sl_eligible_d = sl_potential[(sl_potential['DISTRICT_NUMBER'] == d)]
                sl_eligible_d_list = sl_eligible_d['ACCOUNT_NUMBER'].values.tolist()
                eligible_sl_count = len(sl_eligible_d_list)

                nested_rep_count = 0
                for n in nesty_reps_d_list:
                    if nested_rep_count >= nesty_rep_limit.get() * eligible_sl_count: # nesty_rep_limit is the max number of Reps that can be nested to a leader in a campaign
                        break
                    else:
                        nesty_reps.loc[n, ['UPLINE_ACCOUNT_NUMBER']] = sl_eligible_d_list[nested_rep_count % eligible_sl_count]
                        nesty_reps.loc[n, ['Nested_To_SL']] = 1
                        nesty_reps.loc[n, ['Nesting_Campaign']] = campaign_list[c-1]
                        #print('the number of nestings conducted in this district until now: ', nested_rep_count)
                        nested_rep_count = nested_rep_count + 1

            rep_dict[c] = nesty_reps
    ## =============================================================================
        # ## CALCULATE UPLINE 2 & 3
        # #Upline 2
        # rep_copy = rep_dict[c][['UPLINE_ACCOUNT_NUMBER']]
        # rep_2 = pd.merge(rep_dict[c], rep_copy, left_on='UPLINE_ACCOUNT_NUMBER', right_index=True, how='left')
        # rep_2.rename(columns = {'UPLINE_ACCOUNT_NUMBER_x':'UPLINE','UPLINE_ACCOUNT_NUMBER_y' : 'UPLINE2'}, inplace = True)
        # #Upline 3
        # rep_3 = pd.merge(rep_2, rep_copy, left_on='UPLINE2', right_index=True, how='left')
        # rep_3.rename(columns = {'UPLINE_ACCOUNT_NUMBER':'UPLINE3'}, inplace = True)
        # rep_dict[c] = rep_3
        rep_3 = rep_dict[c] #with the new function calculating ALL uplines the block above is replaced by this line
    ## =============================================================================
    ## =============================================================================
    ## TAKE ONLY SLs
        sl_1 = rep_3[(rep_3['BADGE_LEVEL'] >= 0) & (rep_3['STATUS_CODE'].isin([2, 3]))] #Badge_Level = 0 >>> CAN
        #NOTE THAT Some uplines are strangely in status other than 2 & 3 and yet remain Leader. They are excluded
    # =============================================================================
    # =============================================================================
        # CALCULATE ACTIVES
        #Actives with positive QV
        sl_G1Active = rep_3[(rep_3['QV'] > 0)].groupby(['UPLINE1']).size()
        sl_G1Active=sl_G1Active.to_frame() #the result above is a series. Make it a DF for the upcoming JOIN
        sl_G1Active=sl_G1Active.rename(columns={0: 'G1Actives'}) #the calculated field is not named. Name it properly
    
        #Actives with 50+ QV »»» For FT Bonus
        sl_G1Active_FT = rep_3[(rep_3['QV'] >= en_rep_sales.get())].groupby(['UPLINE1']).size()
        sl_G1Active_FT = sl_G1Active_FT.to_frame() 
        sl_G1Active_FT = sl_G1Active_FT.rename(columns={0: 'G1Actives_forFT'}) 
    
        #Actives with 100+ QV »»» For QPA 1
        sl_G1Active_QPA1 = rep_3[(rep_3['QV'] >= 100) & (rep_3['LOA'] == 1)].groupby(['UPLINE1']).size()
        sl_G1Active_QPA1 = sl_G1Active_QPA1.to_frame() 
        sl_G1Active_QPA1 = sl_G1Active_QPA1.rename(columns={0: 'G1Actives_forQPA1'}) 
    
        #Actives with 125+ QV »»» For QPA 2
        sl_G1Active_QPA2 = rep_3[(rep_3['QV'] >= 125) & (rep_3['LOA'] == 2)].groupby(['UPLINE1']).size()
        sl_G1Active_QPA2 = sl_G1Active_QPA2.to_frame() 
        sl_G1Active_QPA2 = sl_G1Active_QPA2.rename(columns={0: 'G1Actives_forQPA2'}) 
    
        #Actives with 150+ QV »»» For QPA 3
        sl_G1Active_QPA3 = rep_3[(rep_3['QV'] >= 150) & (rep_3['LOA'] == 3)].groupby(['UPLINE1']).size()
        sl_G1Active_QPA3 = sl_G1Active_QPA3.to_frame() 
        sl_G1Active_QPA3 = sl_G1Active_QPA3.rename(columns={0: 'G1Actives_forQPA3'}) 
    # =============================================================================
    # =============================================================================
        # CALCULATE G-BASED SALES
        #G1 CV_base - Only CVs of those with QV >= $50 are included.
        #Note that if QV <= -50, the associated neg CV would yield neg commission as well
        sl_G1_CV = rep_3[(rep_3['QV'] >= en_rep_sales.get()) | (rep_3['QV'] <= -en_rep_sales.get())].groupby(['UPLINE1']).agg({'CV':np.sum})
        sl_G1_CV = sl_G1_CV.rename(columns={'CV': 'G1_CV'})
    
        #G1 QV For Team Sales
        sl_G1_QV = rep_3.groupby(['UPLINE1']).agg({'QV':np.sum})
        sl_G1_QV = sl_G1_QV.rename(columns={'QV': 'G1_QV'})
    
        #G2 CV_base - Only CVs of those with QV >= $50 are included.
        sl_G2_CV = rep_3[(rep_3['QV'] >= en_rep_sales.get()) | (rep_3['QV'] <= -en_rep_sales.get())].groupby(['UPLINE2']).agg({'CV':np.sum})
        sl_G2_CV = sl_G2_CV.rename(columns={'CV': 'G2_CV'})

        #G2 QV For Team Sales
        sl_G2_QV = rep_3.groupby(['UPLINE2']).agg({'QV':np.sum})
        sl_G2_QV = sl_G2_QV.rename(columns={'QV': 'G2_QV'})
    
        #G3 CV_base - Only CVs of those with QV >= $50 are included.
        sl_G3_CV = rep_3[(rep_3['QV'] >= en_rep_sales.get()) | (rep_3['QV'] <= -en_rep_sales.get())].groupby(['UPLINE3']).agg({'CV':np.sum})
        sl_G3_CV = sl_G3_CV.rename(columns={'CV': 'G3_CV'})
        
        #G3 QV For Team Sales
        sl_G3_QV = rep_3.groupby(['UPLINE3']).agg({'QV':np.sum})
        sl_G3_QV = sl_G3_QV.rename(columns={'QV': 'G3_QV'})
    
        #G1 Downline Count (regardless the title)
        sl_G1Downlines = sl_1.groupby(['UPLINE1']).size()
        sl_G1Downlines = sl_G1Downlines.to_frame()
        sl_G1Downlines = sl_G1Downlines.rename(columns={0: 'G1_ALL'})

        # CALCULATE EXECUTIVE G-BASED BAD DEBT: For Commission Calculation



        # CALCULATE G-BASED BAD DEBT: For Commission Calculation
        #Bad debt related commissions are deducted from commission calculation for every rep with a bad debt amount >= 50CAD
        #G1 QV For Commission Calculation
        sl_G1_BAD = rep_3[((rep_3['BAD_DEBT'] >= en_rep_sales.get()) | (rep_3['BAD_DEBT'] <= -en_rep_sales.get()))].groupby(['UPLINE1']).agg({'BAD_DEBT':np.sum})
        sl_G1_BAD = sl_G1_BAD.rename(columns={'BAD_DEBT': 'G1_BAD'})
    
        #G2 QV For Commission Calculation
        sl_G2_BAD = rep_3[((rep_3['BAD_DEBT'] >= en_rep_sales.get()) | (rep_3['BAD_DEBT'] <= -en_rep_sales.get()))].groupby(['UPLINE2']).agg({'BAD_DEBT':np.sum})
        sl_G2_BAD = sl_G2_BAD.rename(columns={'BAD_DEBT': 'G2_BAD'})
    
        #G3 QV For Commission Calculation
        sl_G3_BAD = rep_3[((rep_3['BAD_DEBT'] >= en_rep_sales.get()) | (rep_3['BAD_DEBT'] <= -en_rep_sales.get()))].groupby(['UPLINE3']).agg({'BAD_DEBT':np.sum})
        sl_G3_BAD = sl_G3_BAD.rename(columns={'BAD_DEBT': 'G3_BAD'})


    # =============================================================================
    # =============================================================================
        # GATHER FIELDS
        sl_2 = pd.merge(sl_1, sl_G1Active, left_index=True, right_index=True, how='left') 
        sl_3 = pd.merge(sl_2, sl_G1Active_FT, left_index=True, right_index=True, how='left')
        sl_4 = pd.merge(sl_3, sl_G1Active_QPA1, left_index=True, right_index=True, how='left')
        sl_5 = pd.merge(sl_4, sl_G1Active_QPA2, left_index=True, right_index=True, how='left')
        sl_6 = pd.merge(sl_5, sl_G1Active_QPA3, left_index=True, right_index=True, how='left') 
        sl_7 = pd.merge(sl_6, sl_G1_CV, left_index=True, right_index=True, how='left')
        sl_8 = pd.merge(sl_7, sl_G1_QV, left_index=True, right_index=True, how='left')
        sl_9 = pd.merge(sl_8, sl_G2_CV, left_index=True, right_index=True, how='left')
        sl_10 = pd.merge(sl_9, sl_G2_QV, left_index=True, right_index=True, how='left')
        sl_11 = pd.merge(sl_10, sl_G3_CV, left_index=True, right_index=True, how='left')
        sl_12 = pd.merge(sl_11, sl_G3_QV, left_index=True, right_index=True, how='left')
        sl_13 = pd.merge(sl_12, sl_G1Downlines, left_index=True, right_index=True, how='left')
        sl_14 = pd.merge(sl_13, sl_G1_BAD, left_index=True, right_index=True, how='left')
        sl_15 = pd.merge(sl_14, sl_G2_BAD, left_index=True, right_index=True, how='left')
        sl_16 = pd.merge(sl_15, sl_G3_BAD, left_index=True, right_index=True, how='left')
    
        #Replace NULL values with 0
        # I'm using inplace=True to actually change the contents of df.
        sl_16.update(sl_16[['G1Actives', 'G1Actives_forFT',
                              'G1Actives_forQPA1', 'G1Actives_forQPA2', 'G1Actives_forQPA3',
                              'G1_CV','G2_CV', 'G3_CV', 'G1_QV', 'G2_QV', 'G3_QV', 'G1_ALL',
                              'G1_BAD', 'G2_BAD', 'G3_BAD']].fillna(0))  # null values cause the sums to be null when included in calculation

    
        #Calculate Team Sales (TS)
        sl_16['TS'] = sl_16['QV'] + sl_16['G1_QV'] + sl_16['G2_QV'] + sl_16['G3_QV']
        
    # =============================================================================
    # =============================================================================
        # CALCULATE TITLES              
        #Set T0 (Candidates)
        sl_16.loc[
            (sl_16['QV'] < Entries_PS_Dict[1].get()) |  
            (sl_16['TS'] < Entries_TS_Dict[1].get()) | 
            (sl_16['G1Actives'] < Entries_G1Act_Dict[1].get()), 
            'PAID_LEVEL_SIM'] = 0
    
        #update_badges_graces_onerole
        update_badge_grace(sl_16,0,26,3)
    
        #update_downlines: get G1 T0 count
        Calculated_G1_0 = update_downlines(sl_16, 0) #1st Zero: For titles equal to CAN; 2nd 0 for downlines equal to 0 (not greater than or equal to 0)
        #join the downline titled count with the main table
        sl_17 = pd.merge(sl_16, Calculated_G1_0, left_index=True, right_index=True, how='left')
        #set downline count 0 for null values
        sl_17['G1_0'].fillna(0, inplace=True)
    
        #Set T1
        sl_17.loc[
                ((sl_17['QV'] >= Entries_PS_Dict[1].get()) &  
                (sl_17['TS'] >= Entries_TS_Dict[1].get()) & 
                (sl_17['G1Actives'] >= Entries_G1Act_Dict[1].get()))
                &
                ((sl_17['QV'] < Entries_PS_Dict[2].get()) |
                (sl_17['TS'] < Entries_TS_Dict[2].get()) |
                (sl_17['G1Actives'] < Entries_G1Act_Dict[2].get()) |
                (sl_17['G1_ALL'] - sl_17['G1_0'] < Entries_Dwn_Dict[2][1].get())), #T1 downline requirement for T2
                'PAID_LEVEL_SIM'] = 1
        #update_badges_graces_onerole
        update_badge_grace(sl_17,1,26,3)
    
        #update_downlines
        Calculated_G1_1 = update_downlines(sl_17, 1)
        #join the downline titled count with the main table
        sl_18 = pd.merge(sl_17, Calculated_G1_1, left_index=True, right_index=True, how='left')
        #set downline count 0 for null values
        sl_18['G1_1'].fillna(0, inplace=True)
    
        #Set T2
        sl_18.loc[
                ((sl_18['QV'] >= Entries_PS_Dict[2].get()) &  
                (sl_18['TS'] >= Entries_TS_Dict[2].get()) & 
                (sl_18['G1Actives'] >= Entries_G1Act_Dict[2].get()) &
                (sl_18['G1_ALL'] - sl_18['G1_0'] >= Entries_Dwn_Dict[2][1].get())) #T1 downline requirement for T2
                &
                ((sl_18['QV'] < Entries_PS_Dict[3].get()) |
                (sl_18['TS'] < Entries_TS_Dict[3].get()) | 
                (sl_18['G1Actives'] < Entries_G1Act_Dict[3].get()) |
                (sl_18['G1_ALL'] - sl_18['G1_0'] < (Entries_Dwn_Dict[3][1].get() + Entries_Dwn_Dict[3][2].get())) | #T1-2 downline requirement for T3
                (sl_18['G1_ALL'] - sl_18['G1_0'] - sl_18['G1_1'] < Entries_Dwn_Dict[3][2].get())), #T2 downline requirement for T3
                'PAID_LEVEL_SIM'] = 2
        #update_badges_graces_onerole
        update_badge_grace(sl_18,2,26,3)
    
        #update_downlines
        Calculated_G1_2 = update_downlines(sl_18, 2)
        #join the downline titled count with the main table
        sl_19 = pd.merge(sl_18, Calculated_G1_2, left_index=True, right_index=True, how='left')
        #set downline count 0 for null values
        sl_19['G1_2'].fillna(0, inplace=True)
    
        #Set T3
        sl_19.loc[
                ((sl_19['QV'] >= Entries_PS_Dict[3].get()) &  
                (sl_19['TS'] >= Entries_TS_Dict[3].get()) & 
                (sl_19['G1Actives'] >= Entries_G1Act_Dict[3].get()) &
                (sl_19['G1_ALL'] - sl_19['G1_0'] >= (Entries_Dwn_Dict[3][1].get() + Entries_Dwn_Dict[3][2].get()) ) & #T1-2 downline requirement for T3
                (sl_19['G1_ALL'] - sl_19['G1_0'] - sl_19['G1_1'] >= Entries_Dwn_Dict[3][2].get())) #T2 downline requirement for T3
                &
                ((sl_19['QV'] < Entries_PS_Dict[4].get()) |
                (sl_19['TS'] < Entries_TS_Dict[4].get()) | 
                (sl_19['G1Actives'] < Entries_G1Act_Dict[4].get()) |
                (sl_19['G1_ALL'] - sl_19['G1_0'] < (Entries_Dwn_Dict[4][1].get() + Entries_Dwn_Dict[4][2].get() + Entries_Dwn_Dict[4][3].get())) | #T1-2-3 downline requirement for T4
                (sl_19['G1_ALL'] - sl_19['G1_0'] - sl_19['G1_1'] < (Entries_Dwn_Dict[4][2].get() + Entries_Dwn_Dict[4][3].get())) | #T2-3 downline requirement for T4
                (sl_19['G1_ALL'] - sl_19['G1_0'] - sl_19['G1_1'] - sl_19['G1_2'] < Entries_Dwn_Dict[4][3].get())), #T3 downline requirement for T4
                'PAID_LEVEL_SIM'] = 3 #ATTENTION
        #update_badges_graces_onerole
        update_badge_grace(sl_19,3,26,3)
    
        #update_downlines
        Calculated_G1_3 = update_downlines(sl_19, 3) #ATTENTION
        #join the downline titled count with the main table
        sl_20 = pd.merge(sl_19, Calculated_G1_3, left_index=True, right_index=True, how='left')
        #set downline count 0 for null values
        sl_20['G1_3'].fillna(0, inplace=True) #ATTENTION
    
        #Set T4
        sl_20.loc[
                ((sl_20['QV'] >= Entries_PS_Dict[4].get()) &  
                (sl_20['TS'] >= Entries_TS_Dict[4].get()) & 
                (sl_20['G1Actives'] >= Entries_G1Act_Dict[4].get()) &
                (sl_20['G1_ALL'] - sl_20['G1_0'] >= (Entries_Dwn_Dict[4][1].get() + Entries_Dwn_Dict[4][2].get() + Entries_Dwn_Dict[4][3].get())) & #T1-2-3 downline requirement for T4
                (sl_20['G1_ALL'] - sl_20['G1_0'] - sl_20['G1_1'] >= (Entries_Dwn_Dict[4][2].get() + Entries_Dwn_Dict[4][3].get())) & #T2-3 downline requirement for T4
                (sl_20['G1_ALL'] - sl_20['G1_0'] - sl_20['G1_1']  - sl_20['G1_2'] >= Entries_Dwn_Dict[4][3].get())) #T3 downline requirement for T4
                &
                ((sl_20['QV'] < Entries_PS_Dict[5].get()) |
                (sl_20['TS'] < Entries_TS_Dict[5].get()) | 
                (sl_20['G1Actives'] < Entries_G1Act_Dict[5].get()) |
                (sl_20['G1_ALL'] - sl_20['G1_0'] < (Entries_Dwn_Dict[5][1].get() + Entries_Dwn_Dict[5][2].get() + Entries_Dwn_Dict[5][3].get() + Entries_Dwn_Dict[5][4].get())) | #T1-2-3-4 downline requirement for T5
                (sl_20['G1_ALL'] - sl_20['G1_0'] - sl_20['G1_1'] < (Entries_Dwn_Dict[5][2].get() + Entries_Dwn_Dict[5][3].get() + Entries_Dwn_Dict[5][4].get())) | #T2-3-4 downline requirement for T5
                (sl_20['G1_ALL'] - sl_20['G1_0'] - sl_20['G1_1'] - sl_20['G1_2'] < (Entries_Dwn_Dict[5][3].get() + Entries_Dwn_Dict[5][4].get())) | #T3-4 downline requirement for T5
                (sl_20['G1_ALL'] - sl_20['G1_0'] - sl_20['G1_1'] - sl_20['G1_2'] - sl_20['G1_3'] < Entries_Dwn_Dict[5][4].get())), #T4 downline requirement for T5
                'PAID_LEVEL_SIM'] = 4 #ATTENTION
        #update_badges_graces_onerole
        update_badge_grace(sl_20,4,26,3) #ATTENTION
    
        #update_downlines
        Calculated_G1_4 = update_downlines(sl_20, 4) #ATTENTION
        #join the downline titled count with the main table
        sl_21 = pd.merge(sl_20, Calculated_G1_4, left_index=True, right_index=True, how='left')
        #set downline count 0 for null values
        sl_21['G1_4'].fillna(0, inplace=True) #ATTENTION
    
        #Set T5
        sl_21.loc[
                ((sl_21['QV'] >= Entries_PS_Dict[5].get()) &  
                (sl_21['TS'] >= Entries_TS_Dict[5].get()) & 
                (sl_21['G1Actives'] >= Entries_G1Act_Dict[5].get()) &
                (sl_21['G1_ALL'] - sl_21['G1_0'] >= (Entries_Dwn_Dict[5][1].get() + Entries_Dwn_Dict[5][2].get() + Entries_Dwn_Dict[5][3].get() + Entries_Dwn_Dict[5][4].get())) & #T1-2-3-4 downline requirement for T5
                (sl_21['G1_ALL'] - sl_21['G1_0'] - sl_21['G1_1'] >= (Entries_Dwn_Dict[5][2].get() + Entries_Dwn_Dict[5][3].get() + Entries_Dwn_Dict[5][4].get())) & #T2-3-4 downline requirement for T5
                (sl_21['G1_ALL'] - sl_21['G1_0'] - sl_21['G1_1']  - sl_21['G1_2'] >= (Entries_Dwn_Dict[5][3].get() + Entries_Dwn_Dict[5][4].get())) & #T3-4 downline requirement for T5
                (sl_21['G1_ALL'] - sl_21['G1_0'] - sl_21['G1_1']  - sl_21['G1_2'] - sl_21['G1_3'] >= Entries_Dwn_Dict[5][4].get())) #T4 downline requirement for T5
                &
                ((sl_21['QV'] < Entries_PS_Dict[6].get()) |
                (sl_21['TS'] < Entries_TS_Dict[6].get()) | 
                (sl_21['G1Actives'] < Entries_G1Act_Dict[6].get()) |
                (sl_21['G1_ALL'] - sl_21['G1_0'] < (Entries_Dwn_Dict[6][1].get() + Entries_Dwn_Dict[6][2].get() + Entries_Dwn_Dict[6][3].get() + Entries_Dwn_Dict[6][4].get() + Entries_Dwn_Dict[6][5].get())) | #T1-2-3-4-5 downline requirement for T6
                (sl_21['G1_ALL'] - sl_21['G1_0'] - sl_21['G1_1'] < (Entries_Dwn_Dict[6][2].get() + Entries_Dwn_Dict[6][3].get() + Entries_Dwn_Dict[6][4].get() + Entries_Dwn_Dict[6][5].get())) | #T2-3-4-5 downline requirement for T6
                (sl_21['G1_ALL'] - sl_21['G1_0'] - sl_21['G1_1'] - sl_21['G1_2'] < (Entries_Dwn_Dict[6][3].get() + Entries_Dwn_Dict[6][4].get() + Entries_Dwn_Dict[6][5].get())) | #T3-4-5 downline requirement for T6
                (sl_21['G1_ALL'] - sl_21['G1_0'] - sl_21['G1_1'] - sl_21['G1_2'] - sl_21['G1_3'] < (Entries_Dwn_Dict[6][4].get() + Entries_Dwn_Dict[6][5].get())) | #T4-5 downline requirement for T6
                (sl_21['G1_ALL'] - sl_21['G1_0'] - sl_21['G1_1'] - sl_21['G1_2'] - sl_21['G1_3'] - sl_21['G1_4'] < Entries_Dwn_Dict[6][5].get())), #T5 downline requirement for T6
                'PAID_LEVEL_SIM'] = 5 #ATTENTION
        #update_badges_graces_onerole
        update_badge_grace(sl_21,5,26,3) #ATTENTION
    
        #update_downlines
        Calculated_G1_5 = update_downlines(sl_21, 5) #ATTENTION
        #join the downline titled count with the main table
        sl_22 = pd.merge(sl_21, Calculated_G1_5, left_index=True, right_index=True, how='left')
        #set downline count 0 for null values
        sl_22['G1_5'].fillna(0, inplace=True) #ATTENTION
    
        #Set T6
        sl_22.loc[
                ((sl_22['QV'] >= Entries_PS_Dict[6].get()) &  
                (sl_22['TS'] >= Entries_TS_Dict[6].get()) & 
                (sl_22['G1Actives'] >= Entries_G1Act_Dict[6].get()) &
                (sl_22['G1_ALL'] - sl_22['G1_0'] >= (Entries_Dwn_Dict[6][1].get() + Entries_Dwn_Dict[6][2].get() + Entries_Dwn_Dict[6][3].get() + Entries_Dwn_Dict[6][4].get() + Entries_Dwn_Dict[6][5].get())) & #T1-2-3-4-5 downline requirement for T6
                (sl_22['G1_ALL'] - sl_22['G1_0'] - sl_22['G1_1'] >= (Entries_Dwn_Dict[6][2].get() + Entries_Dwn_Dict[6][3].get() + Entries_Dwn_Dict[6][4].get() + Entries_Dwn_Dict[6][5].get())) & #T2-3-4-5 downline requirement for T6
                (sl_22['G1_ALL'] - sl_22['G1_0'] - sl_22['G1_1']  - sl_22['G1_2'] >= (Entries_Dwn_Dict[6][3].get() + Entries_Dwn_Dict[6][4].get() + Entries_Dwn_Dict[6][5].get())) & #T3-4-5 downline requirement for T6
                (sl_22['G1_ALL'] - sl_22['G1_0'] - sl_22['G1_1']  - sl_22['G1_2'] - sl_22['G1_3'] >= (Entries_Dwn_Dict[6][4].get() + Entries_Dwn_Dict[6][5].get())) & #T4-5 downline requirement for T6
                (sl_22['G1_ALL'] - sl_22['G1_0'] - sl_22['G1_1']  - sl_22['G1_2'] - sl_22['G1_3'] - sl_22['G1_4'] >= Entries_Dwn_Dict[6][5].get())), #T5 downline requirement for T6
                'PAID_LEVEL_SIM'] = 6 #ATTENTION
                #update_badges_graces_onerole
        update_badge_grace(sl_22,6,26,3) #ATTENTION
    
        #update_downlines
        Calculated_G1_6 = update_downlines(sl_22, 6) #ATTENTION
        #join the downline titled count with the main table
        sl_23 = pd.merge(sl_22, Calculated_G1_6, left_index=True, right_index=True, how='left')
        #set downline count 0 for null values
        sl_23['G1_6'].fillna(0, inplace=True) #ATTENTION
        
        #IF THE USER OPTED FOR CENTRAL GROUP BASED COMMISSION CALCULATIONS:
        if EntryStatusCent.get():
            #CALCULATE UPLINE 2 & 3 SIMULATED TITLES - This step is necessary for central group calculations
            #You should regroup rep sales in function of their leaders' SIMULATED titles. Yet the simulated title info is in the sl (sl_23) table
            #whereas the full list of reps is in the rep table (rep_3)
            simulation_titles = sl_23[['PAID_LEVEL_SIM']]
            #Leaders' and Reps' simulated Titles: Note that Reps won't have titles. But in regrouping sales we compare their -titles- to uplines.
            #For that matter assign them a fake negative value so that they will be less than any leader
            rep_3a = pd.merge(rep_3, simulation_titles, left_index=True, right_index=True, how='left') #index of BOTH left and right tables is the ACCOUNT_NUMBER
            #the join operation above will yield NULL values for Rep titles:
            rep_3a['PAID_LEVEL_SIM'].fillna(-100, inplace=True)    
            #Upline 1 Simulated Title
            rep_3b = pd.merge(rep_3a, simulation_titles, left_on='UPLINE1', right_index=True, how='left') #index of the right table i.e. rep_copy is the ACCOUNT_NUMBER
            rep_3b.rename(columns = {'PAID_LEVEL_SIM_x':'PAID_LEVEL_SIM','PAID_LEVEL_SIM_y' : 'PAID_LEVEL_SIM_UPLINE'}, inplace = True) 
            #Upline 2 Title
            rep_3c = pd.merge(rep_3b, simulation_titles, left_on='UPLINE2', right_index=True, how='left') #index of the right table i.e. rep_copy is the ACCOUNT_NUMBER
            rep_3c.rename(columns = {'PAID_LEVEL_SIM_x':'PAID_LEVEL_SIM','PAID_LEVEL_SIM_y' : 'PAID_LEVEL_SIM_UPLINE2'}, inplace = True) 
            #Upline 3 Title
            rep_3d = pd.merge(rep_3c, simulation_titles, left_on='UPLINE3', right_index=True, how='left') #index of the right table i.e. rep_copy is the ACCOUNT_NUMBER
            rep_3d.rename(columns = {'PAID_LEVEL_SIM_x':'PAID_LEVEL_SIM','PAID_LEVEL_SIM_y' : 'PAID_LEVEL_SIM_UPLINE3'}, inplace = True) 

            #TEST NULL UPLINE TITLE IMPACT
            rep_3d.update(rep_3d[['PAID_LEVEL_SIM_UPLINE', 'PAID_LEVEL_SIM_UPLINE2', 'PAID_LEVEL_SIM_UPLINE3']].fillna(-200))


            #G1 CV with Central Group: Exclude Sales of Reps with an Upline1 or Upline2 title higher than or equal to title X
            #Only CVs of those with QV >= $50 are included as usual
            #Note that if QV <= -50, the associated neg CV would yield neg commission as well
            #the part before the OR (located right before the indent) is for cases where downline title is below the given title. 
            #Those who have a higher title can still be considered provided that their uplines have still higher title. That is caught by the code block after the OR
            sl_G1_CV_CENTRAL = rep_3d[((rep_3d['QV'] >= en_rep_sales.get()) | (rep_3d['QV'] <= -en_rep_sales.get())) & 
                                     ((rep_3d['PAID_LEVEL_SIM'] < en_title_central.get()) | 
                                             ((rep_3d['PAID_LEVEL_SIM'] >= en_title_central.get()) &
                                              (rep_3d['PAID_LEVEL_SIM'] < rep_3d['PAID_LEVEL_SIM_UPLINE'])))].groupby(['UPLINE1']).agg({'CV':np.sum})
            sl_G1_CV_CENTRAL = sl_G1_CV_CENTRAL.rename(columns={'CV': 'G1_CV_CENTRAL'})
            
            sl_G1_BAD_CENTRAL = rep_3d[((rep_3d['BAD_DEBT'] >= en_rep_sales.get()) | (rep_3d['BAD_DEBT'] <= -en_rep_sales.get())) &
                                     ((rep_3d['PAID_LEVEL_SIM'] < en_title_central.get()) | 
                                             ((rep_3d['PAID_LEVEL_SIM'] >= en_title_central.get()) &
                                              (rep_3d['PAID_LEVEL_SIM'] < rep_3d['PAID_LEVEL_SIM_UPLINE'])))].groupby(['UPLINE1']).agg({'BAD_DEBT':np.sum})
            sl_G1_BAD_CENTRAL = sl_G1_BAD_CENTRAL.rename(columns={'BAD_DEBT': 'G1_BAD_CENTRAL'})
            
            #G2 CV with Central Group: Exclude Sales of Reps with an Upline1 or Upline2 title higher than or equal to title X
            #the part before the OR (located right before the indent) is for cases where downline title is below the given title. 
            #Those who have a higher title can still be considered provided that their uplines have still higher title. That is caught by the code block after the OR
            sl_G2_CV_CENTRAL = rep_3d[((rep_3d['QV'] >= en_rep_sales.get()) | (rep_3d['QV'] <= -en_rep_sales.get())) & 
                                     (((rep_3d['PAID_LEVEL_SIM'] < en_title_central.get()) & 
                                       (rep_3d['PAID_LEVEL_SIM_UPLINE'] < en_title_central.get())) | 
                                             ((rep_3d['PAID_LEVEL_SIM'] >= en_title_central.get()) &
                                              (rep_3d['PAID_LEVEL_SIM'] < rep_3d['PAID_LEVEL_SIM_UPLINE']) & 
                                              (rep_3d['PAID_LEVEL_SIM'] < rep_3d['PAID_LEVEL_SIM_UPLINE2'])))].groupby(['UPLINE2']).agg({'CV':np.sum})
            sl_G2_CV_CENTRAL = sl_G2_CV_CENTRAL.rename(columns={'CV': 'G2_CV_CENTRAL'})
            
            sl_G2_BAD_CENTRAL = rep_3d[((rep_3d['BAD_DEBT'] >= en_rep_sales.get()) | (rep_3d['BAD_DEBT'] <= -en_rep_sales.get())) &
                                     (((rep_3d['PAID_LEVEL_SIM'] < en_title_central.get()) & 
                                       (rep_3d['PAID_LEVEL_SIM_UPLINE'] < en_title_central.get())) | 
                                             ((rep_3d['PAID_LEVEL_SIM'] >= en_title_central.get()) &
                                              (rep_3d['PAID_LEVEL_SIM'] < rep_3d['PAID_LEVEL_SIM_UPLINE']) & 
                                              (rep_3d['PAID_LEVEL_SIM'] < rep_3d['PAID_LEVEL_SIM_UPLINE2'])))].groupby(['UPLINE2']).agg({'BAD_DEBT':np.sum})
            sl_G2_BAD_CENTRAL = sl_G2_BAD_CENTRAL.rename(columns={'BAD_DEBT': 'G2_BAD_CENTRAL'})
            
            #G3 CV with Central Group: Exclude Sales of Reps with an Upline1 or Upline2 title higher than or equal to title X
            #the part before the OR (located right before the indent) is for cases where downline title is below the given title. 
            #Those who have a higher title can still be considered provided that their uplines have still higher title. That is caught by the code block after the OR
            sl_G3_CV_CENTRAL = rep_3d[((rep_3d['QV'] >= en_rep_sales.get()) | (rep_3d['QV'] <= -en_rep_sales.get())) & 
                                     (((rep_3d['PAID_LEVEL_SIM'] < en_title_central.get()) & 
                                       (rep_3d['PAID_LEVEL_SIM_UPLINE'] < en_title_central.get()) & 
                                       (rep_3d['PAID_LEVEL_SIM_UPLINE2'] < en_title_central.get())) | 
                                             ((rep_3d['PAID_LEVEL_SIM'] >= en_title_central.get()) &
                                              (rep_3d['PAID_LEVEL_SIM'] < rep_3d['PAID_LEVEL_SIM_UPLINE']) & 
                                              (rep_3d['PAID_LEVEL_SIM'] < rep_3d['PAID_LEVEL_SIM_UPLINE2']) &
                                              (rep_3d['PAID_LEVEL_SIM'] < rep_3d['PAID_LEVEL_SIM_UPLINE3'])))].groupby(['UPLINE3']).agg({'CV':np.sum})
            sl_G3_CV_CENTRAL = sl_G3_CV_CENTRAL.rename(columns={'CV': 'G3_CV_CENTRAL'})
            
            sl_G3_BAD_CENTRAL = rep_3d[((rep_3d['BAD_DEBT'] >= en_rep_sales.get()) | (rep_3d['BAD_DEBT'] <= -en_rep_sales.get())) &
                                     (((rep_3d['PAID_LEVEL_SIM'] < en_title_central.get()) & 
                                       (rep_3d['PAID_LEVEL_SIM_UPLINE'] < en_title_central.get()) & 
                                       (rep_3d['PAID_LEVEL_SIM_UPLINE2'] < en_title_central.get())) | 
                                             ((rep_3d['PAID_LEVEL_SIM'] >= en_title_central.get()) &
                                              (rep_3d['PAID_LEVEL_SIM'] < rep_3d['PAID_LEVEL_SIM_UPLINE']) & 
                                              (rep_3d['PAID_LEVEL_SIM'] < rep_3d['PAID_LEVEL_SIM_UPLINE2']) &
                                              (rep_3d['PAID_LEVEL_SIM'] < rep_3d['PAID_LEVEL_SIM_UPLINE3'])))].groupby(['UPLINE3']).agg({'BAD_DEBT':np.sum})
            sl_G3_BAD_CENTRAL = sl_G3_BAD_CENTRAL.rename(columns={'BAD_DEBT': 'G3_BAD_CENTRAL'})

            sl_23a = pd.merge(sl_23, sl_G1_CV_CENTRAL, left_index=True, right_index=True, how='left')
            sl_23b = pd.merge(sl_23a, sl_G2_CV_CENTRAL, left_index=True, right_index=True, how='left')
            sl_23c = pd.merge(sl_23b, sl_G3_CV_CENTRAL, left_index=True, right_index=True, how='left')
            sl_23d = pd.merge(sl_23c, sl_G1_BAD_CENTRAL, left_index=True, right_index=True, how='left')
            sl_23e = pd.merge(sl_23d, sl_G2_BAD_CENTRAL, left_index=True, right_index=True, how='left')
            sl_23f = pd.merge(sl_23e, sl_G3_BAD_CENTRAL, left_index=True, right_index=True, how='left')
            sl_23f.update(sl_23f[['G1_CV_CENTRAL', 'G2_CV_CENTRAL', 'G3_CV_CENTRAL', 'G1_BAD_CENTRAL','G2_BAD_CENTRAL', 'G3_BAD_CENTRAL']].fillna(0))  # avoid confusion in comm caclulation by replacing NULLs
        else:
            sl_23f = sl_23
        
        #CALCULATE COMMISSION FOR SIMULATED TITLES
        count_by_title_list = sl_23f['PAID_LEVEL_SIM'].value_counts() #gives the number of records for every unique value i.e. titles
        for t in Entries_Comm_Dict.keys(): #loop for every title to be simulated
            if t in count_by_title_list.keys(): #get only the titles that exist after simulation. Those that do not exist give key error
                #BAD DEBT is given positive. User should be warned for the input format
                sl_23f.loc[(sl_23f['PAID_LEVEL_SIM'] == t), 'G1_Comm_SIM'] = (sl_23f['G1_CV'] * Entries_Comm_Dict[t][1].get() - sl_23f['G1_BAD'] * Entries_Claw_Dict[t][1].get())  #G1 Comm
                sl_23f.loc[(sl_23f['PAID_LEVEL_SIM'] == t), 'G2_Comm_SIM'] = (sl_23f['G2_CV'] * Entries_Comm_Dict[t][2].get() - sl_23f['G2_BAD'] * Entries_Claw_Dict[t][2].get()) #G2 Comm
                sl_23f.loc[(sl_23f['PAID_LEVEL_SIM'] == t), 'G3_Comm_SIM'] = (sl_23f['G3_CV'] * Entries_Comm_Dict[t][3].get() - sl_23f['G3_BAD'] * Entries_Claw_Dict[t][3].get()) #G3 Comm
                #sl_23f.update(sl_23f[['G1_Comm_SIM', 'G2_Comm_SIM', 'G3_Comm_SIM']].fillna(0)) # null values cause the sums to be null when included in calculation
                sl_23f.loc[(sl_23f['PAID_LEVEL_SIM'] == t), 'G123_Comm_SIM'] = (sl_23f['G1_Comm_SIM'] + sl_23f['G2_Comm_SIM'] + sl_23f['G3_Comm_SIM']) #Total Commission
        
        #CALCULATE COMMISSION WITH THE CENTRAL GROUP SCENARIO IF SELECTED BY THE USER
        if EntryStatusCent.get():
            for t in Entries_Comm_Dict.keys(): #loop for every title to be simulated
                if t in count_by_title_list.keys(): #get only the titles that exist after simulation. Those that do not exist give key error
                    #BAD DEBT is given positive. User should be warned for the input format
                    sl_23f.loc[(sl_23f['PAID_LEVEL_SIM'] == t), 'G1_Comm_CENTRAL_SIM'] =  (sl_23f['G1_CV_CENTRAL'] * Entries_Comm_Dict[t][1].get() - sl_23f['G1_BAD_CENTRAL'] * Entries_Claw_Dict[t][1].get())  #G1 Comm
                    sl_23f.loc[(sl_23f['PAID_LEVEL_SIM'] == t), 'G2_Comm_CENTRAL_SIM'] =  (sl_23f['G2_CV_CENTRAL'] * Entries_Comm_Dict[t][2].get() - sl_23f['G2_BAD_CENTRAL'] * Entries_Claw_Dict[t][2].get())  #G2 Comm
                    sl_23f.loc[(sl_23f['PAID_LEVEL_SIM'] == t), 'G3_Comm_CENTRAL_SIM'] =  (sl_23f['G3_CV_CENTRAL'] * Entries_Comm_Dict[t][3].get() - sl_23f['G3_BAD_CENTRAL'] * Entries_Claw_Dict[t][3].get())  #G3 Comm
                    #sl_23f.update(sl_23f[['G1_Comm_CENTRAL_SIM', 'G2_Comm_CENTRAL_SIM', 'G3_Comm_CENTRAL_SIM']].fillna(0))  # null values cause the sums to be null when included in calculation
                    sl_23f.loc[(sl_23f['PAID_LEVEL_SIM'] == t), 'G123_Comm_CENTRAL_SIM'] =  (sl_23f['G1_Comm_CENTRAL_SIM'] + sl_23f['G2_Comm_CENTRAL_SIM'] + sl_23f['G3_Comm_CENTRAL_SIM']) #Total Commission
            
        #Save results
        sl_dict[c] = sl_23f
        
        #EXPORT RESULTS FOR TEST
        testo = str(time.strftime("%c")).replace('/','_') #for naming the folder where the export file is saved
        testo = testo.replace(':', '_')  # for naming the folder where the export file is saved
        if EntryStatus.get() == 1: #if the user has clicked the option of exporting simulation results
            sl_dict[c].to_csv(en_browse.get() + '/sl_' + str(c) + '_' + testo + '.csv')
            if EntryStatusCent.get(): #if central group calculation is selected the last processed rep data will be in df rep_3d
                rep_3d.to_csv(en_browse.get() + '/rep_' + str(c) + '_' + testo + '.csv')
            else:
                rep_3.to_csv(en_browse.get() + '/rep_' + str(c) + '_' + testo + '.csv')
            
    # ============================END OF LOOP=========================================
    
    # =============================================================================
    # # MAKE CHARTS  IF SELECTED BY USER
    if EntryCharts.get():
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec

        # GET TITLE COUNT CHARTS
        num_charts = len(sl_dict.keys())
        num_grid_y = 2 #math.ceil(math.sqrt(num_charts))
        num_grid_x = math.ceil(num_charts / 2) #math.ceil(num_charts / num_grid_y)

        plt.figure(1, figsize=(36,36), dpi = 80)
        G = gridspec.GridSpec(math.ceil(len(sl_dict.keys())/2)*3,2) #Pay attention to the CAPITAL 'S' in GridSpec
        for k in sl_dict.keys():
            plt.subplot(G[math.ceil(k/2)*3-2:math.ceil(k/2)*3,math.ceil((k-1)/2-math.floor((k-1)/2))])

            bar_width = 0.30

            plotme_sim = sl_dict[k].groupby('PAID_LEVEL_SIM').size().to_frame()
            plotme_sim = plotme_sim.rename(columns={0: 'TITLE_COUNT'}) #the calculated field is not named. Name it properly

            plotme_orig_temp = sl_dict[k][['PAID_LEVEL']].replace(-1,0) #Original source includes -1 as title level which stands for CAN as well. Applies only for CANADA
            plotme_orig = plotme_orig_temp.groupby('PAID_LEVEL').size().to_frame()
            plotme_orig = plotme_orig.rename(columns={0: 'TITLE_COUNT'}) #the calculated field is not named. Name it properly

            #Define the x axis. Note that one of the simulated / original title can have less number of titles with associated leaders
            #To avoid incompatible size error (when there is a y value for one of the sim / orig and not the other) get the longer one into account
            # Note that both axes can be of different length but they overlap. for the final xticks get the longer one
            x_sim = plotme_sim.index.values.astype(int) #astype, a numpy method makes the copy of the array, cast to a specified type.
            x_orig = plotme_orig.index.values.astype(int)
            if len(plotme_sim.index) >= len(plotme_orig.index):
                x_axis = x_sim
            else:
                x_axis = x_orig

            plot_values_sim = []
            for v in plotme_sim[['TITLE_COUNT']].values:
                plot_values_sim.append(v[0])

            y_sim = plt.bar(x_sim, plot_values_sim, bar_width,
            #y_sim = plt.bar(x_sim, plotme_sim[['TITLE_COUNT']].values, width = 0.30) #,
                            alpha=0.30,
                            color='cornflowerblue', #for color options: https://matplotlib.org/examples/color/named_colors.html
                            label='simulation')

            plot_values_orig = []
            for v in plotme_orig[['TITLE_COUNT']].values:
                plot_values_orig.append(v[0])

            # original value is the bar on the right in each couple
            y_orig = plt.bar(x_orig+bar_width, plot_values_orig, bar_width,
            #y_orig = plt.bar(x_orig+bar_width, plotme_orig[['TITLE_COUNT']].values,bar_width,
                             alpha=0.40,
                             color='rebeccapurple',
                             label='original')

            plt.xticks(x_axis + bar_width / 2, x_axis) #1st argument is for the location of the tick, the second is the x value itself
            #plt.xlabel('Title #')
            plt.ylabel('SL Count')
            plt.title('Campaign: ' + str(campaign_list[k-1]))

            for i, each in enumerate(plotme_orig.index):
                for col in plotme_orig.columns:
                    y = plotme_orig.loc[each][col]
                    plt.text(i + bar_width / 2, y, y, multialignment = 'left', rotation = 'horizontal')

            for i, each in enumerate(plotme_sim.index):
                for col in plotme_sim.columns:
                    y = plotme_sim.loc[each][col]
                    plt.text(i - bar_width / 2, y, y, multialignment = 'left', rotation = 'horizontal')

            plt.tight_layout()

            #plt.figure(1).legend(handles=[y_sim, y_orig], labels = ['simulation', 'original'], loc='upper right', ncol = 2) #with ncol=2 the legend is on one line spanning 2 columns

            #Enter subtitle i.e. the title for the whole figure covering the subplots
            st = plt.figure(1).suptitle('Number of Leaders by Title ID (0: Untitled)', fontsize=14)
            # shift subplots down:
            st.set_y(0.95)
            plt.figure(1).subplots_adjust(top=0.85)
            plt.figure(1).subplots_adjust(hspace=.1) #add vertical space between subplots
    
        # GET GRACE COUNT CHARTS
        plt.figure(2, figsize=(46,46), dpi = 80)
        G = gridspec.GridSpec(len(sl_dict.keys())*3,1) #Pay attention to the CAPITAL 'S' in GridSpec
        for k in sl_dict.keys():

            plt.subplot(G[k*3-2:k*3,0])
        
            bar_width = 0.30
            
            plotme_sim = sl_dict[k].groupby('GRACE_COUNT_SIM').size().to_frame()
            plotme_sim = plotme_sim.rename(columns={0: 'COUNT_BY_GRACE'}) #the calculated field is not named. Name it properly
        
            plotme_orig_temp = sl_dict[k][['GRACE_COUNT']].replace(-1,0) #Original source includes -1 as title level which stands for CAN as well. Applies only for CANADA
            plotme_orig = plotme_orig_temp.groupby('GRACE_COUNT').size().to_frame()
            plotme_orig = plotme_orig.rename(columns={0: 'COUNT_BY_GRACE'}) #the calculated field is not named. Name it properly
        
            x_sim = plotme_sim.index.values.astype(int) #astype, a numpy method makes the copy of the array, cast to a specified type.
            x_orig = plotme_orig.index.values.astype(int)
            if len(plotme_sim.index) >= len(plotme_orig.index):
                x_axis = x_sim
            else:
                x_axis = x_orig

            plot_values_sim = []
            for v in plotme_sim[['COUNT_BY_GRACE']].values:
                plot_values_sim.append(v[0])

            y_sim = plt.bar(x_sim, plot_values_sim, bar_width,
                            alpha=0.30,
                            color='cornflowerblue', #for color options: https://matplotlib.org/examples/color/named_colors.html
                            label='simulation')
            # original value is the bar on the right in each couple
            plot_values_orig = []
            for v in plotme_orig[['COUNT_BY_GRACE']].values:
                plot_values_orig.append(v[0])

            y_orig = plt.bar(x_orig+bar_width, plot_values_orig, bar_width,
                             alpha=0.40,
                             color='rebeccapurple',
                             label='original')
            
            plt.xticks(x_axis+bar_width/2, x_axis) #1st argument is for the location of the tick, the second is the x value itself
            plt.ylabel('SL Count')
            plt.title('Campaign: ' + str(campaign_list[k-1]))
                    
            for i, each in enumerate(plotme_orig.index):
                for col in plotme_orig.columns:
                    y = plotme_orig.loc[each][col]
                    plt.text(i + bar_width/2, y, y, multialignment = 'left', rotation = 'horizontal')
                    
            for i, each in enumerate(plotme_sim.index):
                for col in plotme_sim.columns:
                    y = plotme_sim.loc[each][col]
                    plt.text(i - bar_width/2, y, y,  multialignment = 'left', rotation = 'horizontal')
            
            plt.tight_layout()
            
            #plt.figure(2).legend(handles=[y_sim, y_orig], labels = ['simulation', 'original'], loc='upper right', ncol = 2) #with ncol=2 the legend is on one line spanning 2 columns
            #Enter subtitle i.e. the title for the whole figure covering the subplots
            st2 = plt.figure(2).suptitle('Number of Leaders by Grace Count', fontsize=14)
            # shift subplots down:
            st2.set_y(0.95)
            plt.figure(2).subplots_adjust(top=0.85)
            plt.figure(2).subplots_adjust(hspace=.1)
            
        # GET COMMISSION CHARTS
        plt.figure(3, figsize=(46,46), dpi = 80)
        G = gridspec.GridSpec(math.ceil(len(sl_dict.keys())/2)*3,2) #Pay attention to the CAPITAL 'S' in GridSpec
        for k in sl_dict.keys():
            plt.subplot(G[math.ceil(k/2)*3-2:math.ceil(k/2)*3,math.ceil((k-1)/2-math.floor((k-1)/2))])
            
            bar_width = 0.30
            
            grouped_title_sim = sl_dict[k][['PAID_LEVEL_SIM','G1_Comm_SIM', 'G2_Comm_SIM', 'G3_Comm_SIM']].groupby('PAID_LEVEL_SIM')
            plotme_g1_sim = grouped_title_sim[['G1_Comm_SIM']].aggregate(np.sum)
            plotme_g1_sim['G1_Comm_SIM'].fillna(0, inplace=True) #for title id 0 commission sum will be NULL leading to the ValueError: posx and posy should be finite values
            plotme_g1_sim = plotme_g1_sim.values/1000
            plotme_g1_sim = plotme_g1_sim.round(2)
            
            plotme_g2_sim = grouped_title_sim[['G2_Comm_SIM']].aggregate(np.sum)
            plotme_g2_sim['G2_Comm_SIM'].fillna(0, inplace=True)
            plotme_g2_sim = plotme_g2_sim.values/1000
            plotme_g2_sim = plotme_g2_sim.round(2)
            
            plotme_g3_sim = grouped_title_sim[['G3_Comm_SIM']].aggregate(np.sum)
            plotme_g3_sim['G3_Comm_SIM'].fillna(0, inplace=True)
            plotme_g3_sim = plotme_g3_sim.values/1000
            plotme_g3_sim = plotme_g3_sim.round(2)
            
            x_length = max(len(plotme_g1_sim), len(plotme_g2_sim), len(plotme_g3_sim))
            x_g1_sim = np.arange(0, x_length)
            
            x_axis = x_g1_sim

            plot_values_g1_sim = []
            for v in plotme_g1_sim:
                plot_values_g1_sim.append(v[0])

            y_g1_sim = plt.bar(x_g1_sim, plot_values_g1_sim, bar_width, #for a better look show values in 1000s
                            alpha=0.30,
                            color='khaki', #for color options: https://matplotlib.org/examples/color/named_colors.html
                            label='simulation')

            plot_values_g2_sim = []
            for v in plotme_g2_sim:
                plot_values_g2_sim.append(v[0])

            y_g2_sim = plt.bar(x_g1_sim, plot_values_g2_sim, bar_width, #for a better look show values in 1000s
                            alpha=0.30,
                            color='powderblue', #for color options: https://matplotlib.org/examples/color/named_colors.html
                            label='simulation',
                            bottom = plot_values_g1_sim)

            plot_values_g3_sim = []
            for v in plotme_g3_sim:
                plot_values_g3_sim.append(v[0])

            y_g3_sim = plt.bar(x_g1_sim, plot_values_g3_sim, bar_width, #for a better look show values in 1000s
                            alpha=0.30,
                            color='rosybrown', #for color options: https://matplotlib.org/examples/color/named_colors.html
                            label='simulation',
                            bottom = [sum(x) for x in zip(plot_values_g1_sim, plot_values_g2_sim)])
            
            plt.xticks(x_axis, x_axis) #1st argument is for the location of the tick, the second is the x value itself
        
            plt.ylabel('K $')
            plt.title('Campaign: ' + str(campaign_list[k-1]))
            
            #add data label only if the value is not 0. Adding them up for higher generations result in overlapping labels
            for i in x_g1_sim:                                    
                if plotme_g1_sim[i] != 0:
                    plt.text(i - bar_width / 4, plotme_g1_sim[i] / 2, plotme_g1_sim[i][0]) #put the label in the middle of the related bar
                if plotme_g2_sim[i] != 0:
                    plt.text(i - bar_width / 4, plotme_g1_sim[i] + plotme_g2_sim[i] / 2, plotme_g2_sim[i][0]) #G2 label will be on top of the full height of G1 bar + half of G2 bar height
                if plotme_g3_sim[i] != 0:
                    plt.text(i - bar_width / 4, plotme_g1_sim[i] + plotme_g2_sim[i] + plotme_g3_sim[i] / 2, plotme_g3_sim[i][0])
                    
            plt.tight_layout()
            
            #plt.figure(3).legend(handles=[y_g1_sim, y_g2_sim, y_g3_sim], labels = ['G1 Comm', 'G2 Comm', 'G3 Comm'], loc='upper right', ncol = 3) #with ncol=3 the legend is on one line spanning 3 columns
            #Enter subtitle i.e. the title for the whole figure covering the subplots
            st3 = plt.figure(3).suptitle('Leadership Commissions (In K $) by Title ID', fontsize = 14)
            # shift subplots down:
            st3.set_y(0.95)
            plt.figure(3).subplots_adjust(top = 0.85)
            plt.figure(3).subplots_adjust(hspace = .1)
        
        if EntryStatusCent.get():
            plt.figure(4, figsize=(46,46), dpi = 80)
            G = gridspec.GridSpec(math.ceil(len(sl_dict.keys())/2)*3,2) #Pay attention to the CAPITAL 'S' in GridSpec
            for k in sl_dict.keys():
                plt.subplot(G[math.ceil(k/2)*3-2:math.ceil(k/2)*3,math.ceil((k-1)/2-math.floor((k-1)/2))])
                
                bar_width = 0.30
                
                grouped_title_sim = sl_dict[k][['PAID_LEVEL_SIM','G1_Comm_CENTRAL_SIM', 'G2_Comm_CENTRAL_SIM', 'G3_Comm_CENTRAL_SIM']].groupby('PAID_LEVEL_SIM')
                plotme_g1_sim = grouped_title_sim[['G1_Comm_CENTRAL_SIM']].aggregate(np.sum)
                plotme_g1_sim['G1_Comm_CENTRAL_SIM'].fillna(0, inplace=True) #for title id 0 commission sum will be NULL leading to the ValueError: posx and posy should be finite values
                plotme_g1_sim = plotme_g1_sim.values/1000
                plotme_g1_sim = plotme_g1_sim.round(2)
                
                plotme_g2_sim = grouped_title_sim[['G2_Comm_CENTRAL_SIM']].aggregate(np.sum)
                plotme_g2_sim['G2_Comm_CENTRAL_SIM'].fillna(0, inplace=True)
                plotme_g2_sim = plotme_g2_sim.values/1000
                plotme_g2_sim = plotme_g2_sim.round(2)
                
                plotme_g3_sim = grouped_title_sim[['G3_Comm_CENTRAL_SIM']].aggregate(np.sum)
                plotme_g3_sim['G3_Comm_CENTRAL_SIM'].fillna(0, inplace=True)
                plotme_g3_sim = plotme_g3_sim.values/1000
                plotme_g3_sim = plotme_g3_sim.round(2)
                
                x_length = max(len(plotme_g1_sim), len(plotme_g2_sim), len(plotme_g3_sim))
                x_g1_sim = np.arange(0, x_length)
                
                x_axis = x_g1_sim

                plot_values_g1_sim = []
                for v in plotme_g1_sim:
                    plot_values_g1_sim.append(v[0])

                y_g1_sim = plt.bar(x_g1_sim, plot_values_g1_sim, bar_width, #for a better look show values in 1000s
                                alpha=0.30,
                                color='khaki', #for color options: https://matplotlib.org/examples/color/named_colors.html
                                label='simulation')

                plot_values_g2_sim = []
                for v in plotme_g2_sim:
                    plot_values_g2_sim.append(v[0])

                y_g2_sim = plt.bar(x_g1_sim, plot_values_g2_sim, bar_width, #for a better look show values in 1000s
                                alpha=0.30,
                                color='powderblue', #for color options: https://matplotlib.org/examples/color/named_colors.html
                                label='simulation',
                                bottom = plot_values_g1_sim)

                plot_values_g3_sim = []
                for v in plotme_g3_sim:
                    plot_values_g3_sim.append(v[0])

                y_g3_sim = plt.bar(x_g1_sim, plot_values_g3_sim, bar_width, #for a better look show values in 1000s
                                alpha=0.30,
                                color='rosybrown', #for color options: https://matplotlib.org/examples/color/named_colors.html
                                label='simulation',
                                bottom = [sum(x) for x in zip(plot_values_g1_sim, plot_values_g2_sim)])
                
                plt.xticks(x_axis, x_axis) #1st argument is for the location of the tick, the second is the x value itself
            
                plt.ylabel('K $')
                plt.title('Campaign: ' + str(campaign_list[k-1]))
                
                #add data label only if the value is not 0. Adding them up for higher generations result in overlapping labels
                for i in x_g1_sim:                                    
                    if plotme_g1_sim[i] != 0:
                        plt.text(i - bar_width / 4, plotme_g1_sim[i] / 2, plotme_g1_sim[i][0]) #put the label in the middle of the related bar
                    if plotme_g2_sim[i] != 0:
                        plt.text(i - bar_width / 4, plotme_g1_sim[i] + plotme_g2_sim[i] / 2, plotme_g2_sim[i][0]) #G2 label will be on top of the full height of G1 bar + half of G2 bar height
                    if plotme_g3_sim[i] != 0:
                        plt.text(i - bar_width / 4, plotme_g1_sim[i] + plotme_g2_sim[i] + plotme_g3_sim[i] / 2, plotme_g3_sim[i][0])
                        
                plt.tight_layout()
                
                #plt.figure(4).legend(handles=[y_g1_sim, y_g2_sim, y_g3_sim], labels = ['G1 Comm', 'G2 Comm', 'G3 Comm'], loc='upper right', ncol = 3) #with ncol=3 the legend is on one line spanning 3 columns
                #Enter subtitle i.e. the title for the whole figure covering the subplots
                st3 = plt.figure(4).suptitle('Leadership Commissions (In K $) by Title ID \n Central Group Scenario Applied', fontsize = 14)
                # shift subplots down:
                st3.set_y(0.95)
                plt.figure(4).subplots_adjust(top = 0.85)
                plt.figure(4).subplots_adjust(hspace = .1)
    # ----------------------------------------
        plt.show()
# =============================================================================
# =============================================================================
# USER INTERFACE
# =============================================================================
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
       
root = Tk()
root.title("Leadership Diviner")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)
   
# Ask user where she wants to save the output files
#ttk.Label(mainframe, text="Select the directory to export simulation results :").grid(column=6, row=32, sticky = (E), columnspan = 5)
dirBut = Button(mainframe, text='Browse', command = askdirectory, height = 2, state='disabled')  #by default grey out 
dirBut.grid(column = 12, row = 42, sticky = (W), rowspan = 2) #if you immediately call the grid method at the line you create the button, it returns None and you cannot use the configure option

en_browse = StringVar()
BrowseLabel = ttk.Entry(mainframe, width = 43, textvariable = en_browse, state='disabled') #by default grey out
BrowseLabel.grid(column = 6, row = 43, sticky = (W, E), columnspan = 6) #if you immediately call the grid method at the line you create the label, it returns None and you cannot use the configure option

#Checkbutton to enable folder browsing for the export file location
EntryStatus = IntVar()
ttk.Checkbutton(mainframe, text='Export simulation results to the location below:',
	    command = EnableDisableEntry, variable = EntryStatus).grid(column=6, row=42, sticky = (W, E), columnspan = 6)

#Checkbutton to enable charts
EntryCharts = IntVar()
ttk.Checkbutton(mainframe, text='Provide charts', 
	    variable = EntryCharts).grid(column=7, row=44, sticky = (W, E), columnspan = 2)


#empty label for the look
ttk.Label(mainframe, text="").grid(column=0, row=1)

# Input file button
inputBut = Button(mainframe, text='Select Input File', command = ask_input_file, height = 1, state='active')
inputBut.grid(column = 7, row = 2, sticky = (W, E), columnspan = 2) #if you immediately call the grid method at the line you create the button, it returns None and you cannot use the configure option

en_browse_input = StringVar()
BrowseInputLabel = ttk.Entry(mainframe, width = 43, textvariable = en_browse_input, state='disabled')
BrowseInputLabel.grid(column = 9, row = 2, sticky = (W, E), columnspan = 7) #if you immediately call the grid method at the line you create the label, it returns None and you cannot use the configure option

FootnoteLabel = ttk.Label(mainframe, text="The input file must be tab separated", font = ('Helvetica', 9, 'italic')).grid(column = 7, row = 3, sticky=(W), columnspan = 5)

#empty label for the look
ttk.Label(mainframe, text="").grid(column=0, row = 11)

#subtitle
ttk.Label(mainframe, text="TITLE QUALIFIERS: Sales and Actives", font = 'bold').grid(column=7, row=12, sticky=(W, E), columnspan = 5)
#leadership qualifier labels
ttk.Label(mainframe, text="Title ID", wraplength = 30, justify = RIGHT).grid(column=7, row=13, sticky=(W, E))
ttk.Label(mainframe, text="Personal Sales", wraplength = 50).grid(column=8, row=13, sticky=(W, E)) #wraplength wraps as in Excel
ttk.Label(mainframe, text="Team Sales", wraplength = 50).grid(column=9, row=13, sticky=(W, E))
ttk.Label(mainframe, text="G1 Actives", wraplength = 50).grid(column=10, row=13, sticky=(W, E))

#Create title id labels
for t in range(1,7): #to be changed for 12 titles
    ttk.Label(mainframe, text = str(t)).grid(column = 7, row = 13+t, sticky = E)

#empty label for the look
ttk.Label(mainframe, text="").grid(column=0, row=26)

#Commission Labels
ttk.Label(mainframe, text="COMMISSION RATES", font = 'bold').grid(column = 12, row = 12, sticky=(W, E), columnspan = 3)
ttk.Label(mainframe, text="G1").grid(column=12, row = 13, sticky=(W, E))
ttk.Label(mainframe, text="G2").grid(column=13, row = 13, sticky=(W, E))
ttk.Label(mainframe, text="G3").grid(column=14, row = 13, sticky=(W, E))

#Clawback Labels
ttk.Label(mainframe, text="CLAWBACK RATES", font = 'bold').grid(column = 16, row = 12, sticky=(W, E), columnspan = 3)
ttk.Label(mainframe, text="G1").grid(column=16, row = 13, sticky=(W, E))
ttk.Label(mainframe, text="G2").grid(column=17, row = 13, sticky=(W, E))
ttk.Label(mainframe, text="G3").grid(column=18, row = 13, sticky=(W, E))

vcmd = root.register(check_int) #this is for calidation function checking int

#empty label for the look
ttk.Label(mainframe, text="", width = 6).grid(column=15, row = 16)
ttk.Label(mainframe, text="", width = 6).grid(column=19, row = 16)

#Sales threshold for Rep sales to be included in commission calculations
ttk.Label(mainframe, text = "Include rep sales, returns and bad debt >= ").grid(column = 26, row = 14, sticky = (W), rowspan = 1, columnspan = 4)
ttk.Label(mainframe, text = "in commission calculation").grid(column = 27, row = 15, sticky = (W), rowspan = 1, columnspan = 4)
ttk.Label(mainframe, text = "$").grid(column = 25, row = 15, sticky = (E))
en_rep_sales = IntVar()
en_rep_sales.set(50) #set default values for PS entries
ttk.Entry(mainframe, width = 1, textvariable = en_rep_sales, validate = 'key', validatecommand = (vcmd, '%P')).grid(column = 26, row = 15, sticky = (W, E))

#Enable central group based commission calculation
CentralCommLabel = ttk.Label(mainframe, text = "Exclude Reps under a leader with title >=", justify = RIGHT, state='disabled')
CentralCommLabel.grid(column = 26, row = 18, sticky = (W), columnspan = 6)
en_title_central = IntVar()
en_title_central.set(4)
ComboComm = ttk.Combobox(mainframe, width = 2, textvariable = en_title_central, values = list(range(1,7)), state='disabled')
ComboComm.grid(column = 31, row = 18, sticky=(W, E))

EntryStatusCent = IntVar()
ttk.Checkbutton(mainframe, text='Use Central Groups for commission calculations', 
	    command = EnableDisableCent, variable = EntryStatusCent).grid(column = 26, row = 17, sticky = (W, E), columnspan = 6)

#Enable nesting of Reps to Leaders
EntryStatusNesting = IntVar()
ttk.Checkbutton(mainframe, text='Use nesting for Reps w/o a Leader',
                command=EnableDisableNest, variable = EntryStatusNesting).grid(column = 26, row = 21, sticky = (W, E), columnspan = 6)
#Enter number of Reps that can be nested to a leader in a campaign
nesty_rep_label = ttk.Label(mainframe, text = "Max number of Reps that can be nested to an SL in a campaign", justify = RIGHT, state='disabled')
nesty_rep_label.grid(column = 27, row = 22, sticky = (W), columnspan = 6)
nesty_rep_limit = IntVar()
nesty_rep_limit.set(4)
ComboNest = ttk.Combobox(mainframe, width = 2, textvariable = nesty_rep_limit, values = list(range(1,15)), state='disabled')
ComboNest.grid(column = 26, row = 22, sticky=(W))

#subtitle
ttk.Label(mainframe, text="TITLE QUALIFIERS: Downlines", font = 'bold').grid(column=7, row = 27, sticky=(W, E), columnspan = 5)
ttk.Label(mainframe, text="|----------------------------- Upline Title ID -----------------------------|").grid(column = 8, row = 28, sticky=(W, E), columnspan = 5)

ttk.Label(mainframe, text="Dwn Title ID", wraplength = 50, justify = RIGHT).grid(column=7, row = 28, sticky=(W, E), rowspan = 2)
#Downline Qualifier Table
# Upline title labels for the downline qualifiers matrix-Start with 2: Title 1 cannot have a downline condition
for t in range(2,7): #to be changed for 12 titles
    ttk.Label(mainframe, text = str(t)).grid(column = 6 + t, row = 29, sticky = W)
# Downline title labels for the downline qualifiers matrix-End with 11: The highest title cannot be the downline condition of any title
for t in range(1,6): #to be changed for 12 titles
    ttk.Label(mainframe, text = str(t)).grid(column = 7, row = 29 + t, sticky = E)
              
#Set default parameter
dict_defaults = {'PS':      [125,   125,    125,    125,    125,      9999999],
                 'TS':      [850,   4000,   12000,  36000,  225000,   9999999],
                 'G1Act':   [5,     10,     20,     30,     30,       9999999],
                 'Comm': {1: {1: 0.05,  2: 0.02, 3: 0.00}, #the second key within the nested dictionary is the Generation
                         2: {1: 0.05,  2: 0.05, 3: 0.01},
                         3: {1: 0.06,  2: 0.08, 3: 0.05},
                         4: {1: 0.06,  2: 0.10, 3: 0.05},
                         5: {1: 0.07,  2: 0.11, 3: 0.06},
                         6: {1: 0.00,  2: 0.00, 3: 0.00}},
                 'Claw': {1: {1: 0.02,  2: 0.01, 3: 0.00}, #the second key within the nested dictionary is the Generation
                         2: {1: 0.05,  2: 0.01, 3: 0.00},
                         3: {1: 0.08,  2: 0.02, 3: 0.00},
                         4: {1: 0.09,  2: 0.03, 3: 0.00},
                         5: {1: 0.00,  2: 0.00, 3: 0.00},
                         6: {1: 0.00,  2: 0.00, 3: 0.00}},
                 'Dwn': {2: {1: 2},
                         3: {1: 3,  2: 0}, #In order to be title 3, you need to have 3 title1 in your G1
                         4: {1: 4,  2: 2,   3: 0},
                         5: {1: 4,  2: 2,   3: 1,   4: 1}, #In order to be title 5, you need to have 4 title1, 2 title2, 1 title3, 1 title4 in your G1
                         6: {1: 999,2: 999, 3: 999, 4: 999, 5: 999}}
                 }

#entries for commission ratios
Entries_Comm_Dict = {}
for i in range(1, 7): #key i is title id
    Entries_Comm_Dict[i] = {}
    for j in range(1, 4): #key j is generation
        en_comm = DoubleVar()
        Entries_Comm_Dict[i][j] = en_comm
        en_comm.set(dict_defaults['Comm'][i][j]) #set default values for Comm entries
        ttk.Combobox(mainframe, width = 8, textvariable = en_comm, values = list(np.arange(0.0, 1.0, 0.05))).grid(column = j + 11, row = i + 13, sticky = (W)) # values parameter sets the interval among choices in the combo

# entries for clawback ratios
Entries_Claw_Dict = {}
for i in range(1, 7):  # key i is title id
    Entries_Claw_Dict[i] = {}
    for j in range(1, 4):  # key j is generation
        en_claw = DoubleVar()
        Entries_Claw_Dict[i][j] = en_claw
        en_claw.set(dict_defaults['Claw'][i][j])  # set default values for Comm entries
        ttk.Combobox(mainframe, width=8, textvariable=en_claw, values=list(np.arange(0.0, 1.0, 0.05))).grid(column=j + 15, row=i + 13, sticky=(W)) # values parameter sets the interval among choices in the combo

#entries for personal sales thresholds
Entries_PS_Dict = {}
for i in range(1, 7):
    en_ps = IntVar()
    Entries_PS_Dict[i] = en_ps
    en_ps.set(dict_defaults['PS'][i-1]) #set default values for PS entries
#    ttk.Entry(mainframe, width = 8, textvariable = en_ps).grid(column = 8, row = i + 3, sticky = (W))
    ttk.Entry(mainframe, width = 8, textvariable = en_ps, validate = 'key', validatecommand = (vcmd, '%P')).grid(column = 8, row = i + 13, sticky = (W))

#entries for team sales thresholds
Entries_TS_Dict = {}
for i in range(1, 7):
    en_ts = IntVar()
    Entries_TS_Dict[i] = en_ts
    en_ts.set(dict_defaults['TS'][i-1]) #set default values for TS entries
    ttk.Entry(mainframe, width = 8, textvariable = en_ts, validate = 'key', validatecommand = (vcmd, '%P')).grid(column = 9, row = i + 13, sticky = (W))

#comboboxes for G1 Active thresholds
Entries_G1Act_Dict = {}
for i in range(1, 7):
    en_g1act = IntVar()
    Entries_G1Act_Dict[i] = en_g1act
    en_g1act.set(dict_defaults['G1Act'][i-1]) #set default values for G1 Active entries
    ttk.Combobox(mainframe, width = 8, textvariable = en_g1act, values = list(range(0,91))).grid(column = 10, row = i + 13, sticky=(W, E))

#comboboxes for downline (structure) requirements
Entries_Dwn_Dict = {}
for i in range(2, 7): #1st loop for the upline titles i
    Entries_Dwn_Dict[i] = {} #dictionary within dictionary. The first key is the upline, the second is the downline title id
    for j in range(1, 7): #2nd loop for the downline titles j
        if j < i:
            en_dwn = IntVar()
            Entries_Dwn_Dict[i][j] = en_dwn
            en_dwn.set(dict_defaults['Dwn'][i][j]) #set default values for G1 Active entries
            ttk.Combobox(mainframe, width = 8, textvariable = en_dwn, values = list(range(0,10))).grid(column = i + 6, row = j + 29, sticky=(W, E))

#empty label for the look
ttk.Label(mainframe, text="").grid(column=0, row = 44)

#Place the OK button to launch the simulation a.k.a. the diviner function
s = ttk.Style()
s.configure("Bold.TButton", font = ('bold'), foreground = 'green')
button = ttk.Button(mainframe, text = 'CALCULATE', command = validate_logic, style = "Bold.TButton").grid(column = 12, row = 49, columnspan = 2, rowspan = 2)

root.mainloop()
#TO DOs!!!!!!!!!!!!!!!!
# UPLOAD CAMPAIGN DATA AND MAKE THE EXE FILE
# Calculate Bonuses
# Add rolled up Leader charts
# Ask user for the user input with 2 options:
    #use existing preinstalled data
    #import data from file to select
# User INPUT
    # ask user to enter
        # grace count for Titled and Untitled
#Validate user entry: 
    #higher title threshold cannot be less than the lower 
    #whether a folder for export files selected
    #etc
# TAG those who hit the Grace Period limit as REMOVED
        #Those with Grace = 0 AND Badge = 0 are Removed. Substract that amount from UNT count
            #1. Add additional field Removed_Bin: Flag removed SLs in Campaign X
            #2. Add additional field Removed_PC_Bin_Upline1/2/3 in Campaign X+1: Bring the flags from PC.
            #3. Add fields Upline4-5-6 and calculate: For comm calculations there is need for 3 uplines.
            #The most extreme can be the removal of all upline 1,2,3
            #4. For all records where Removed_PC_Bin_Upline1 is flagged, make Upline1 = NULL; repeat this for Upline 2 and 3
            #5. For all records where Removed_PC_Bin_Upline1 is NULL, Upline1 = Upline2 
                #>>>> Bu olmaz. Ya o da gittiyse???? Hatta ustunde 10 nesil olsun, onu da gitmisse Upline = ZM olmali.Yukaridaki adimlari da kontrol et
        #Update the uplines before all G-based calculations
# If you make the simulation of more than 6 titles, add the OR BLOCK for the Set T6 part
# Get PC GRACE_COUNT_SIM
        #If she was removed the PC either exclude her forever unless she gets an actve in her G1
        # or keep her as if she was re-recruited right after being removed
