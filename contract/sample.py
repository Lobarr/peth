# Declare the state variables
# will only happen once during contract creation
state["students"]: list = [] if "students" not in state else state["students"]
state["teacher"]: str = "" if "teacher" not in state else state["teacher"]
state["max_size"]: int = 30 if "max_size" not in state else state["max_size"]
state["current_size"]: int = 0 if "current_size" not in state else state["current_size"]
state["subject"] = "" if "subject" not in state else state["subject"]
# Declare only once to retreat it as const
state["admin"] = msg["sender"] if "admin" not in state else state["admin"]

def addStudent(name: str) -> bool:
  # Admin check
  if msg["sender"] == state["admin"]:
    # Add student only if class size not full
    if state["current_size"] < state["max_size"]:
      state["students"].append(name)
      state["current_size"] += 1
      
      return True
  return False

def removeStudent(name:str) -> bool:
  # Admin check
  if msg["sender"] == state["admin"]:
    # Check if the student even exists
    if data["name"] in state["students"]:
      state["students"].remove(name)
      return True
  
  return False

def setTeacher(teacher: str) -> bool:
  try:
    if msg["sender"] == state["admin"]:
      state["teacher"] = teacher
      return True
  except:
    return False
  
def setMaxSize(new_max_size: int) -> bool:
  try: 
    if msg["sender"] == state["admin"]:
      state["max_size"] = new_max_size
      return True
  except:
    return False

def setSubject(subject: str) -> bool:
  try:
    if msg["sender"] == state["admin"]:
      state["subject"] = subject
      return True
  except:
    return False

def getStudents() -> list:
  return state["students"]

def getTeacher() -> str:
  return state["teacher"]

def getMaxSize() -> int:
  return state["max_size"]

def getCurrentSize() -> int:
  return state["current_size"]

def getSubject() -> str:
  return state["subject"]
