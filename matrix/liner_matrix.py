import pandas as pd

class LinerMatrix(object):

    def __init__(self, dataframe, group_num, bystep = False):
        self.df = dataframe
        self.gn = group_num
        self.bystep = bystep

    def run_matrix(self):
        return self.run_strategy_bystep() \
            if self.bystep else self.run_strategy_normal()

    def run_strategy_normal(self):
        row = self.df.shape[0]
        base = int(row / self.gn)
        rem = row % self.gn
        result = []
        i = 0
        while (i < self.gn): 
            s = i * base + (i if i < rem else rem)
            l = base + 1 if i < rem else base
            tmp_df = self.df.iloc[s : s + l, :].reset_index(drop=True)
            result.append(tmp_df)
            i = i + 1
        return result

    def run_strategy_bystep(self):
        row = self.df.shape[0]
        result = []
        i = 0
        while (i < self.gn): 
            tmp_df = self.df.iloc[i : row : self.gn, :].reset_index(drop=True)
            result.append(tmp_df)
            i = i + 1
        return result

if __name__=="__main__":
    data = []
    data.append(list(range(16)))
    df = pd.DataFrame(data).T
    df.columns = ["test"]
    print(df)
    print(LinerMatrix(df, 4).run_matrix())
    print(LinerMatrix(df, 4, True).run_matrix())
