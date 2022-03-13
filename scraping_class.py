from turtle import st
from unicodedata import name
import requests # HTMLファイルの取得用
from bs4 import BeautifulSoup # HTMLファイルの解析用
import re
import csv
import pandas as pd
import soupsieve
import collections

class TleagueGameScraping:
    def __init__(self, season_year):
        self.season_year = season_year
        self.base_url = "https://tleague.jp/schedule/"
        self.base_url_team = "https://tleague.jp/player/"
        self.is_end = False

    # 実際に試合データを取ってくるページのLinkのリストを取得する
    def get_link(self):
        self.link_list = []
        url = self.base_url + "?season=" + self.season_year

        # Requestsのget関数にアクセス先のurlを与えてHTMLファイルを取得.
        ## これはGETメソッドのリクエストをサーバーに送ってレスポンスを取得している.
        response = requests.get(url)
        print(response) #=>[200] は成功レスポンス.

        # BeautifulSoupオブジェクトを生成.
        ## .content属性でHTMLのbytes形式のデータを取得."lxml"はパース(読み取り)方式の一種.
        soup = BeautifulSoup(response.content, "lxml")

        #以下は、htmlの中身を取得する操作
        ## まず各試合がレコードになった表部分のhtmlを取得
        matchlist = soup.find(class_="table-responsive mb-30")
        ## 次に各試合のレコードを操作(1シーズン88試合?)：
        for i in matchlist.find_all(name="tr"):
            # 各試合の詳細へ繋がるurlリンクを取得
            inner = i.find(class_="text-center align-middle p-2 text-nowrap")
            # print(type(inner))

            # URLリンクを抽出(例外処理付)
            try:
                href = inner.find('a').get('href')
            except AttributeError:
                href = ''
            # リストに加える.
            self.link_list.append(href[10:])
        # print(self.link_list)


    def get_match_record(self):
        i = 1
        # 各試合のデータを抽出するinner関数
        def _get_each_match_record(i):
            game_result_dict = {}
            url_each_mutch = self.base_url + self.link_list[i]
            # print(url_each_mutch)
            # 各試合のスコアをhtmlから取得.
            try:
                response_match = requests.get(url_each_mutch)
                soup_match = BeautifulSoup(response_match.content, "lxml")
                # 以下はhtmlファイルの操作
                table = soup_match.find(name="table", class_="table table-borderless my-3")
                game_list = table.find_all(name="tr")

                #各試合のスコアを格納する処理
                result_names = ["db", "s1", "s2", "s3", "vm"]
                for i, game_html in enumerate(game_list):
                    result = game_html.find("div", class_="text-white text-center font-weight-bold").text
                    # 抽出したHTML文字列の加工(半角数字以外を取り除く)
                    result = re.sub(pattern="[^0-9]", repl='', string=result)
                    # 試合結果のdictに、加工したHTML文字列を格納(文字列として)
                    game_result_dict[result_names[i]] =str(result)


                # 対戦チーム名(HomeTeam, AwayTeam)を格納する処理
                block_temp = soup_match.find_all("div", class_="container")[2]
                block_temp2 = block_temp.find_all("a", class_="font-weight-bold h6")
                HomeTeam_name, AwayTeam_name = block_temp2[1].text, block_temp2[3].text
                game_result_dict["HomeTeam_name"] = HomeTeam_name
                game_result_dict["AwayTeam_name"] = AwayTeam_name
                print(game_result_dict)
                return game_result_dict
            except:
                return None

        # ループ処理で、Seasonの各試合の記録を取ってくる.
        self.match_result_list = []
        for i in range(len(self.link_list)):
            self.match_result_list.append(_get_each_match_record(i))


    def get_team_info(self):
        '''
        season_year年シーズンにおける、各チームの選手情報を取得するメソッド。
        現時点では、チーム内の選手ランクの内訳を取得する.
        '''
        # urlを作成
        if int(self.season_year) == 2018:
            # 2018年シーズンのHPでは選手ランクが載っていなかった為、とりあえず2019年で代用.
            url = self.base_url_team + "index.php" + "?year=2019"
        else:
            url = self.base_url_team + "index.php" + "?year=" + self.season_year

        # urlへリクエスト, HTMLファイルをレスポンスで取得
        response = requests.get(url)
        # BeautifulSoupオブジェクトを生成.
        soup = BeautifulSoup(response.content, "lxml")

        # 結果格納用のdict
        self.team_info_dict ={}

        # 以下は、取得したHTMLファイルから必要な情報を抽出していく処理

        ## 各チームのメンバーの情報が載ってるブロックを抽出
        team_list = soup.find(class_="page-section page-team bg-light py-50")
        team_list = team_list.find_all(class_="pt-lg-25")
        print(len(team_list))
        
        # チーム一つ一つを繰り返し処理：
        for team_html in team_list:
            # 1. チーム名を取得したい...!
            team_name = team_html.find(name="div", class_="d-inline-block font-size-14 font-size-lg-20 font-weight-bold").text
            print(team_name)
            
            # 2. チーム内の各選手のランクを取得してリストに格納する...!
            player_rank_list =[]
            player_list = team_html.find_all(name="div", class_="player-list-item col-4 col-md-3 col-lg-2 mb-30 px-2 px-lg-10")
            print(len(player_list))
            
            for player_html in player_list:
                # 対象選手のランク情報を取得
                try:
                    player_rank = player_html.find_all(name="span")[1].text
                    # print(player_rank)
                    player_rank_list.append(player_rank)
                except:
                    pass

            # 3. チーム内の選手ランク毎の人数を集計(S, AAA, AA, A)する
            rank_count = collections.Counter(player_rank_list)
            # 4. 「チーム内の選手数におけるS or AAAランク選手の割合」を算出.
            try:
                rate_AAA_or_S = (rank_count['AAA'] + rank_count['S']) / len(player_list)
                rate_S = rank_count['S']/len(player_list)
            except:
                pass

            # 5. チーム名+選手ランク毎の人数をdictに格納
            try:
                self.team_info_dict[team_name] = {"rank_count_info":rank_count, "rate_AAA_and_S":rate_AAA_or_S, "rate_S":rate_S} 
                del rate_AAA_or_S, rate_S
            except:
                pass


    def save_match_table_as_csv(self, filepath):
        '''self.match_result_list属性をpd.DataFrameに変換=>csvファイルとして出力する.'''
        '''# # dictのListを、listのdictに変換(=しなくて良かった！)
        # self.match_result_dict = {}
        # dict_keys = ["db", "s1", "s2", "s3", "vm", "HomeTeam_name", "AwayTeam_name"]
        # for key_name in dict_keys:
        #     # リスト内包表記で...各keyの結果のListをdictに格納
        #     self.match_result_dict[key_name] = [i[key_name] for i in self.match_result_list]'''

        # DictのListをDataframeに
        self.df = pd.DataFrame(data=self.match_result_list[1:])
        # カラムを並び替えておく
        columns_order = ["db", "s1", "s2", "s3", "vm", "HomeTeam_name", "AwayTeam_name"]
        self.df = self.df.reindex(columns=columns_order)

        # 前処理0(vmが行われかったレコードを"00"で補完)
        self.df['vm'].fillna(value='00', inplace=True)

        # 前処理1(各試合の勝敗のDammy変数化)
        ## apply()に適用する関数を作成
        def _get_match_win_dammy(match_score:str)->int:
            '''
            apply()メソッド用の関数
            各試合の勝敗のスコア(ex."03", "31")から、HomeTeamの勝利ダミー変数を作成するInnor Function
            '''
            match_score = str(match_score)
            dif_game = float(match_score[0]) - float(match_score[1])
            if dif_game > 0.0:
                return 1
            else:
                return 0
        ## 各試合毎にDammy変数を生成
        for match_name in ["db", "s1", "s2", "s3", "vm"]:
            self.df[match_name+f'_HomeWin'] = self.df[match_name].apply(_get_match_win_dammy)
            print(f'fin {match_name}')

        # 前処理2(Team matchの勝敗のDammy変数化)
        def _get_HomeTeam_win_dammy(row):
            '''
            apply()メソッド用のinnor関数
            '''
            # チームの獲得スコアを集計
            HomeTeam_score = 0
            for match_name in ["db", "s1", "s2", "s3", "vm"]:
                HomeTeam_score += row[match_name+'_HomeWin']
            
            # 団体戦の勝敗を判定、Return
            if HomeTeam_score >= 3:
                return 1
            else:
                return 0
        ## apply()メソッドの実行
        self.df['HomeTeam_win'] = self.df.apply(_get_HomeTeam_win_dammy, axis=1)

        # 前処理3 (self.team_info_dictから、チームの情報を追加する)
        ## "チームの地力"として、「チーム内の選手数におけるS or AAAランク選手の割合」を定義
        def _get_Team_rate_AAA_and_S(value:str)->str:
            '''
            apply()メソッド用のinnor関数
            '''
            # 「チーム内の選手数におけるS or AAAランク選手の割合」を取得・格納
            return self.team_info_dict[value]["rate_AAA_and_S"]

        self.df['HomeTeam_rate_AAA_and_S'] = self.df['HomeTeam_name'].apply(_get_Team_rate_AAA_and_S)
        self.df['AwayTeam_rate_AAA_and_S'] = self.df['AwayTeam_name'].apply(_get_Team_rate_AAA_and_S)

        ## 同様に、"チームの地力"として、「チーム内の選手数におけるSランク選手の割合」を定義
        def _get_Team_rate_S(value:str)->str:
            '''
            apply()メソッド用のinnor関数
            '''
            # 「チーム内の選手数におけるS or AAAランク選手の割合」を取得・格納
            return self.team_info_dict[value]["rate_S"]

        self.df['HomeTeam_rate_S'] = self.df['HomeTeam_name'].apply(_get_Team_rate_S)
        self.df['AwayTeam_rate_S'] = self.df['AwayTeam_name'].apply(_get_Team_rate_S)
        
        # export
        self.df.to_csv(filepath, index=False, encoding='utf-8')


def main():
    # set season year
    season_year = "2019"
    # season_year = input("Input season year(2018, 2019, 2020, 2021):")

    # TleagueGameScrapingオブジェクトをinitialize
    tgs = TleagueGameScraping(season_year)

    # scraping
    tgs.get_link() # 各試合のlinkのリストを取得.
    tgs.get_match_record() # 各試合の情報を抽出
    tgs.get_team_info() # 各チームの情報を抽出
    # save
    tgs.save_match_table_as_csv(filepath=fr'C:\Users\Masat\デスクトップ_Instead\webアプリ開発\Tleague_scraping\{season_year}_match_result.csv')

    
if __name__ == "__main__":
    main()