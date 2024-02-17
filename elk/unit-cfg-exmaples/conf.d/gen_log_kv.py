#!/bin/python3
import random
from numpy.random import exponential
import math
import datetime
import time
import json

FORMAT = "kv" # plain, kv, json
TIMEFORMAT = "%F %T"
START_TIMESTAMP = int(time.time())  # timestamp yesterday
FINISH_TIMESTAMP = time.time() + 7 * 24 * 3600           # timestamp now + 1 hour
PARALLEL_FACTOR = 10                            # affect on timing and messages count

# GLOBAL_VARIABLE
global_timestamp = START_TIMESTAMP

# MODULES LIST
MODULES = ["mod1", "mod2", "mod3", "mod4", "mod5"]

# Список підмодулів
SUBMODULES = {
    "mod1": ["submodule1", "submodule2"],
    "mod2": ["submodule3", "submodule4", "submodule5", "submodule6"],
    "mod3": ["submodule7", "submodule8", "submodule9"],
    "mod4": ["submodule2", "submodule4"],
    "mod5": ["submodule3", "submodule5"],
}



# probabilities
DEFAULT_STATUS_PROBABILITIES = {"OK": 0.99, "WARN": 0.099, "FAIL": 0.001}
STATUS_PROBABILITIES = {
    "submodule1": {"OK": 0.9, "WARN": 0.09, "FAIL": 0.01},
    "submodule2": {"OK": 0.8, "WARN": 0.15, "FAIL": 0.05},
    "submodule3": {"OK": 0.7, "WARN": 0.3, "FAIL": 0},
    "submodule4": {"OK": 0.8, "WARN": 0.2, "FAIL": 0},
    "submodule5": {"OK": 0.9, "WARN": 0.1, "FAIL": 0},
    "submodule6": {"OK": 0.4, "WARN": 0.5, "FAIL": 0.1},
}

pop_coeffs = [
    0.1,  # 00:00 - 01:00
    0.1,  # 01:00 - 02:00
    0.2,  # 02:00 - 03:00
    0.1,  # 03:00 - 04:00
    0.4,  # 04:00 - 05:00
    0.6,  # 05:00 - 06:00
    0.8,  # 06:00 - 07:00
    0.9,  # 07:00 - 08:00
    1.0,  # 08:00 - 09:00
    1.2,  # 09:00 - 10:00
    1.4,  # 10:00 - 11:00
    1.5,  # 11:00 - 12:00
    1.6,  # 12:00 - 13:00
    1.5,  # 13:00 - 14:00
    1.4,  # 14:00 - 15:00
    1.3,  # 15:00 - 16:00
    1.2,  # 16:00 - 17:00
    1.5,  # 17:00 - 18:00
    1.8,  # 18:00 - 19:00
    1.6,  # 19:00 - 20:00
    1.2,  # 20:00 - 21:00
    0.8,  # 21:00 - 22:00
    0.5,  # 22:00 - 23:00
    0.3,  # 23:00 - 00:00
]
delay_coeffs = [1/c for c in pop_coeffs]

def generate_message(module, submodule):
  randint = random.randint(1,255)
  templates = [ f"Out of memory: Kill process {randint} ({submodule})",
            "The information being retrieved will not fit in the buffer.",
            "Memory allocation failure: Insufficient memory available.",
            f"Parameter '{submodule}' cannot be NULL.",
            f"An illegal value was given for parameter '{submodule}'.",
            f"The maximum number of connections ({randint}) have already been opened.",
            "Boolean values must be set to either TRUE or FALSE.",
            f"Cannot set this property/capability: {submodule}.",
            "This routine cannot be called after a command has been initiated to a Server.",
            "An illegal value was placed in the structure.",
            "The connection is dead/crashed.",
            "Not enough memory was available to save messages. All messages stored previously have been cleared.",
            "A result datatype cannot be bound to that host program variable type.",
            "Usage error: This routine has been called at an illegal time.",
            "Bind of result set item resulted in overflow.",
            "Bind of result set item resulted in underflow.",
            "Bind of result set item failed because illegal precision value specified.",
            "Bind of result set item failed because illegal scale value was specified.",
            "The data for a column is NULL but no indicator variable was available.",
            "The data for a column was truncated but no indicator variable was available.",
            "A bind was missing for a column.",
            "Fetched value was truncated.",
            "The Conn Router Table has not been initialized.",
            "No connections were configured for the requested Server.",
            "Temporary error: All connections to the requested server are currently in use.",
            "Invalid context handle.",
            "Invalid connection handle.",
            "Invalid command handle.",
            "An unexpected error occurred",
            "The operation requested is illegal on a client connection.",
          ]
  message_template = random.choice(templates)
  return message_template


def generate_log():
  module = random.choice(MODULES)
  submodule = None
  global global_timestamp
  if module in MODULES[-2:]:
    # some random for mod4,mod5
    if random.random() < 0.5:
      submodule = f"submodule{random.randint(1, 9)}"

  if not submodule:
    submodule = random.choice(SUBMODULES[module])

  ct = time.localtime(global_timestamp)
  cur_coeff, next_coeff  = delay_coeffs[ct.tm_hour], delay_coeffs[(ct.tm_hour+1) % 24]
  smoothed_coeff = (cur_coeff * (60 - ct.tm_min) + next_coeff * ct.tm_min) / 60
  timing = round(0.1 + abs(exponential(scale=PARALLEL_FACTOR/2) - 0.9), 3) 
  global_timestamp += ( timing / PARALLEL_FACTOR ) * smoothed_coeff

  local_timestamp = datetime.datetime.fromtimestamp(global_timestamp).strftime(TIMEFORMAT)
  status = random.choices(
        list(STATUS_PROBABILITIES.get(submodule, DEFAULT_STATUS_PROBABILITIES).keys()),
        weights=list(STATUS_PROBABILITIES.get(submodule, DEFAULT_STATUS_PROBABILITIES).values()),
    )[0]
  if timing > 30 and random.random() < 0.5:
    status = "FAIL"
  elif timing > 10 and status == 'OK'  and random.random() < 0.3:
    status = "WARN"
  elif timing > 30 and status == 'OK':
    status = "FAIL"

  if status == "FAIL":
    add_message = generate_message(module, submodule)
  else:
    add_message = ""

  if FORMAT == 'kv':
    if add_message:
        additional_message = f" {submodule}_message=\"{add_message}\""
    else:
        additional_message = ""
    return  f'{local_timestamp} module={module} submodule={submodule} timing={timing} status={status}{additional_message}'

  elif FORMAT == 'json':
    res = {'timestamp': local_timestamp, 'module': module, 'timing': timing, 'status':status}
    if add_message:
      res[f'{submodule}_message'] = add_message
    return json.dumps(res)

  elif FORMAT == 'plain':
    additional_message = f" {add_message}" if add_message else ""
    return f"{local_timestamp}: [{status}] {module}/{submodule}\t{timing:.3f}{additional_message}"



while global_timestamp < FINISH_TIMESTAMP:
  if global_timestamp > time.time():
    time.sleep(1)
    continue
  print(generate_log())

