from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Optional
import time
import uvicorn

app = FastAPI()

active_users: Dict[str, float] = {}
pending_commands: Dict[str, List[dict]] = {}

class UserAction(BaseModel):
    user_id: str

class CommandAction(BaseModel):
    target_user_id: str
    command_type: str
    message: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "running", "message": "API is active on Render"}

@app.post("/activate")
def activate_user(user: UserAction):
    active_users[user.user_id] = time.time()
    if user.user_id not in pending_commands:
        pending_commands[user.user_id] = []
    commands = pending_commands.get(user.user_id, [])
    pending_commands[user.user_id] = []
    return {"status": "success", "commands": commands}

@app.get("/users")
def get_all_active_users():
    current_time = time.time()
    active_list = [user_id for user_id, last_seen in active_users.items() if current_time - last_seen < 300]
    return {"active_users": active_list}

@app.post("/send_command")
def send_command(cmd: CommandAction):
    if cmd.target_user_id not in pending_commands:
        pending_commands[cmd.target_user_id] = []
    new_cmd = {"type": cmd.command_type, "message": cmd.message}
    pending_commands[cmd.target_user_id].append(new_cmd)
    return {"status": "success", "message": f"Command sent to {cmd.target_user_id}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
