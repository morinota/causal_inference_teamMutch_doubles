from enum import unique
import pystan
from pystan.model import StanModel
import pandas as pd
import os
import arviz as az


def load_matchData() -> pd.DataFrame:
    '''試合データをpd.DataFrameで読み込み'''
    datasets_list = []

    season_years = ["2019", "2020", "2021"]
    # 各シーズンのデータを読み込み
    for i, season_year in enumerate(season_years):
        datasets_list.append(pd.read_csv(
            f'{season_year}_match_result.csv', header=0, encoding='utf-8'))

        # シーズンカラムを付与する
        datasets_list[i]["season_year"] = int(season_year)

    # 縦に結合
    df_dataset = pd.concat(datasets_list)

    return df_dataset  # type: ignore


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    '''
    観測データの前処理..
    '''

    def _get_unique_index(df: pd.DataFrame, target_column: str) -> pd.DataFrame:
        # まずユニーク値のリスト
        unique_list = df[target_column].unique()
        # indexとセットのdictを生成
        unique_index_dict = {team_name: (int(team_index) + 1)
                             for team_index, team_name in enumerate(unique_list)}
        # mapメソッドで値を格納
        df[f'{target_column}_index'] = df[target_column].map(unique_index_dict)

        return df

    # 各レコード毎に、ホームチームのユニークなindexを作る.
    return _get_unique_index(df, target_column='HomeTeam_name')


def arrange_data_for_stan(df: pd.DataFrame, X1_column: str) -> dict:
    '''
    観測データを、StanModelに入力するデータ型に変換する関数.

    parameters
    -------------
    df:観測データ
    X1_column:観測データにおける、分析したい原因変数を指定。(ex. ダブルスの勝敗, シングルス1の勝敗, etc.)
    '''
    # DataFrame=>配列のdictに変換
    data = {'N': len(df), 'N_t': len(df['HomeTeam_name'].unique()), 'x1': df[X1_column],
            'x2': df['HomeTeam_rate_S'], 'x3': df['AwayTeam_rate_S'], 'y': df['HomeTeam_win'],
            't_id': df['HomeTeam_name_index']}
    return data


def compile_stan_code(stan_filepath: str) -> StanModel:
    '''
    stanファイルをコンパイルし、StanModelインスタンスとしてReturnする関数.
    '''
    stan_model = StanModel(file=stan_filepath)

    return stan_model


def sampling_MCMC(stan_model: StanModel, data: dict):
    '''
    サンプリングを実行し、結果をReturnする関数.
    '''
    fit = stan_model.sampling(
        data=data, pars=None, chains=4, iter=2000, warmup=200, seed=123, init='random')

    return fit


def summarizing_result(sampling_result):
    pass


def main():
    df = load_matchData()
    df = preprocess(df)
    # コンパイル
    stan_model = compile_stan_code(stan_filepath='baysian_model.stan')
    # dfをstanコードに入力する為に、dictに変換
    data = arrange_data_for_stan(df, X1_column='db_HomeWin')
    # サンプリング
    fit = sampling_MCMC(stan_model=stan_model, data=data)


if __name__ == "__main__":
    main()
