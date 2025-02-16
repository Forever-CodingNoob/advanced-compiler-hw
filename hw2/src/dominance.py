from typing import Dict, Set, List, Optional
from cfg import CFG, BasicBlock
from utils import eprint

def _intersect(bbi: int, bbj: int, doms: List[int]):
    while bbi!=bbj:
        while bbi<bbj:
            bbi = doms[bbi]
        while bbj<bbi:
            bbj = doms[bbj]
    return bbi


class DominatorTree:
    def __init__(self, cfg: CFG):
        self.cfg = cfg
        self.dom: Dict[BasicBlock, Set[BasicBlock]] = {}
        self.idom: Dict[BasicBlock, Optional[BasicBlock]] = {}
        self.dom_frontiers: Dict[BasicBlock, Set[BasicBlock]] = {}
        self.successors: Dict[BasicBlock, Set[BasicBlock]] = {}
        self.compute_dominators()
        self.compute_dominance_frontiers()

    def compute_dominators(self):
        """
        Computes the dominators for each basic block.
        """
        # TODO: Implement the iterative algorithm to compute dominators.
        # ref: https://www.cs.tufts.edu/comp/150FP/archive/keith-cooper/dom14.pdf
        bbs_postorder: List[BasicBlock] = self.cfg.postorder_list()
        n = len(bbs_postorder)
        assert bbs_postorder[n-1] == self.cfg.entry_block
        bb2idx = {bbs_postorder[i]:i for i in range(n)}

        # initialize the dominators array
        doms: List[int] = [None]*(n-1) + [n-1]
        first_processed_pred: List[int] = [None]*n
        for i in range(n-1,-1,-1):
            for succ in bbs_postorder[i].successors:
                j=bb2idx[succ]
                if first_processed_pred[j] is None:
                    first_processed_pred[j] = i
        #eprint(first_processed_pred)

        changed = True
        while changed:
            changed = False
            for bbi in range(n-2, -1, -1):
                new_idom = first_processed_pred[bbi]
                for bbj in (bb2idx[pred] for pred in bbs_postorder[bbi].predecessors):
                    if doms[bbj] is not None:
                        new_idom = _intersect(bbj, new_idom, doms)
                if doms[bbi] != new_idom:
                    doms[bbi] = new_idom
                    changed = True

        self.idom = {bbs_postorder[bbi]:bbs_postorder[doms[bbi]] for bbi in range(n-1)}
        self.idom[bbs_postorder[n-1]]=None

        self.dom[bbs_postorder[n-1]] = set([bbs_postorder[n-1]])
        for bb in bbs_postorder[-2::-1]:
            self.dom[bb] = set([bb]).union(self.dom[self.idom[bb]])

        self.successors = {bb:set() for bb in bbs_postorder}
        for bb in bbs_postorder[-2::-1]:
            self.successors[self.idom[bb]].add(bb)


        #eprint(self.dom)
        #eprint(self.idom)
        #eprint(self.successors)



    def compute_dominance_frontiers(self):
        """
        Computes the dominance frontiers for each basic block.
        """
        # TODO: Implement dominance frontier computation.
        bbs = self.cfg.get_blocks()
        for bb in bbs:
            self.dom_frontiers[bb]=set()
        for bb in bbs:
            if len(bb.predecessors)<=1:
                continue
            for pred in bb.predecessors:
                pointer = pred
                while pointer != self.idom[bb]:
                    self.dom_frontiers[pointer].add(bb)
                    pointer = self.idom[pointer]
        #eprint(self.dom_frontiers)
