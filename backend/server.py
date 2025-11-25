# import os
# from livekit import api
# from flask import Flask, request
# from dotenv import load_dotenv
# from flask_cors import CORS
# from livekit.api import LiveKitAPI, ListRoomsRequest
# import uuid

# load_dotenv()

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})

# async def generate_room_name():
#     name = "room-" + str(uuid.uuid4())[:8]
#     rooms = await get_rooms()
#     while name in rooms:
#         name = "room-" + str(uuid.uuid4())[:8]
#     return name

# async def get_rooms():
#     api = LiveKitAPI()
#     rooms = await api.room.list_rooms(ListRoomsRequest())
#     await api.aclose()
#     return [room.name for room in rooms.rooms]

# @app.route("/getToken")
# async def get_token():
#     name = request.args.get("name", "my name")
#     room = request.args.get("room", None)
    
#     if not room:
#         room = await generate_room_name()
        
#     token = api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET")) \
#         .with_identity(name)\
#         .with_name(name)\
#         .with_grants(api.VideoGrants(
#             room_join=True,
#             room=room
#         ))
    
#     return token.to_jwt()

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5001, debug=True)
from flask import Flask, request, jsonify
from flask_cors import CORS
from livekit import api
from dotenv import load_dotenv
import os, uuid
import function
load_dotenv(".env")
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_PUBLIC_URL = os.getenv("LIVEKIT_PUBLIC_URL")

@app.route("/getToken", methods=["GET"])
def get_token():
    try:
        if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
            return jsonify({"error": "Missing LiveKit API credentials"}), 500
        
        name = request.args.get("name", "student")
        room = request.args.get("room", f"room-{str(uuid.uuid4())[:8]}")

        # token = (
        #     api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        #     .with_identity(name)
        #     .with_grants(api.VideoGrants(
        #         room_join=True,
        #         room=room,
        #         can_publish=True,
        #         can_subscribe=True
        #     ))
        #     .to_jwt()
        # )
        grant = api.VideoGrants(
            room_join=True,
            room=room,
            can_publish=True,
            can_subscribe=True
        )

        # ⭐ TẠO TOKEN ĐÚNG CẤU TRÚC
        token = api.AccessToken(
            LIVEKIT_API_KEY,
            LIVEKIT_API_SECRET
        ).with_identity(name).with_grants(grant).to_jwt()
        
        return jsonify({
            "token": token,
            "room": room,
            "url": LIVEKIT_PUBLIC_URL or LIVEKIT_URL
        })
    except Exception as e:
        print(f"Error generating token: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/agentToken", methods=["GET"])
def get_agent_token():
    room = request.args.get("room")
    if not room:
        return jsonify({"error": "Missing room param"}), 400

    # token = (
    #     api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    #     .with_identity("ai_agent")
    #     .with_grants(api.VideoGrants(
    #         room_join=True,
    #         room=room,
    #         can_publish=True,
    #         can_subscribe=True
    #     ))
    #     .to_jwt()
    # )
    grant = api.VideoGrants(
        room_join=True,
        room=room,
        can_publish=True,
        can_subscribe=True
    )

    token = api.AccessToken(
        LIVEKIT_API_KEY,
        LIVEKIT_API_SECRET
    ).with_identity("ai_agent").with_grants(grant).to_jwt()
    return jsonify({
        "token": token,
        "url": LIVEKIT_URL
    })

@app.route("/aiFeedback/", methods=["POST", "OPTIONS"])  # Handle trailing slash
def ai_feedback():
    print(f"Request method: {request.method}")
    print(f"Request path: {request.path}")
    print(f"Request headers: {dict(request.headers)}")
    
    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response
    
    try:
        if not request.is_json:
            print("Warning: Request is not JSON")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_text = data.get("text", "")
        if not user_text:
            return jsonify({"error": "Text field is required"}), 400
        
        # Check if there are any user messages (lines starting with "You:")
        lines = user_text.split("\n")
        user_lines = [line for line in lines if line.strip().startswith("You:")]
        
        # If no user messages, return special feedback
        if not user_lines:
            bilingual = data.get("bilingual", True)
            if bilingual:
                feedback = """SECTION 1 - ENGLISH:
1. Overall Impression: You haven't spoken yet in this conversation. Please start speaking to receive feedback on your English pronunciation and accent.
2. Specific Feedback: No user input detected. The conversation only contains agent messages.
3. Google Pronunciation Respelling Suggestions: N/A - No user speech to analyze.
4. Additional Tips: To receive feedback, please speak during the conversation. The AI will analyze your pronunciation, accent, and speaking patterns.

SECTION 2 - VIETNAMESE:
1. Ấn tượng tổng quan: Bạn chưa nói trong cuộc trò chuyện này. Vui lòng bắt đầu nói để nhận phản hồi về phát âm và giọng tiếng Anh của bạn.
2. Phản hồi cụ thể: Không phát hiện đầu vào từ người dùng. Cuộc trò chuyện chỉ chứa tin nhắn từ agent.
3. Gợi ý cách phát âm theo Google: N/A - Không có lời nói của người dùng để phân tích.
4. Mẹo bổ sung: Để nhận phản hồi, vui lòng nói trong cuộc trò chuyện. AI sẽ phân tích phát âm, giọng nói và cách nói của bạn."""
            else:
                feedback = """Overall Impression: You haven't spoken yet in this conversation. Please start speaking to receive feedback on your English pronunciation and accent.

Specific Feedback: No user input detected. The conversation only contains agent messages.

Google Pronunciation Respelling Suggestions: N/A - No user speech to analyze.

Additional Tips: To receive feedback, please speak during the conversation. The AI will analyze your pronunciation, accent, and speaking patterns."""
            return jsonify({"feedback": feedback})
        
        # Get bilingual parameter (default: False for backward compatibility)
        bilingual = data.get("bilingual", True)
        
        print(f"Processing feedback for text length: {len(user_text)}, bilingual: {bilingual}")
        # Call AI feedback function
        feedback = function.aiFeedback(user_text, bilingual=bilingual)
        print("Feedback generated successfully")
        return jsonify({"feedback": feedback})
    except Exception as e:
        print(f"Error in ai_feedback: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
