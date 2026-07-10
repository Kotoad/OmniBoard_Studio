# OmniBoard Studio — Block Reference (from the PyQt implementation)

All blocks and their parameters, extracted from the Python (PyQt) version of the app
(`../OmniBoard_Studio_PyQt`).

Sources:
- `Blocks_window_pyqt.py` — block library (tabs, dropdowns, block type names)
- `Data_control.py` (`inicilize_date`) — data stored per block + default values
- `code_compiler.py` — generated Python code and which parameters each block reads
- `spawn_blocks_pyqt.py` — rendering, colors, number of output ports

Compilation has two modes: **MC** (MicroPython, `machine` module — RPi Pico) and
**GPIO** (`RPi.GPIO` — Raspberry Pi boards). Where the generated code differs, both are shown.

---

## Common fields (every block)

Every block's data dict contains these fields regardless of type:

| Field | Meaning |
|---|---|
| `type` | Block type name (e.g. `"If"`, `"Blink_LED"`) |
| `id` | Unique block id |
| `widget` | Reference to the `BlockGraphicsItem` |
| `width`, `height` | Block dimensions |
| `x`, `y` | Position on the canvas (grid-snapped, grid = 25 px) |
| `outputs` | Number of output ports |
| `in_connections`, `out_connections` | Wire connections |
| `canvas` | Canvas the block lives on |

### Value types (`*_type` fields)

Parameters named `value_*_name` come with a matching `value_*_type` that tells the
compiler how to resolve the value (`resolve_value`):

- `Variable` — looked up in the variables registry (`Variables_main['name']['value']`)
- `Device` — looked up in the devices registry, resolves to the device's PIN (`Devices_main['name']['PIN']`)
- literal — anything that is not a known variable/device reference is emitted as-is

---

## Basic blocks (`basic` tab)

### Start
- **Description:** Entry point of the program. Exactly one per canvas; compilation begins here.
- **Parameters:** none (common fields only)
- **Ports:** 0 in, 1 out
- **Generated code:** program preamble (imports, setup, reporter thread, `try:` + `time.sleep(1.5)`)

### End
- **Description:** End point of the program / of a function body.
- **Parameters:** none (common fields only)
- **Ports:** 1 in, 0 out
- **Generated code:** nothing on the main canvas; inside a function it closes the function body and returns compilation to the caller

### Timer
- **Description:** Waits for a given time before continuing.
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `sleep_time` | `"1000"` | Wait time in milliseconds |
- **Ports:** 1 in, 1 out
- **Generated code:** `time.sleep({sleep_time}/1000)`

### Networks
- **Description:** Splits the program into parallel branches ("networks"). Branches can be added/removed with the +/− buttons on the block.
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `networks` | `2` | Number of parallel branches (= number of output ports) |
- **Ports:** 1 in, `networks` outs (`out_1` … `out_n`)
- **Generated code:** no code of its own — each output branch is compiled one after another

### Return
- **Description:** Returns a value from a function.
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `value_1_name` | `"N"` | Value to return |
  | `value_1_type` | `None` | How to resolve it (Variable / Device / literal) |
- **Ports:** 1 in, 1 out
- **Generated code:** `return {value_1}`

---

## Logic blocks (`logic` tab)

### Cycles (dropdown)

#### If
- **Description:** Conditional branching. Conditions can be added/removed with the +/− buttons (if → elif → … → else). Number of outputs = `conditions` + 1 (the last output is the else branch).
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `conditions` | `1` | Number of conditions (if + elifs) |
  | `first_vars` | `{}` | Left operand per condition: `value_{i}_1_name` / `value_{i}_1_type` |
  | `operators` | `{}` | Comparison operator per condition: `operator_{i}` (`==`, `!=`, `<`, `<=`, `>`, `>=`) |
  | `second_vars` | `{}` | Right operand per condition: `value_{i}_2_name` / `value_{i}_2_type` |
- **Ports:** 1 in, `conditions + 1` outs (`out_1` … true branches, last = else)
- **Generated code:**
  ```python
  if {v1_1} {op_1} {v1_2}:
      ...          # out_1
  elif {v2_1} {op_2} {v2_2}:
      ...          # out_2
  else:
      ...          # last output
  ```

