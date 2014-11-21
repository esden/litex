from migen.fhdl.std import *

from misoclib.ethmac.std import *
from misoclib.ethmac.preamble import *

from misoclib.ethmac.test import *

frame_preamble = [
	0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0xD5
]

frame_data = [
	0x00, 0x0A, 0xE6, 0xF0, 0x05, 0xA3, 0x00, 0x12,
    0x34, 0x56, 0x78, 0x90, 0x08, 0x00, 0x45, 0x00,
    0x00, 0x30, 0xB3, 0xFE, 0x00, 0x00, 0x80, 0x11,
    0x72, 0xBA, 0x0A, 0x00, 0x00, 0x03, 0x0A, 0x00,
    0x00, 0x02, 0x04, 0x00, 0x04, 0x00, 0x00, 0x1C,
    0x89, 0x4D, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05,
    0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D,
    0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13
]

class TB(Module):
	def __init__(self):

		sm = self.submodules

	# Streamer (DATA) --> PreambleInserter --> Logger (expect PREAMBLE + DATA)
		sm.inserter_streamer = PacketStreamer(frame_data)
		sm.preamble_inserter = PreambleInserter(8)
		sm.inserter_logger = PacketLogger()
		self.comb +=[
			self.inserter_streamer.source.connect(self.preamble_inserter.sink),
			self.preamble_inserter.source.connect(self.inserter_logger.sink),
		]

	# Streamer (PREAMBLE + DATA) --> CRC32Checher --> Logger (except DATA + check)
		sm.checker_streamer = PacketStreamer(frame_preamble + frame_data)		
		sm.preamble_checker = PreambleChecker(8)
		sm.checker_logger = PacketLogger()
		self.comb +=[
			self.checker_streamer.source.connect(self.preamble_checker.sink),
			self.preamble_checker.source.connect(self.checker_logger.sink),
		]


	def gen_simulation(self, selfp):
		for i in range(500):
			yield
		inserter_reference = frame_preamble + frame_data
		inserter_generated = self.inserter_logger.data

		checker_reference = frame_data
		checker_generated = self.checker_logger.data

		print_results("inserter", inserter_reference, inserter_generated)
		print_results("checker", checker_reference, checker_generated)

if __name__ == "__main__":
	from migen.sim.generic import run_simulation
	run_simulation(TB(), ncycles=1000, vcd_name="my.vcd", keep_files=True)