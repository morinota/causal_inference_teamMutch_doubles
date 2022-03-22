data{
    int N; //観測されたdata数
    int N_t; //対戦チームの種類(ホームチームにする?それとも組み合わせ?)
    int x1[N]; //ダブルスの勝敗ダミー
    real x2[N]; //ホームチームのSランク選手割合
    real x3[N]; //アウェイチームのSランク選手割合
    int y[N]; //団体戦の勝敗ダミー

    //観測されたdataを、チーム_id毎に区別する必要がある.
    int <lower=1, upper=N_t> t_id[N]; //ex)1, 1, 1, 1, 1, 2, 2, ...(これがN個)
}
parameters{
    //共通部分
    real b0_0;
    real b1_0;
    real b2_0;
    real b3_0;
    //対戦チームによる個体差(チームの種類の数の配列)
    real b0_t[N_t];
    real b1_t[N_t];
    real b2_t[N_t];
    real b3_t[N_t];
    
    //個体差を生み出す正規分布のσ
    real <lower=0> s_b0_t;
    real <lower=0> s_b1_t;
    real <lower=0> s_b2_t;
    real <lower=0> s_b3_t;
  
}
//新しいブロック：parametersで定義されている変数を使って、チーム毎の偏回帰係数a[n], b[n]を作る必要がある。
transformed parameters{
    real b0[N_t];
    real b1[N_t];
    real b2[N_t];
    real b3[N_t];

    //チーム数分forループ
    for (n in 1:N_t){
        b0[n] = b0_0 + b0_t[n];
        b1[n] = b1_0 + b1_t[n];
        b2[n] = b2_0 + b2_t[n];
        b3[n] = b3_0 + b3_t[n];
    }
}

model{
  //まずは個人差を正規分布から発生させるためのfor roop
    for (id in 1:N_t){
        b0_t[id] ~ normal(0, s_b0_t);
        b1_t[id] ~ normal(0, s_b1_t);
        b2_t[id] ~ normal(0, s_b2_t);
        b3_t[id] ~ normal(0, s_b3_t);
    }
    //回帰成分
    for (n in 1:N){
        //yがベルヌーイ分布に従う。
        //そのパラメータは説明変数によってに異なる。
        y[n] ~ bernoulli_logit(b0[t_id[n]] + b1[t_id[n]]*x1[n] + b2[t_id[n]]*x2[n] + b3[t_id[n]]*x3[n]);
    }
    //s_bi_t達の事前分布の指定:
    //(記述しない場合、十分に幅の広い一様分布が使われる.)
    
    
}