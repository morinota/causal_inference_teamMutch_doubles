<!-- 記事タイトル -->
<!-- Tリーグ試合データをスクレイピング -->

# 始めに

卓球競技の団体戦において、「ダブルスが重要である」「ダブルスが団体戦の鍵をにぎる」と経験知としてよく言われます。
学生時代等に卓球に打ち込んだ方々は、顧問の先生やクラブチームのコーチから言われたことがある人も少なくないのではないでしょうか。
かくいう私も学生時代に卓球に夢中になった者の一人ですが、色んな方々から言われた覚えがあるので、卓球界においてある種の暗黙知として存在するような気がします。

そこで、統計的因果推論を用いて「卓球団体戦におけるダブルスの勝敗」と「団体戦の勝敗」の因果関係の定量分析を試みます。
もう少し統計的因果推論の用語を用いると、本記事の目的は、「卓球団体戦におけるダブルスの勝敗(=原因変数)」が「団体戦の勝敗(=結果変数)」に与える因果効果(介入効果)の定量化、になります。

以前 Twitter で、高校時代の先輩が「『卓球の団体戦はダブルスを取った方が有利』って説、誰か定量的に分析してくれないかなー」みたいな事を言っていたような気もするので、まあ需要もゼロではないんじゃないでしょうか？笑

自身の統計的因果推論の練習を兼ねてますので、見識がある方からのツッコミは歓迎しております！
また私同様に、卓球が好きな方からのコメント・ツッコミも歓迎しております！

# ステップ 0-1 どんなデータを用いる？

さて、上述した分析を行うに当たって、まずはともかくデータセットが必要になります。
必要なデータセットは、基本的には団体戦の結果に関するデータですね。
団体戦の結果の公開状況を考慮して、今回は T リーグの試合結果のデータを用いる事にしました。

T リーグは 2018 年からスタートした、日本初の卓球競技のプロリーグです。
2021-2022 シーズンにおいては、男子 4 チーム、女子 5 チームでそれぞれ優勝を争います。
T リーグの試合形式は団体戦です。ざっくり説明すると、1 つの団体戦の中でダブルス、シングルス 1、シングルス 2、シングルス 3、ビクトリーマッチの順に計 5 試合行われます。そして 3 試合勝利したチームの勝利となります。
(試合形式に関してもう少し詳細を説明すると、ビクトリーマッチは必ずしも行われる訳ではなく、シングルス 3 を終えた時点で団体戦の勝敗が決していない場合にのみ実施されます。)
従って団体戦の勝敗＋上記の 5 種類の試合の勝敗のデータが、本記事において主要なデータになります。

実は本記事の目的を達成する為には、恐らく上記の試合結果(ダブルス等、各試合の勝敗＋団体戦の勝敗)以外にもデータが必要になります。
詳しくは次の記事以降で書く予定ですが、「ダブルスの勝敗」と「団体戦の勝敗」の因果関係を検討する為には、それらの両方に影響を与えうる第三の因子(1 つとも限りません)を考慮した分析を行う必要がある為です。統計的因果推論の世界では、この第三の因子を"交絡因子"と呼び、この「交絡因子にいかに対応するか」が重要であるようです。

# ステップ 0-2 T リーグの HP から試合結果のデータをスクレイピング

データ収集方法に関しては、T リーグの HP から過去の試合結果のデータをスクレイピングさせていただく事にしました。
当然、手作業で一試合一試合 csv ファイルに打ち込むより遙かに効率的ですし、元々スクレイピングによるデータ収集の自動化・効率化、みたいな技術にも興味があったので練習がてら作ってみました。

T リーグの試合データのスクレイピングに関しては、先人の方々がいらっしゃったので参考にさせていただきました。良記事、ありがとうございました！

