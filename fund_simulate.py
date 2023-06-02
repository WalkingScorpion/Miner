import sys
import os
from data_fetcher import em_fetcher as emf
from fund import fund_base as fb
from fund import fund_obj as fo
from invest_stategy import continue_signal_strategy as css
from invest_stategy import acc_signal_strategy as ass
from matrix import liner_matrix as lm

if __name__=="__main__":
    matrix_num = 3
    init = 50000
    df_dict = {}
    st_dict = {
        's3' : css.ContinueSignalStrategy(init, 0.2, 3),
        's4' : css.ContinueSignalStrategy(init, 0.2, 4),
        's5' : css.ContinueSignalStrategy(init, 0.2, 5),
        's6' : css.ContinueSignalStrategy(init, 0.2, 6),
        's7' : css.ContinueSignalStrategy(init, 0.2, 7),
    }
    for code in fo.FundDict.keys():
        f = emf.EastMoneyFetcher(code, "2018-01-01", "2023-03-30")
        f.fetch_data()
        df = f.build_dataframe()
        matrix = lm.LinerMatrix(df, matrix_num)
        df_list = matrix.run_matrix()
        df_dict[code] = df_list
    r = 0
    while (r < matrix_num):
        print('-------------------------- matrix %ld -------------------------' % r)
        for name, strategy in st_dict.items():
            for code, fund in fo.FundDict.items():
                ab = df_dict.get(code)[r]
                fund.clear()
                fund.set_code(code)
                fund.bind_data(ab)
                fm = {code:fund}
                strategy.set_name(name)
                strategy.bind_fund_map(fm)
                strategy.run_strategy()
                strategy.show()
                print()
        r = r + 1
        
