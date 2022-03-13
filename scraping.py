
import scraping_class

def main():
    # set season year
    season_years = ["2018", "2019", "2020", "2021"]
    # season_year = input("Input season year(2018, 2019, 2020, 2021):")
    for season_year in season_years:
    # TleagueGameScrapingオブジェクトをinitialize
        tgs = scraping_class.TleagueGameScraping(season_year)

        # scraping
        tgs.get_link() # 各試合のlinkのリストを取得.
        tgs.get_match_record() # 各試合の情報を抽出
        tgs.get_team_info() # 各チームの情報を抽出
        # save
        tgs.save_match_table_as_csv(filepath=fr'C:\Users\Masat\デスクトップ_Instead\webアプリ開発\causal_inference_teamMutch_doubles\{season_year}_match_result.csv')
        
        del tgs

if __name__ == "__main__":
    main()