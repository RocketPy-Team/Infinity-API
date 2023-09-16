from typing import List, Tuple
from pydantic import BaseModel

class Parachute(BaseModel, frozen=True):
    name: "List[str]"
    cd_s: "List[float]"
    sampling_rate: "List[int]"
    lag: "List[float]"
    noise: "List[Tuple[float, float, float]]" = [(0, 8.3, 0.5), (0, 8.3, 0.5)]
    triggers: "List[str]"

    def __hash__(self):
        return hash((
            tuple(self.name),
            tuple(self.cd_s),
            tuple(self.sampling_rate),
            tuple(self.lag),
            tuple(self.noise),
            tuple(self.triggers),
        ))

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
