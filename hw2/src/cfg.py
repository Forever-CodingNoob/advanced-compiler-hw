from typing import Dict, List, Set
from bril import Function, Instruction, Label, ValueOperation
from utils import eprint
from operator import add
from functools import reduce


class BasicBlock:
    def __init__(self, label: str, instrs: List[Instruction] = None):
        self.label = label
        self.instructions: List[Instruction] = instrs if instrs is not None else []
        self.predecessors: Set['BasicBlock'] = set()
        self.successors: Set['BasicBlock'] = set()

    def __repr__(self):
        return f'BasicBlock({self.label})'

    def _repr_debug(self):
        return f"label: {self.label}\n\tsucc: {[j.label for j in self.successors]}\n\tpred: {[j.label for j in self.predecessors]}"


class CFG:
    def __init__(self, function: Function):
        self.function: Function = function
        self.blocks: Dict[str, BasicBlock] = {}
        self.entry_block: BasicBlock = self.construct_cfg()

    def construct_cfg(self) -> BasicBlock:
        """
        Constructs the CFG for the function and returns the entry block.
        """
        # TODO: Implement CFG construction logic
        # Steps:
        # 1. Divide instructions into basic blocks.
        # 2. Establish successor and predecessor relationships.
        # 3. Handle labels and control flow instructions.

        # add the starting basic block
        unique_name = "entry"
        while unique_name in (instr.label for instr in self.function.instrs if isinstance(instr, Label)):
            unique_name+="0"
        instrs_tmp = [Label({"label": unique_name})] + self.function.instrs

        n=len(instrs_tmp)
        labels_idx = [i for i in range(n) if isinstance(instrs_tmp[i], Label)]

        m=len(labels_idx)
        BBs = [BasicBlock(label=instrs_tmp[i].label,
                          instrs=instrs_tmp[i+1:j])
               for i,j in zip(labels_idx, labels_idx[1:]+[n])]
        assert len(BBs) == m

        label2BB = {bb.label:bb for bb in BBs}
        self.blocks = label2BB

        def get_successors(i: int) -> Set['BasicBlock']:
            # i: index of BB in BBs
            last_instr: Instruction= instrs_tmp[labels_idx[i+1]-1 if i<m-1 else n-1]
            match last_instr.op:
                case "jmp" | "br": # taken
                    return set(map(lambda label: label2BB[label], last_instr.labels))
                case "ret": # jumping out of function
                    return set()
                case _: # fall through (including 'call' instruction and another label)
                    return set([BBs[i+1]]) if i<m-1 else set()

        for i in range(m): # len(BBs)
            BBs[i].successors = get_successors(i)
            for succ in BBs[i].successors:
                succ.predecessors.add(BBs[i])

        for bb in BBs:
            eprint(f"function {self.function.name}")
            eprint(bb._repr_debug())
            eprint("**********")

        return BBs[0]

    def get_blocks(self) -> List[BasicBlock]:
        return list(self.blocks.values())

    @staticmethod
    def _postorder_list(bb: BasicBlock, visited: Set[str]) -> List[BasicBlock]:
        visited.add(bb.label)
        return reduce(add,
                    [CFG._postorder_list(succ, visited) for succ in bb.successors if succ.label not in visited],
                    []) + [bb]

    def postorder_list(self) -> List[BasicBlock]:
        return self._postorder_list(self.entry_block, set())
