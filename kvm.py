import sys, copy, json
from dataclasses import dataclass
from typing import Any
from importlib import import_module
from libtools import StackUnpacked
    
@dataclass
class Env:
    parent: Env | None
    table: dict[str, Any]

@dataclass
class Function:
    name: str
    start_pc: int
    env: Env

@dataclass
class Frame:
    return_pc: int
    stack_depth: int
    env: dict[str, Any]

class KVM:
    
    USE, LABEL, \
    PUSH, POP, \
    STOREL, STORE, LOAD, STOREG, LOADG, \
    JMP, JZ, JNZ, \
    FN, RET, CALL, HALT = range(16)
        
    def __init__(self):
        self.code: list[tuple[str, Any]] = []
        self.pc: int = 0

        self.data_stack: List[Any] = []
        self.call_stack: List[Frame] = []

        self.env: Env = Env(None, {})
        self.labels: dict[str, int] = {}
        
    def check_labels(self, instructions: list[tuple[str, Any]]):
        for op, arg in instructions:
            if op == KVM.LABEL:
                self.labels[arg] = len(self.code)
            else:
                self.code.append((op, arg))

        for i, instruction in enumerate(self.code):
            if instruction[0] in (KVM.JMP, KVM.JZ, KVM.JNZ):
                label_name = instruction[1]
                if label_name not in self.labels:
                    raise Exception(f'Unknown label: {label_name}')

    def push(self, value):
        self.data_stack.append(value)

    def pop(self):
        if self.data_stack:
            return self.data_stack.pop()
        else:
            raise Exception(f'Stack underflow')

    def load(self, name: str):
        if name in self.env.table:
            return self.env.table[name]

        current_env = self.env
        while current_env is not None:
            current_env = current_env.parent
            if current_env is not None and name in current_env.table:
                return current_env.table[name]

        raise Exception(f'Var {name} not found')

    def storel(self, name: str, value):
            self.env.table[name] = value
    
    def store(self, name: str, value):
        current_env = self.env
        while current_env is not None:
            current_env = current_env.parent
            if current_env is not None and name in current_env.table:
                current_env.table[name] = value
                return
        self.env.table[name] = value

    def loadg(self, name: str):
        current_env = self.env
        while current_env.parent is not None:
            current_env = current_env.parent
        if name in current_env.table:
            return current_env.table[name]

        raise Exception(f'Var {name} not found in global environment')

    def storeg(self, name: str, value):
        current_env = self.env
        while current_env.parent is not None:
            current_env = current_env.parent
        current_env.table[name] = value

    def run(self):
        while self.pc < len(self.code):
            instruction = self.code[self.pc]
            op = instruction[0]
            arg = instruction[1]

            match op:
                case KVM.PUSH:
                    self.push(arg)
                    self.pc += 1
                case KVM.POP:
                    self.pop()
                    self.pc += 1
                case KVM.STOREL:
                    value = self.pop()
                    self.store(arg, value)
                    self.pc += 1
                case KVM.STORE:
                    value = self.pop()
                    self.store(arg, value)
                    self.pc += 1
                case KVM.LOAD:
                    value = self.load(arg)
                    self.push(value)
                    self.pc += 1
                case KVM.LOADG:
                    value = self.loadg(arg)
                    self.push(value)
                    self.pc += 1
                case KVM.STOREG:
                    value = self.pop()
                    self.storeg(arg, value)
                    self.pc += 1
                case KVM.JMP:
                    self.pc = self.labels[arg]
                case KVM.JZ:
                    value = self.pop()
                    if not value:
                        self.pc = self.labels[arg]
                    else:
                        self.pc += 1
                case KVM.JNZ:
                    value = self.pop()
                    if value:
                        self.pc = self.labels[arg]
                    else:
                        self.pc += 1
                case KVM.FN:
                    if arg not in self.labels:
                        raise Exception(f'Unknown label: {label_name}')
                    
                    func = Function(
                        name=arg,
                        start_pc=self.labels[arg],
                        env=self.env
                        )
                    
                    self.push(func)
                    self.pc += 1
                case KVM.RET:
                    result = self.pop()
                    
                    frame = self.call_stack.pop()
                    self.data_stack = self.data_stack[:frame.stack_depth]
                    
                    self.env = frame.env
                    self.pc = frame.return_pc

                    self.push(result)
                case KVM.CALL:
                    func = self.pop()
 
                    args_count = arg
                    args = []

                    for _ in range(args_count):
                        args.insert(0, self.pop())

                        
                    if callable(func):
                        result = func(args)
                        if isinstance(result, StackUnpacked):
                            for value in result:
                                self.push(value)
                        elif result is not None:
                            self.push(result)
                        
                        self.pc += 1
                    elif isinstance(func, Function):
                        frame = Frame(
                            return_pc=self.pc + 1,
                            stack_depth=len(self.data_stack),
                            env=self.env)
                        self.call_stack.append(frame)

                        self.pc = func.start_pc

                        new_env = Env(parent=func.env, table={})
                            
                        for i, arg_value in enumerate(args):
                            new_env.table[f'-arg{i}'] = arg_value
                        self.env = new_env
                    else:
                        raise Exception(f'Object {func} is not callable')
                case KVM.USE:
                    #example: USE, ('stdlib', ('std', 'stack'))
                    if type(arg) is str:
                        kvm = KVM()
                        
                        try:
                            code_file = open(arg)
                        except FileNotFoundError:
                            raise Exception(f'Failed to find code file {arg}')

                        code = json.load(code_file)
                        
                        kvm.check_labels(code)
                        env = kvm.run()

                        self.env.table.update(env.table)
                    else:
                        package_name = arg[0]
                        lib_names = arg[1]

                        try:
                            package = import_module(package_name)
                        except ImportError:
                            raise Exception(f'Failed to find package {package_name}')

                        if not lib_names:
                            raise Exception('Required at least one library name')
                        else:
                            current_lib = getattr(package, lib_names[0], None)
                            if current_lib is None:
                                raise Exception(f'Package {package_name} has no library {lib_names[0]}')

                            for lib_name in lib_names[1:]:
                                current_lib = current_lib.get_child(lib_name)
                                if current_lib is None:
                                    raise Exception(f'Library {lib_name} has not found')
                            self.env.table.update(current_lib.get_table())
                    self.pc += 1
                case KVM.HALT:
                    return self.env
