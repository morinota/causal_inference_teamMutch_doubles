library(rstan)
set.seed(123)

# データ読み込み
df = read.csv('2021_match_result.csv', header = TRUE,
              encoding = 'UTF-8')
# stanに渡すデータをlist()に入れる(Pythonでいうdict？？)
data = list()

# stanコードのコンパイル.
stanmodel = stan_model(file = '階層ベイズ.stan')
# stanコードにデータを渡してサンプリング.
fit <- sampling(object = stanmodel, 
                data=data, 
                # サンプリングして保存したいパラメータを指定.
                pars=c('a', 'b'),
                # パラメータの初期値を設定.
                init=,
                seed=1234,
                iter = 1000, warmup=200, thin=2, chains =3
                
                )



# MCMCサンプリングの実行

