data{
    int N; //data数
    int N_p; //今回は46都道府県
    real x1[N]; //GRP
    real x2[N]; //acv
    real x3[N]; //price
    real y[N]; //売上

    //prefecture_id毎に区別する必要がある
    int <lower=1, upper=N_p> p_id[N]; //df['id']が入る。ex)1, 1, 1, 1, 1, 2, 2, ...
}

parameters{
    //共通部分
    real b0_0;
    real b1_0;
    real b2_0;
    real b3_0;
    //地域差(都道府県の数だけ)
    real b0_p[N_p];
    real b1_p[N_p];
    real b2_p[N_p];
    real b3_p[N_p];
    
    //個人差を生み出す正規分布のσ
    real <lower=0> s_b0_p;
    real <lower=0> s_b1_p;
    real <lower=0> s_b2_p;
    real <lower=0> s_b3_p;
    //a[n]x+b[n]の測定誤差
    real <lower=0> s_y;
}
//新しいブロック：parametersで定義されている変数を使って、個人毎のa[n], b[n]を作る必要がある。
transformed parameters{     //parametersで定義されている変数を使って、変形された別のパラメータを定義可能。
    real b0[N_p];
    real b1[N_p];
    real b2[N_p];
    real b3[N_p];

    //都道府県分forループ
    for (n in 1:N_p){
        b0[n] = b0_0 + b0_p[n];
        b1[n] = b1_0 + b1_p[n];
        b2[n] = b2_0 + b2_p[n];
        b3[n] = b3_0 + b3_p[n];
    }
}


model{
    //まずは個人差を正規分布から発生させるためのfor roop
    for (id in 1:N_p){
        b0_p[id] ~ normal(0, s_b0_p);
        b1_p[id] ~ normal(0, s_b1_p);
        b2_p[id] ~ normal(0, s_b2_p);
        b3_p[id] ~ normal(0, s_b3_p);
    }

    //回帰式
    for (n in 1:N){
        //観測される売上が正規分布に従う。平均値は都道府県毎に異なる。
        y[n] ~ normal(b0[p_id[n]] + b1[p_id[n]]*x1[n] + b2[p_id[n]]*x3[n] + b3[p_id[n]]*x3[n], s_y);
    }
}