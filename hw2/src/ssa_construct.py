from typing import Dict, List, Set, Tuple, Deque
from bril import Function, Instruction, ValueOperation, Label
from cfg import CFG, BasicBlock
from dominance import DominatorTree
from collections import deque
from operator import add
from functools import reduce
from utils import eprint

def construct_ssa(function: Function):
    """
    Transforms the function into SSA form.
    """
    cfg = CFG(function)
    dom_tree = DominatorTree(cfg)

    # Step 1: Variable Definition Analysis
    global_vars, def_blocks = collect_definitions(cfg)

    # Step 2: Insert φ-Functions
    insert_phi_functions(cfg, dom_tree, global_vars, def_blocks)

    # Step 3: Rename Variables
    rename_variables(cfg, dom_tree, global_vars)

    # After transformation, update the function's instructions
    reconstruct_instructions(cfg)

def collect_definitions(cfg: CFG) -> Tuple[Set[str], Dict[str, Set[BasicBlock]]]:
    """
    Collects the set of basic blocks in which each variable is defined.
    """
    # TODO: Implement variable definition collection
    global_vars: Set[str] = set()
    def_blocks: Dict[str, Set[BasicBlock]] = {arg['name']:set([cfg.entry_block]) for arg in cfg.function.args}
    bbs = cfg.get_blocks()

    for bb in bbs:
        killed_vars = set()
        for instr in bb.instructions:
            if hasattr(instr, 'args'):
                for arg in instr.args:
                    if arg not in killed_vars:
                        global_vars.add(arg)
            if hasattr(instr, 'dest'):
                killed_vars.add(instr.dest)
                def_blocks[instr.dest] = def_blocks.get(instr.dest, set()).union(set([bb]))

    eprint("global vars:", global_vars)
    eprint("def_blocks:", def_blocks)
    return global_vars, def_blocks

def has_phi_function(var: str, bb: BasicBlock) -> bool:
    return var in [instr.dest for instr in bb.instructions if instr.op=='phi']


def insert_phi_functions(cfg: CFG, dom_tree: DominatorTree, global_vars: Set[str], def_blocks: Dict[str, Set[BasicBlock]]):
    """
    Inserts φ-functions into the basic blocks.
    """
    # TODO: Implement φ-function insertion using dominance frontiers
    eprint("inserting phi-functions ...")
    argtype = {arg['name']:arg['type'] for arg in cfg.function.args}
    for var in global_vars:
        processed_def_blocks = deque(def_blocks[var]) # stack or queue
        while processed_def_blocks:
            bb = processed_def_blocks.pop()
            eprint(f"def of {var} in bb {bb.label}")
            var_types = [instr.type for instr in bb.instructions if hasattr(instr, 'dest') and instr.dest == var]
            var_type = var_types[-1] if var_types else argtype[var]
            for frontier_bb in dom_tree.dom_frontiers[bb]:
                if not has_phi_function(var, frontier_bb):
                    frontier_bb.instructions = [ValueOperation({
                        'op': 'phi',
                        'dest': var,
                        'type': var_type
                    })] + frontier_bb.instructions
                    processed_def_blocks.append(frontier_bb)
                    #eprint(f"basic block {frontier_bb.label}")
                    #eprint("instrs:", frontier_bb.instructions)

def init_var(var: str, counter: Dict[str, int], stack: Dict[str, Deque[int]]):
    assert '.' not in var, var
    counter[var] = 0
    stack[var] = deque()

def base_name(var: str) -> str:
    return var.split('.')[0]

def current_name(var: str, counter: Dict[str, int], stack: Dict[str, Deque[int]]) -> str:
    if not stack.get(var):
        return new_name(var, counter, stack)
    return f"{var}.{stack[var][-1]}"

def new_name(var: str, counter: Dict[str, int], stack: Dict[str, Deque[int]]) -> str:
    if var not in counter.keys():
        init_var(var, counter, stack)
    stack[var].append(counter[var]) # push to stack
    counter[var] += 1
    return current_name(var, counter, stack)

def rename(bb: BasicBlock, dom_tree: DominatorTree, counter: Dict[str, int], stack: Dict[str, Deque[int]]):
    #phi_functions = filter(lambda instr: instr.op=='phi', bb.instructions)
    eprint(f"renaming block {bb.label}")
    for instr in bb.instructions:
        if hasattr(instr, 'args') and instr.op != 'phi': # no need to rename arguments of phi function
            for argi in range(len(instr.args)):
                instr.args[argi] = current_name(instr.args[argi], counter, stack)
        if hasattr(instr, 'dest'):
            instr.dest = new_name(instr.dest, counter, stack)
    for succ in bb.successors:
        eprint(f"in succ {succ.label}")
        for phi in filter(lambda instr: instr.op=='phi', succ.instructions):
            phi.args.append(current_name(base_name(phi.dest), counter, stack))
            phi.labels.append(bb.label)
    for dom_succ in dom_tree.successors[bb]:
        rename(dom_succ, dom_tree, counter, stack)
    for instr in filter(lambda instr: hasattr(instr, 'dest'), bb.instructions):
        stack[base_name(instr.dest)].pop() # pop from stack


def rename_variables(cfg: CFG, dom_tree: DominatorTree, global_vars: Set[str]):
    """
    Renames variables to ensure each assignment is unique.
    """
    # TODO: Implement variable renaming
    eprint("start renaming ...")
    #counter: Dict[str, int] = {var:0 for var in global_vars}
    #stack: Dict[str, Deque[int]] = {var:deque() for var in global_vars}
    counter: Dict[str, int] = dict()
    stack: Dict[str, Deque[int]] = dict()
    #eprint(dom_tree.successors)

    for arg in cfg.function.args:
        arg['name'] = new_name(arg['name'], counter, stack)
    rename(cfg.entry_block, dom_tree, counter, stack)

def reconstruct_instructions(cfg: CFG):
    """
    Reconstructs the instruction list from the CFG after SSA transformation.
    """
    # TODO: Implement instruction reconstruction
    labels: List[Label] = [instr for instr in cfg.function.instrs if isinstance(instr, Label)]
    block_instrs: List[List[Instruction]] = [cfg.blocks[label.label].instructions for label in labels]
    #eprint(labels)
    #eprint(cfg.entry_block)

    cfg.function.instrs = [Label({'label':cfg.entry_block.label})] + cfg.entry_block.instructions + reduce(
        add,
        ([label]+instrs for (label, instrs) in zip(labels, block_instrs)),
        []
    )
