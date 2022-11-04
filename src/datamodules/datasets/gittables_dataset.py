from pathlib import Path
from typing import Optional

import pandas as pd
import torch
from torch.utils.data import IterableDataset

from src.utils import check_table, dict2tuples


class GitTablesDataset(IterableDataset):
    def __init__(
        self,
        data_dir: str,
        data_files: Optional[list[str]] = None,
    ):
        super().__init__()

        data_dir = Path(data_dir)
        if data_files is None:
            self.data_files = data_dir.rglob("*.parquet")
        else:
            self.data_files = [data_dir / f for f in data_files]

    def __iter__(self) -> list[tuple]:
        assert (
            torch.utils.data.get_worker_info() is None
        ), "only support single-process data loading"
        for f in self.data_files:
            try:
                df = pd.read_parquet(f)
                df.columns = df.columns.str.replace("\ufeff", "")
                df.drop_duplicates(inplace=True)
            except Exception:
                continue

            if check_table(df):
                df = df.fillna("")
                yield from map(dict2tuples, df.to_dict("records"))
