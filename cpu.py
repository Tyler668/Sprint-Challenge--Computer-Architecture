"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = True
        self.ram = [0] * 256
        self.pc = 0
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.reg[4] = 0b00000000
        # self.reg[4] = self.reg[4]
        self.sp = 7
        self.mar = None
        self.mdr = None
        self.fl = None
        self.im = None
        self.ist = None

        self.func_registry = {
            0b10000010: self.do_ldi,
            0b01000111: self.do_prn,
            0b10100010: self.do_mul,
            0b01000101: self.do_push,
            0b01000110: self.do_pop,
            0b00000001: self.do_hlt,
            0b01010000: self.do_call,
            0b00010001: self.do_ret,
            0b10100000: self.do_add,
            0b10100111: self.do_cmp,
            0b01010101: self.do_jeq,
            0b01010110: self.do_jne,
            0b01010100: self.do_jmp
        }

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def load(self, program_filename=''):
        """Load a program into memory."""

        address = 0

        with open(program_filename) as f:
            for line in f:
                line = line.split('#')
                line = line[0].strip()
                # print(int(line, 2))

                if line != '':
                    line = int(line, 2)
                    self.ram[address] = line
                    address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def do_ldi(self):
        reg_addr = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[reg_addr] = value
        self.pc += 3

    def do_prn(self):
        reg_addr = self.ram_read(self.pc + 1)
        print(self.reg[reg_addr])
        self.pc += 2

    def do_mul(self):
        op1 = self.reg[0]
        op2 = self.reg[1]
        product = (op1 * op2)
        self.reg[0] = product
        self.pc += 3

    def do_push(self):
        # Decrement stack pointer
        # print('self.reg:', self.reg)
        self.reg[self.sp] -= 1
        # Copy value from register into memory
        reg_addr = self.ram[self.pc+1]
        value = self.reg[reg_addr]  # This is what we want to push

        address = self.reg[self.sp]
        self.ram[address] = value

        self.pc += 2

    def do_pop(self):
        ram_addr = self.reg[self.sp]
        value = self.ram[ram_addr]

        # Find correct place in reg to put value with instructions at pc + 1
        reg_addr = self.ram[self.pc + 1]

        # Set correct reg address to new value
        self.reg[reg_addr] = value

        # Increment stack pointer
        self.reg[self.sp] += 1

        # Iterate pc
        self.pc += 2

    def do_hlt(self):
        self.running = False
        self.pc += 1

    def do_add(self):
        op1 = self.reg[self.ram[self.pc + 1]]
        op2 = self.reg[self.ram[self.pc + 2]]
        sum = op1 + op2

        self.reg[0] = sum
        self.pc += 3

    def do_call(self):
        ret_addr = self.pc + 2

        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = ret_addr

        reg_num = self.ram[self.pc + 1]
        subroutine_addr = self.reg[reg_num]

        self.pc = subroutine_addr

    def do_ret(self):
        ret_addr = self.ram[self.reg[self.sp]]

        self.reg[self.sp] += 1

        self.pc = ret_addr

    def do_cmp(self):
        op1 = self.reg[self.ram[self.pc + 1]]
        op2 = self.reg[self.ram[self.pc + 2]]
        if op1 < op2:
            self.reg[4] = 0b00000100
        elif op1 > op2:
            self.reg[4] = 0b00000010
        elif op1 == op2:
            self.reg[4] = 0b00000001

        self.pc += 3

    def do_jeq(self):
        regStr = str(bin(self.reg[4]))
        lastDigit = regStr[-1]
        lastDigit = int(lastDigit)

        if lastDigit == 1:
            jump_to = self.reg[self.ram[self.pc + 1]]
            self.pc = jump_to
        else:
            self.pc += 2

    def do_jne(self):
        regStr = str(bin(self.reg[4]))
        lastDigit = regStr[-1]
        lastDigit = int(lastDigit)

        if lastDigit == 0:
            jump_to = self.reg[self.ram[self.pc + 1]]
            self.pc = jump_to
        else:
            self.pc += 2

    def do_jmp(self):
        self.pc = self.reg[self.ram[self.pc + 1]]

    def run(self):
        """Run the CPU."""

        while self.running:
            ir = self.ram[self.pc]  # Instruction register
            self.func_registry[ir]()

            if ir not in self.func_registry:
                print(f'Unknown instruction {ir} at address {self.pc}')
                sys.exit(1)


ls8 = CPU()
# Sprint
ls8.load("C:\\Users\\tyler\\Documents\\github\\Computer-Architecture\\ls8\\examples\\sctest.ls8")
ls8.run()
