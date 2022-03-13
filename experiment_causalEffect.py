from preprocess import Preprocess
import pandas as pd
import os
import statsmodels as sm

def load_matchData()->pd.DataFrame:
    '''試合データをpd.DataFrameで読み込み'''

    INPUT_DIR = r'C:\Users\Masat\デスクトップ_Instead\webアプリ開発\Tleague_scraping'
    datasets_list = []

    season_years = ["2018", "2019", "2020", "2021"]
    # 各シーズンのデータを読み込み
    for i, season_year in enumerate(season_years):
        datasets_list.append(pd.read_csv(os.path.join(INPUT_DIR, f'{season_year}_match_result.csv'), header=0, encoding='utf-8'))
        
        # シーズンカラムを付与する
        datasets_list[i]["season_year"] = int(season_year)

    # 縦に結合
    df_dataset = pd.concat(datasets_list)

    return df_dataset


def modeling(X:pd.DataFrame, y:pd.Series):


def main():
    df = load_matchData()
    
    df = Preprocess()








if __name__ == "__main__":
    main()

