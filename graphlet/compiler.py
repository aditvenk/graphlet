from __future__ import annotations
from typing import Iterable, List, Protocol
from .graph import Graph
from .passes import DeadCodeElimination, ConstantFolding
from .debug import log

class Pass(Protocol):
    def run(self, g: Graph) -> Graph: ...

class Compiler:
    def __init__(self, passes: Iterable[Pass] | None = None) -> None:
        self.pipeline: List[Pass] = list(passes) if passes is not None else [
            ConstantFolding(),
            DeadCodeElimination(),
        ]

    def compile(self, g: Graph) -> Graph:
        log("Compiler start")
        for p in self.pipeline:
            log(f" Running pass: {p.__class__.__name__}")
            g = p.run(g)
        log("Compiler done")
        return g