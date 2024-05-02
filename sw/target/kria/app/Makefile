TARGET_EXEC ?= bioemus.out

BUILD_DIR ?= ./build
SRC_DIRS ?= ./src

SRCS := $(shell find $(SRC_DIRS) -name *.cpp -or -name *.c -or -name *.s)
OBJS := $(SRCS:%=$(BUILD_DIR)/%.o)
DEPS := $(OBJS:.o=.d)

INC_DIRS := $(shell find $(SRC_DIRS) -type d)
INC_FLAGS := $(addprefix -I,$(INC_DIRS))
LDFLAGS := -pthread -lzmq

CPPFLAGS ?= $(INC_FLAGS) -MMD -MP -O3 -pthread -lzmq

# Debug
DEBUG_TARGET_EXEC := debug_$(TARGET_EXEC)
DEBUG_CPPFLAGS ?= $(CPPFLAGS) -DDEBUG
# DEBUG_CPPFLAGS += -DDBG_FIXED_SEED
# DEBUG_CPPFLAGS += -DDBG_PROBE_TSTAMP_STIM
# DEBUG_CPPFLAGS += -DDBG_PROBE_TSTAMP_SPIKES
# DEBUG_CPPFLAGS += -DDBG_PROBE_TSTAMP_WAVES

$(BUILD_DIR)/$(TARGET_EXEC): $(OBJS)
	$(CXX) $(OBJS) -o $@ $(LDFLAGS)

# assembly
$(BUILD_DIR)/%.s.o: %.s
	$(MKDIR_P) $(dir $@)
	$(AS) $(ASFLAGS) -c $< -o $@

# c source
$(BUILD_DIR)/%.c.o: %.c
	$(MKDIR_P) $(dir $@)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

# c++ source
$(BUILD_DIR)/%.cpp.o: %.cpp
	$(MKDIR_P) $(dir $@)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

# debug target
debug: CPPFLAGS := $(DEBUG_CPPFLAGS)
debug: $(BUILD_DIR)/$(DEBUG_TARGET_EXEC)

$(BUILD_DIR)/$(DEBUG_TARGET_EXEC): $(OBJS)
	$(CXX) $(OBJS) -o $@ $(LDFLAGS)

.PHONY: clean debug

clean:
	$(RM) -r $(BUILD_DIR)

-include $(DEPS)

MKDIR_P ?= mkdir -p
