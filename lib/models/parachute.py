from typing import List, Tuple
from pydantic import BaseModel


class Parachute(BaseModel):
    name: List[str] = ["Main", "Drogue"]
    cd_s: List[float] = [10, 1]
    lag: List[float] = [1.5, 1.5]
    sampling_rate: List[int] = [105, 105]
    noise: List[Tuple[float, float, float]] = [(0, 8.3, 0.5), (0, 8.3, 0.5)]
    triggers: List[str] = [
        "lambda p, h, y: y[5] < 0 and h < 800",
        "lambda p, h, y: y[5] < 0",
    ]

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return [self[i] for i in range(*idx.indices(len(self)))]
        return Parachute(
            name=[self.name[idx]],
            cd_s=[self.cd_s[idx]],
            triggers=[self.triggers[idx]],
            sampling_rate=[self.sampling_rate[idx]],
            lag=[self.lag[idx]],
            noise=[self.noise[idx]],
        )

    def __len__(self):
        if self.name is not None:
            return len(self.name)
        return 0
