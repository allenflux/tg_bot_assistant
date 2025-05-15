from flask import Flask, request, jsonify, render_template, redirect, url_for
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import asyncio

# ====== CONFIGURATION ======
api_id = 814757     # <-- Replace with your own API ID
api_hash = '6705a5e22c1d46f27defab5e019d6754'  # <-- Replace with your own API hash
session_name = 'session_file'  # The local session file name
# ============================

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Initialize TelegramClient and connect once
client = TelegramClient(session_name, api_id, api_hash, loop=loop)
loop.run_until_complete(client.connect())

# Simple wrapper to run async in the shared event loop
def run_async(coro):
    return loop.run_until_complete(coro)

# ==============================
# Flask Routes
# ==============================

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        run_async(client.send_code_request(phone))
        return render_template('code.html', phone=phone)
    return render_template('login.html')

@app.route('/code', methods=['POST'])
def code():
    phone = request.form['phone']
    code = request.form['code']
    password = request.form.get('password')
    try:
        if run_async(client.is_user_authorized()):
            return redirect(url_for('get_members_form'))
        run_async(client.sign_in(phone, code))
    except SessionPasswordNeededError:
        if password:
            run_async(client.sign_in(password=password))
        else:
            return render_template('code.html', phone=phone, error="Two-step verification password required.")
    return redirect(url_for('get_members_form'))

@app.route('/get_members_form')
def get_members_form():
    return '''
        <form method="get" action="/get_members">
            Group link: <input type="text" name="group_link">
            <input type="submit" value="Get Members">
        </form>
    '''

@app.route('/get_members', methods=['GET'])
def get_members():
    group_link = request.args.get('group_link')
    if not group_link:
        return jsonify({"error": "Missing group_link parameter"}), 400
    try:
        members = run_async(fetch_members(group_link))
        return jsonify(members)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================
# Async Telegram Logic
# ==============================

async def fetch_members(group_link):
    if not await client.is_user_authorized():
        raise Exception("Client not authorized. Please log in.")
    try:
        # Try to parse as a normal public group/channel
        entity = await client.get_entity(group_link)
    except:
        # If fails, treat it as an invite link
        if '/joinchat/' in group_link or '+' in group_link:
            hash_part = group_link.split('/')[-1] if '/joinchat/' in group_link else group_link.split('+')[-1]
            try:
                invite = await client(ImportChatInviteRequest(hash_part))
                entity = invite.chats[0]
            except Exception as e:
                # Already a participant is not a fatal error; try to get entity normally
                if "already a participant" in str(e).lower():
                    entity = await client.get_entity(group_link)
                else:
                    raise e
        else:
            raise Exception("Invalid group link format")

    # Supergroups
    if hasattr(entity, 'megagroup') and entity.megagroup:
        all_participants = []
        offset = 0
        limit = 100
        while True:
            participants = await client(GetParticipantsRequest(
                channel=entity,
                filter=ChannelParticipantsSearch(''),
                offset=offset,
                limit=limit,
                hash=0
            ))
            if not participants.users:
                break
            all_participants.extend(participants.users)
            offset += len(participants.users)
        # return [p.to_dict() for p in all_participants]
        return [serialize_user(p) for p in all_participants]
    else:
        # Normal group (non-supergroup)
        participants = await client.get_participants(entity)
        # return [p.to_dict() for p in participants]
        return [serialize_user(p) for p in participants]

def serialize_user(user):
    return {
        "id": user.id,
        "username": getattr(user, "username", None),
        "first_name": getattr(user, "first_name", None),
        "last_name": getattr(user, "last_name", None),
        "phone": getattr(user, "phone", None),
        "is_bot": getattr(user, "bot", False),
    }

# ==============================
# Flask Start
# ==============================

if __name__ == '__main__':
    app.run(debug=True)