#### While
- **Description:** Loop that runs while a condition holds. Output 1 is the loop body (true), output 2 continues after the loop (false).
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `value_1_name` / `value_1_type` | `"N"` / `None` | Left operand |
  | `operator` | `"=="` | Comparison operator |
  | `value_2_name` / `value_2_type` | `"N"` / `None` | Right operand |
- **Ports:** 1 in, 2 outs (`out_1` = body, `out_2` = after loop)
- **Generated code:** `while {value_1} {operator} {value_2}:`

#### While_true
- **Description:** Infinite loop.
- **Parameters:** none (common fields only)
- **Ports:** 1 in, 1 out (loop body)
- **Generated code:** `while True:`

#### Switch
- **Description:** Sets a device output HIGH or LOW (ON/OFF toggle drawn on the block).
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `value_1_name` | `"N"` | Target device |
  | `switch_state` | `False` | Desired state (True = ON, False = OFF) |
- **Ports:** 1 in, 1 out
- **Generated code:**
  - MC: `{device}.value(1)` / `{device}.value(0)`
  - GPIO: `GPIO.output({device}, GPIO.HIGH)` / `GPIO.output({device}, GPIO.LOW)`

#### For_Loop
- **Description:** Listed in the block library dropdown, but **not implemented** — it has no
  entry in `Data_control.inicilize_date` and no handler in the compiler's `process_map`.

### Comparison (dropdown)

All six blocks share the same structure; only the operator differs.
They behave like an if/else: output 1 = true branch, output 2 = false branch.

| Block | Operator |
|---|---|
| Lower | `<` |
| Greater | `>` |
| Equal | `==` |
| Not_equal | `!=` |
| Greater_equal | `>=` |
| Lower_equal | `<=` |

- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `value_1_name` / `value_1_type` | `"N"` / `None` | Left operand |
  | `value_2_name` / `value_2_type` | `"N"` / `None` | Right operand |
  | `operator` | `None` | Operator (set from block type) |
- **Ports:** 1 in, 2 outs (`out_1` = true, `out_2` = false)
- **Generated code:**
  ```python
  if {value_1} {op} {value_2}:
      ...          # out_1
  else:
      ...          # out_2
  ```

### Bool logic (dropdown)

- **Parameters (all seven blocks):**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `value_1_name` / `value_1_type` | `"N"` / `None` | First operand |
  | `value_2_name` / `value_2_type` | `"N"` / `None` | Second operand (**`Not` has none** — `value_2_name` is `None`) |
  | `operator` | `None` | Unused (operator comes from block type) |
- **Ports:** 1 in, 1 out
- **Generated code:**
  | Block | Code |
  |---|---|
  | Not | `{v1} = not {v1}` (in-place, no branching) |
  | And | `if {v1} == True and {v2} == True:` |
  | Nand | `if {v1} == False or {v2} == False:` |
  | Or | `if {v1} == True or {v2} == True:` |
  | Nor | `if {v1} == False and {v2} == False:` |
  | Xor | `if {v1} != {v2}:` |
  | Xnor | `if {v1} == {v2}:` |

---

## Math blocks (`math` tab)

### Plus, Minus, Multiply, Divide, Modulo, Power, Root

All share the same structure; only the operator differs.

| Block | Operator | Generated code |
|---|---|---|
| Plus | `+` | `{result} = {v1} + {v2}` |
| Minus | `-` | `{result} = {v1} - {v2}` |
| Multiply | `*` | `{result} = {v1} * {v2}` |
| Divide | `/` | `{result} = {v1} / {v2}` |
| Modulo | `%` | `{result} = {v1} % {v2}` |
| Power | `**` | `{result} = {v1} ** {v2}` |
| Root | `** 0.5` | `{result} = {v1} ** 0.5 {v2}` *(square root of v1)* |

- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `value_1_name` / `value_1_type` | `"N"` / `None` | First operand |
  | `value_2_name` / `value_2_type` | `"N"` / `None` | Second operand |
  | `operator` | `None` | Operator (set from block type) |
  | `result_var_name` / `result_var_type` | `"N"` / `None` | Variable that receives the result |
- **Ports:** 1 in, 1 out

### Random_number
- **Description:** Stores a random integer from a range into a variable.
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `value_1_name` / `value_1_type` | `"N"` / `None` | Lower bound |
  | `value_2_name` / `value_2_type` | `"N"` / `None` | Upper bound |
  | `result_var_name` / `result_var_type` | `"N"` / `None` | Target variable |
