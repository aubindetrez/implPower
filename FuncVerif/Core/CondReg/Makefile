export COCOTB_REDUCED_LOG_FMT=1
export SIM = icarus
export TOPLEVEL_LANG = verilog
export TOPLEVEL = CondReg
export MODULE = test_condreg
export TOOLS = $(shell git rev-parse --show-toplevel)/Tools
export VERILOG_SOURCES = $(shell pwd)/$(TOPLEVEL).v
export SVERILOG_SOURCES = $(shell git rev-parse --show-toplevel)/Logic/Core/$(TOPLEVEL).sv

include $(shell cocotb-config --makefiles)/Makefile.sim

# Convert systemVerilog to verilog
${VERILOG_SOURCES}: ${SVERILOG_SOURCES}
	${TOOLS}/convert_sv ${SVERILOG_SOURCES} ${VERILOG_SOURCES}

clean_all: clean
	rm -rf __pycache__ results.xml *.v # Clean generated files
