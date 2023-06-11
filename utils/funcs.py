#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import re
import time
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta


# ігнорування попередження SettingWithCopyWarning
pd.set_option('mode.chained_assignment', None)  


# In[3]:


# конвертування строчки дати в формат дати 
# d, m, y = [int(x) for x in df.at[0, "Date"].split("/")]
# a = date(y, m, d)
# a
# date(2023, 5, 9).isoweekday() == 2  # первірка дати на вівторок


# In[101]:


list_columns =   [
        "Date",
        "HomeTeam",
        "AwayTeam",
        "rez_h_full",
        "rez_a_full",
        "rez_h_first",
        "rez_a_first",
        "h_first",
        "h_full",
        "a_first",
        "a_full",
    ] 
# funcs

def get_team_results(
                    h_team_name: str,
                    a_team_name: str,
                    matches_before: pd.DataFrame,
                    ) -> tuple[int, int, int, int] :
    """
    отримання результатів команд, останнього матчу
    повертає список з 4 чисел, різниці забитих мячів
      - дом. команди в першому таймі,
      - дом. команди в повному матчі,
      - гост. команди в першому таймі,
      - гост. команди в повному матчі,
    """
    h_team_match = matches_before[                            
                        (matches_before["HomeTeam"] == h_team_name) | 
                        (matches_before["AwayTeam"] == h_team_name)
                    ].tail(1) 
    
    a_team_match = matches_before[
                        (matches_before["HomeTeam"] == a_team_name) |
                        (matches_before["AwayTeam"] == a_team_name)
                    ].tail(1) 

    h_first = (
                    int(h_team_match.at[h_team_match.index[0], "HTHG"]) - 
                    int(h_team_match.at[h_team_match.index[0], "HTAG"])
                )


    h_full = (
                    int(h_team_match.at[h_team_match.index[0], "FTHG"]) - 
                    int(h_team_match.at[h_team_match.index[0], "FTAG"])
                )

    h_first = h_first if h_team_name in h_team_match["HomeTeam"].values else -h_first
    h_full = h_full if h_team_name in h_team_match["HomeTeam"].values else -h_full


    a_first = (
                    int(a_team_match.at[a_team_match.index[0], "HTHG"]) - 
                    int(a_team_match.at[a_team_match.index[0], "HTAG"])
                )

    a_full = (
                    int(a_team_match.at[a_team_match.index[0], "FTHG"]) - 
                    int(a_team_match.at[a_team_match.index[0], "FTAG"])
                )
    a_first = a_first if a_team_name in a_team_match["HomeTeam"].values else -a_first
    a_full = a_full if a_team_name in a_team_match["HomeTeam"].values else -a_full
    
    return (
        h_first,
        h_full,
        a_first,
        a_full,
    )


def get_rez_data_df(df_data):
    rez_data = []
    for ind in df_data.index:
        current_match = df_data.loc[ind]
        matches_before = df_data.loc[:ind-1]
        h_team_name = current_match["HomeTeam"]
        a_team_name = current_match["AwayTeam"]
        if ( 
            (h_team_name in matches_before["HomeTeam"].values or
                     h_team_name in matches_before["AwayTeam"].values) and 
            (a_team_name in matches_before["HomeTeam"].values or
                     a_team_name in matches_before["AwayTeam"].values)  
        ):
            h_first, h_full, a_first, a_full = get_team_results(
                                                         h_team_name,
                                                         a_team_name,
                                                        matches_before
                                                        )
 
            data_row = [
                *current_match.values,
                h_first,
                h_full,
                a_first,
                a_full
            ]
            rez_data.append(data_row)
    return rez_data


def get_clean_data_df(df):
    df.loc[:, "Date"] =  [date.fromisoformat("-".join(x.split("/")[::-1]))  for x in df.loc[:, "Date"].values]
    df = df[df["Date"] < date.today()]
    df.sort_values(by=["Date"], ascending=True, inplace=True, ignore_index=True)
    df_data = df.loc[:, ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "HTHG", "HTAG"]]

    clean_data = pd.DataFrame(
                            data=get_rez_data_df(df_data),
                            columns=list_columns
                )
    return clean_data, df_data


def get_near_last_tuesday(target_date):
    near_tuesday = target_date
    while near_tuesday.isoweekday() != 2:
        near_tuesday -= timedelta(days=1)
        
    return near_tuesday


# In[116]:


def get_total_work(clean_data, old_data, team_names):

    tuesday = get_near_last_tuesday(date.today())
    
    work_df = clean_data[
        (clean_data["Date"] >= tuesday - timedelta(days=14)) &
        (clean_data["Date"] < tuesday) 
    ] 
    
    # минулі результати
    work_df["index"] = work_df.index
    work_df_np = work_df[[
                            "h_first", "h_full",
                            "a_first", "a_full",
                            "rez_h_full", "rez_a_full", "rez_h_first", "rez_a_first",
                            "index"
                ]].to_numpy()

   
    filtred_work_df_np = work_df_np[
        work_df_np[:, 6] == work_df_np[:, 7]  # нічья перший тайм
#             work_df_np[:,6] + work_df_np[:, 7] > 1.5  # тб 1.5  перший тайм 
    ]
    if filtred_work_df_np.shape[0] == 0: 
        print("немає нічьї за останні дві неділі в перших таймах")
        return
    
    for h_name, a_name in team_names:
        h_first_target, h_full_target, a_first_target, a_full_target = get_team_results(
                                                         h_name,
                                                         a_name,
                                                        old_data
                                                        )
        print(f"останні резульати команд - {h_name} - {a_name}")
        print(h_first_target, h_full_target, a_first_target, a_full_target)
        print()

  

        if not (
                filtred_work_df_np[
                        (filtred_work_df_np[:, 0] == h_first_target)
                        &
                        (filtred_work_df_np[:, 1] == h_full_target)
#                         &
#                         (filtred_work_df_np[:, 2] == a_first_target)
#                         &(filtred_work_df_np[:, 3] == a_full_target)
                ].shape[0] >= 2        
        ): 
            print("result - no")
            continue
        print("result - yes")


# In[122]:


def main_work(df, team_names: list[tuple]):
 
    clean_data, old_data = get_clean_data_df(df)
 
   
    rez_dict = get_total_work(clean_data, old_data, team_names)
     


# In[121]:


if __name__ == "__main__":
    df = pd.read_csv("./old_data/some_test.csv")
    main_work(df, [("Канберра Олимпик", "Гангалин"),])

