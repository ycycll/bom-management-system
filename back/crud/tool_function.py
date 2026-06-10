class CheckCleaner:
    def __init__(self, df_input):
        self.df = df_input

    def check_and_clean(self, col, value):
        # 清除常规值
        col_del = f'{col}_del'
        condition = self.df[col] != value
        self.df[col_del] = self.df[col].fillna('').where(condition, other='')

    def check_in_description(self, col_name):
        new_col_name = f'{col_name}_bom'
        self.df[new_col_name] = self.df.apply(_in, args=(f'{col_name}_del',), axis=1).map(
            {True: '', False: f',{col_name}'})

    def check_normal_in_description(self, col_name):
        new_col_name = f'{col_name}_bom'
        self.df[new_col_name] = self.df.apply(_in, args=(f'{col_name}',), axis=1).map(
            {True: '', False: f',{col_name}'})

    def review(self, col: str, col_non_standard_configs: list, col_standard_config: str):
        pattern = "|".join(col_non_standard_configs)

        is_standard_or_empty = (
                (self.df[col] == col_standard_config) |
                (self.df[col] == '') |
                (self.df[col].isna())
        )

        feature_review_false = is_standard_or_empty & (
            self.df['materialDesc'].str.contains(pattern, na=False, regex=True))
        if feature_review_false.any():
            self.df.loc[feature_review_false, 'bomFalse'] = self.df.loc[feature_review_false, 'bomFalse'] + f',{col}'


def _in(row, x):
    return str(row[x]) in str(row['materialDesc'])


class Cleaner:  # 清理标准特征
    def __init__(self, df_input):
        self.df = df_input

    def clean(self, col, value, new_col=False):
        condition = self.df[col] != value
        if new_col:
            col_new = col + '_del'
            self.df[col_new] = self.df[col].where(condition, other='')
        else:
            self.df[col] = self.df[col].where(condition, other='')
