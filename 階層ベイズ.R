library(rstan)
set.seed(123)

# データ読み込み
df = read.csv('2021_match_result.csv', header = TRUE,
              encoding = 'UTF-8')
# stanに渡すデータをlist()に入れる(Pythonでいうdict？？)
data = list()

# stanコードのコンパイル.

# stanコードにデータを渡す.

# MCMCサンプリングの実行

