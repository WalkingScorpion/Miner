import sys
import os
from data_fetcher import em_fetcher as emf
from fund import fund_base as fb
from fund import fund_obj as fo
from invest_stategy import single_bond_strategy as sbs
from matrix import liner_matrix as lm

if __name__=="__main__":
    f = emf.EastMoneyFetcher('007230', "2020-01-01", "2023-03-23")
    f.fetch_data()
    df = f.build_dataframe()
    matrix = lm.LinerMatrix(df, 2)
    df_list = matrix.run_matrix()
    for (i, ab) in enumerate(df_list):
        fund = fo.F007230(ab, True)
        fm = {'007230':fund}
        strategy = sbs.SingleBondStrategy(fm, 5000)
        strategy.run_strategy()
        print('---- matrix %ld ----' % (i))
        fund.show()
        strategy.show()