- Shisato 様(https://www.eureka-moments-blog.com/entry/2020/04/30/173420)
- ishigen の技術ブログ 様(https://ishigentech.hatenadiary.jp/entry/2019/03/09/160224)

昨年のシーズン辺りで、T リーグの HP のデザインレイアウトや URL に変更があった様で、Web ページの中身や HTML にそこまで詳しくない事もあり、中々苦戦しました。

以下、スクレイピング用のコードになります。
まずは、スクレイピング用の処理を管理する為の、TleagueGameScraping クラスの定義のファイルです。
(これまで自分自身でクラスを定義する事があまり無かったので、属性をたくさん作ってしまいました。不要な属性や冗長な点もあるかと思います笑)

<!-- コード挿入 -->

```python:scraping_class.py

import requests # HTMLファイルの取得用
from bs4 import BeautifulSoup # HTMLファイルの解析用
import pandas as pd

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
```

続いて、スクレイピングを実行するファイルです。
scraping_class で定義した TleagueGameScraping クラスを用いて、T リーグの HP から試合結果のデータを取得・加工し、csv 出力しています。

<!-- scraping.py -->

```python:scraping.py

import scraping_class

def main():
    # set season year
    season_years = ["2018", "2019", "2020"]
    # season_year = input("Input season year(2018, 2019, 2020, 2021):")
    for season_year in season_years:
    # TleagueGameScrapingオブジェクトをinitialize
        tgs = scraping_class.TleagueGameScraping(season_year)

        # scraping
        tgs.get_link() # 各試合のlinkのリストを取得.
        tgs.get_match_record()
        # # save
        tgs.save_match_table_as_csv(filepath=fr'保存したいディレクトリ名\{season_year}_match_result.csv')

        del tgs

if __name__ == "__main__":
    main()

```

# ステップ 0-3 スクレイピングによるデータセット生成

結果として、以下のデータが得られました。
手作業で試合結果を打ち込むよりはやはり遙かに速いので、処理が回った瞬間は快楽物質が分泌しまくりました！
(やはり自動化って最高です！)

<!-- データセット -->

| db  | s1  | s2  | s3  | vm  | HomeTeam_name        | AwayTeam_name                | db_HomeWin | s1_HomeWin | s2_HomeWin | s3_HomeWin | vm_HomeWin | HomeTeam_win | HomeTeam_rate_AAA_and_S | AwayTeam_rate_AAA_and_S | HomeTeam_rate_S     | AwayTeam_rate_S     |
| --- | --- | --- | --- | --- | -------------------- | ---------------------------- | ---------- | ---------- | ---------- | ---------- | ---------- | ------------ | ----------------------- | ----------------------- | ------------------- | ------------------- |
| 12  | 30  | 31  | 23  | 10  | 木下マイスター東京   | 岡山リベッツ                 | 0          | 1          | 1          | 0          | 1          | 1            | 0.5555555555555556      | 0.5                     | 0.4444444444444444  | 0.08333333333333333 |
| 12  | 32  | 31  | 13  | 01  | 日本生命レッドエルフ | 木下アビエル神奈川           | 0          | 1          | 1          | 0          | 0          | 0            | 0.6363636363636364      | 0.5                     | 0.2727272727272727  | 0.2                 |
| 20  | 32  | 23  | 32  | 00  | T.T 彩たま           | 琉球アスティーダ             | 1          | 1          | 0          | 1          | 0          | 1            | 0.45454545454545453     | 0.5                     | 0.18181818181818182 | 0.1                 |
| 02  | 31  | 30  | 23  | 10  | 岡山リベッツ         | T.T 彩たま                   | 0          | 1          | 1          | 0          | 1          | 1            | 0.5                     | 0.45454545454545453     | 0.08333333333333333 | 0.18181818181818182 |
| 21  | 31  | 13  | 30  | 00  | 木下アビエル神奈川   | トップおとめピンポンズ名古屋 | 1          | 1          | 0          | 1          | 0          | 1            | 0.5                     | 0.4166666666666667      | 0.2                 | 0.16666666666666666 |
| 20  | 31  | 13  | 30  | 00  | 木下マイスター東京   | 琉球アスティーダ             | 1          | 1          | 0          | 1          | 0          | 1            | 0.5555555555555556      | 0.5                     | 0.4444444444444444  | 0.1                 |

各レコードは、1 つの団体戦における各試合結果となっています。
各カラムの定義は、以下の様になっています。

- db, s1, s2, s3, vm (str): その団体戦におけるダブルス、シングルス 1, シングルス 2, シングルス 3, ビクトリーマッチのスコア。ex)db="02"の場合、ゲームカウント 0-2 でアウェイチームの勝利。
- HomeTeam_name (str)：その団体戦におけるホームチーム名です。
- AwayTeam_name (str)：その団体戦におけるアウェイチーム名です。
- db_HomeWin, s1_HomeWin, s2_HomeWin, s3_HomeWin, vm_HomeWin : その団体戦内のダブルス、シングルス 1, シングルス 2, シングルス 3, ビクトリーマッチにおける、ホームチームの勝利を示すダミー変数。
- HomeTeam_win：その団体戦における、ホームチームの勝利を示すダミー変数。
- HomeTeam_rate_AAA_and_S, AwayTeam_rate_AAA_and_S：ホームチーム、もしくはアウェイチームにおける、全選手に占める AAA ランク orS ランク選手の割合。
- HomeTeam_rate_S, AwayTeam_rate_S：ホームチーム、もしくはアウェイチームにおける、全選手に占める S ランク選手の割合。（詳しくは次回の記事で説明しますが、今回の因果推論で"交絡因子"として使用します）

# まとめ

とりあえず今回、因果効果の推定の為に、T リーグの試合結果をスクレイピングしてデータセットを収集・作成しました。
コーディングに関しては、HTML 文字列をレスポンスとして受け取った後の、特定の情報を指定して取得する処理の部分に中々苦戦し、お世辞にも綺麗とは言えないコードになっていると思います...。
しかしまあ、無事にデータセットを作成する事ができ、初めてのスクレイピングとしては満足しています。
(スクレイピングの処理に関しても、なんか汚いコードだなと思った方はぜひ指摘いただければ嬉しいです！)

次回以降は、統計的因果推論の手法を用いて、「卓球団体戦におけるダブルスの勝敗」が「団体戦の勝敗」に与える因果効果の向きとその大きさに関して分析していきたいと思います。
(予定としては、まず次回は「バックドア基準」の話をまとめながら、回帰モデルを用いた因果推論を試してみる予定です！)

初投稿という事で、文章的にも Markdown の構成的にも、稚拙な点が多々あるとは思いますが、**最後までお読みいただきありがとうございました！**

繰り返しになりますが自身の**統計的因果推論やコーディングの練習**を兼ねてますので、**上記分野が好きな方々からツッコミ・コメントをいただけたらとても喜びます**！
また私同様に、**卓球が好きな方からのコメント・ツッコミもいただけたらとても嬉しいです**！
