
import pandas as pd


class CsvService:

    @staticmethod
    def import_csv(path):
        return pd.read_csv(path)

    @staticmethod
    def export_csv(df, path):
        df.to_csv(path, index=False)