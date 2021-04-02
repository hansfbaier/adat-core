#!/usr/bin/env python3
"""
    synchronous shift register: bits appear in the output at the next
                                clock cycle
"""
from nmigen import Elaboratable, Signal, Module, Cat
from nmigen.cli import main_parser, main_runner

# pylint: disable=too-few-public-methods
class InputShiftRegister(Elaboratable):
    """shift register with given depth in bits"""
    def __init__(self, depth):
        self.enable_in = Signal()
        self.bit_in    = Signal()
        self.clear_in  = Signal()
        self.value_out = Signal(depth)

    def elaborate(self, platform) -> Module:
        """build the module"""
        m = Module()

        with m.If(self.clear_in):
            m.d.sync += self.value_out.eq(0)
        with m.Elif(self.enable_in):
            m.d.sync += self.value_out.eq((self.value_out << 1) | self.bit_in)

        return m

# pylint: disable=too-few-public-methods
class OutputShiftRegister(Elaboratable):
    """shift register with given depth in bits"""
    def __init__(self, depth, rotate=False):
        self.enable_in = Signal()
        self.we_in     = Signal()
        self.bit_out   = Signal()
        self.value_in  = Signal(depth)
        self.rotate    = rotate

    def elaborate(self, platform) -> Module:
        """build the module"""
        m = Module()

        value = Signal.like(self.value_in)
        m.d.comb += self.bit_out.eq(value[0])

        with m.If(self.we_in):
            m.d.sync += value.eq(self.value_in)
        with m.Elif(self.enable_in):
            m.d.sync += value.eq(Cat(value[1:], value[0])) if self.rotate else value.eq((value >> 1))

        return m


if __name__ == "__main__":
    parser = main_parser()
    parser.add_argument("-d", "--depth", dest="depth",
        metavar="DEPTH", type=int, default=8,
        help="set depth of shiftregister to DEPTH  (default: %(default)s)")
    args = parser.parse_args()
    reg_depth = args.depth
    module = InputShiftRegister(reg_depth)
    main_runner(parser, args, module, name="InputShiftRegister",
                ports=[module.enable_in, module.bit_in, module.value_out])
    module = OutputShiftRegister(reg_depth)
    main_runner(parser, args, module, name="OutputShiftRegister",
                ports=[module.enable_in, module.we_in, module.bit_out, module.value_in])
