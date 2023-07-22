from typing import List, Tuple
from pydantic import BaseModel

class Parachute(BaseModel, frozen=True):
    name: "List[str]"
    CdS: "List[float]"
    samplingRate: "List[int]"
    lag: "List[float]"
    noise: "List[Tuple[float, float, float]]"
    triggers: "List[str]"

    def __hash__(self):
        return hash((
            tuple(self.name),
            tuple(self.CdS),
            tuple(self.samplingRate),
            tuple(self.lag),
            tuple(self.noise),
            tuple(self.triggers),
        ))

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return [self[i] for i in range(*idx.indices(len(self)))]
        else:
            return Parachute(
                name=[self.name[idx]],
                CdS=[self.CdS[idx]],
                triggers=[self.triggers[idx]],
                samplingRate=[self.samplingRate[idx]],
                lag=[self.lag[idx]],
                noise=[self.noise[idx]],
            )

    def __len__(self):
        if self.name is not None:
            return len(self.name)
        return 0