- **Ports:** 1 in, 1 out
- **Generated code:** `{result} = random.randint({v1}, {v2})`

### Plus_one / Minus_one
- **Description:** Increments / decrements a variable by 1.
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `value_1_name` / `value_1_type` | `"N"` / `None` | Variable to modify |
- **Ports:** 1 in, 1 out
- **Generated code:** `{v1} = {v1} + 1` / `{v1} = {v1} - 1`

---

## I/O blocks (`IO` tab)

### Button
- **Description:** Reads a physical button and branches: output 1 = pressed (ON), output 2 = not pressed (OFF).
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `value_1_name` / `value_1_type` | `"N"` / `None` | Button device (resolves to its PIN) |
- **Ports:** 1 in, 2 outs (`out_1` = ON, `out_2` = OFF)
- **Generated code:**
  ```python
  if Button().is_pressed({device}):
      ...          # out_1 (ON)
  else:
      ...          # out_2 (OFF)
  ```

### LED (dropdown)

#### Blink_LED
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `value_1_name` / `value_1_type` | `"N"` / `None` | LED device |
  | `sleep_time` | `"1000"` | Blink duration in milliseconds |
- **Generated code:** `led.Blink_LED({device}, {sleep_time})`

#### Toggle_LED
- **Parameters:** `value_1_name` / `value_1_type` (default `"N"` / `None`) — LED device
- **Generated code:** `led.Toggle_LED({device})`

#### PWM_LED
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `value_1_name` / `value_1_type` | `"N"` / `None` | LED device |
  | `PWM_value` | `"50"` | Duty cycle / brightness value |
- **Generated code:** `led.PWM_LED({device}, {PWM_value})`

#### RGB_LED
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `first_vars` | `{}` | Three pins: `value_{i}_1_name` / `value_{i}_1_type` for i = 1..3 (R, G, B) |
  | `second_vars` | `{}` | Three PWM values: `value_{i}_2_PWM` / `value_{i}_2_type` for i = 1..3 |
- **Generated code:** `led.RGB_LED({pin1}, {pin2}, {pin3}, {pwm1}, {pwm2}, {pwm3})`

#### LED_ON / LED_OFF
- **Parameters:** `value_1_name` / `value_1_type` (default `"N"` / `None`) — LED device
- **Generated code:** `led.LED_ON({device})` / `led.LED_OFF({device})`

All LED blocks: 1 in, 1 out. The `led = LED()` / `btn = Button()` helper objects are
emitted in the program preamble when any LED/Button block is present.

---

## Function blocks (`Functions` tab)

### Function
- **Description:** Call of a user-defined function (each function has its own canvas with its own Start/End). The first time a Function block is compiled, the function definition is emitted; every occurrence emits a call.
- **Parameters:**
  | Parameter | Default | Meaning |
  |---|---|---|
  | `name` | — | Function name |
  | `return_var_name` / `return_var_type` | `""` / `None` | Variable in the caller that receives the return value |
  | `internal_vars.ref_vars` | `{}` | Function's own variable parameters (names in the `def` signature) |
  | `internal_vars.main_vars` | `{}` | Arguments passed from the caller (per entry: `name`, `type`) |
  | `internal_devs.ref_devs` | `{}` | Function's device parameters (names in the `def` signature) |
  | `internal_devs.main_devs` | `{}` | Device arguments passed from the caller |
- **Ports:** 1 in, 1 out
- **Generated code:**
  ```python
  def {name}(
      {ref_var_1},
      ...
      {ref_dev_1},
      ...
  ):
      ...              # function canvas body

  {return_var} = {name}(
      {main_var_1},
      ...
  )
  ```

---

## Block colors (canvas rendering)

| Category | Blocks | Color |
|---|---|---|
| Life cycle | Start, Return, Networks | `#6AAE8B` (green) |
| Life cycle | End | `#FF6B6B` (red) |
| Control flow | Timer, If, While, While_true, Switch | `#7A9BC9` (blue) |
| Input | Button | `#A0A8AE` (gray) |
| Functions | Function | `#CE8B52` (orange) |
| Operations | all math, comparison and bool blocks | `#A07AC9` (purple) |
| LED control | Blink_LED, Toggle_LED, PWM_LED, RGB_LED, LED_ON, LED_OFF | `#8AAE6A` (light green) |
