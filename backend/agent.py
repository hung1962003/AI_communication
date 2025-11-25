from prompts import WELCOME_MESSAGE, conversation_prompt, feedback_prompt
import os
from dotenv import load_dotenv
from livekit import agents ,rtc
from livekit.agents import (
    Agent, AgentSession, JobContext, WorkerOptions,
    AutoSubscribe, RoomInputOptions
)
from livekit.agents.llm import ChatContext, ChatRole
from livekit.plugins import openai, deepgram, silero
from openai import OpenAI
import inspect
import asyncio
# ==== Load biến môi trường ====
load_dotenv(".env")

# ==== Khởi tạo client OpenAI để chấm feedback ====
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==== Định nghĩa Agent ====
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=conversation_prompt)

# ==== Hàm tiện ích cho HTTP session (optional) ====
def _http_kwarg_for(klass, http):
    try:
        params = inspect.signature(klass.__init__).parameters
        if "http_session" in params:
            return {"http_session": http}
        if "session" in params:
            return {"session": http}
    except Exception:
        pass
    return {}

# ==== Hàm khởi tạo chính ====
async def entrypoint(ctx: agents.JobContext):
    # Khởi tạo STT / TTS / LLM / VAD
    stt = deepgram.STT(model="nova-2")
    tts = openai.TTS(voice="alloy")
    vad = silero.VAD.load()

    # Dùng OpenAI plugin để gọi Groq API
    llm_kwargs = _http_kwarg_for(openai.LLM, None)
    llm = openai.LLM(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "1.0"))
    )

    # Khởi tạo agent chính
    operator = Assistant()

    # Tạo phiên hội thoại (session)
    va = AgentSession(
        stt=stt,
        tts=tts,
        llm=llm,
        vad=vad,
        preemptive_generation=True
    )
    
    async def handle_session_start():
        try:
            print("🔹 Session started! Bắt đầu khởi tạo context hoặc TTS ...")
            await asyncio.sleep(1)
            await va.generate_reply(instructions=WELCOME_MESSAGE)
            print("✅ Hoàn tất khởi tạo!")
        except Exception as e:
            print("⚠️ Lỗi trong handle_session_start:", e)

    # Gửi lời chào ban đầu
    @va.on("session_started")
    def on_session_started(_):
        asyncio.create_task(handle_session_start())
        
    # # --- conversation_item_added: sync wrapper + async handler ---
    # async def handle_user_message_async(ev):
    #     try:
    #         if ev.item.role != "user":
    #             return
    #         text = ev.item.text_content.strip()
    #         if not text:
    #             return

    #         # Nếu client.chat.completions.create là blocking, chạy trong thread
    #         def call_feedback():
    #             return client.chat.completions.create(
    #                 model="gpt-4o-mini",
    #                 messages=[
    #                     {"role": "system", "content": feedback_prompt},
    #                     {"role": "user", "content": text}
    #                 ]
    #             )

    #         # Chạy blocking call trong thread pool để không block event loop
    #         fb_resp = await asyncio.to_thread(call_feedback)

    #         # Trích nội dung feedback — tùy cấu trúc response của client
    #         try:
    #             feedback = fb_resp.choices[0].message.content
    #         except Exception:
    #             # fallback: convert to str
    #             feedback = str(fb_resp)

    #         print(f"\n📝 Feedback for user:\n{feedback}\n")

    #         # (Tuỳ bạn muốn) gửi feedback như một reply TTS:
    #         # await va.generate_reply(instructions=feedback)  # hoặc tuỳ logic
    #     except Exception as e:
    #         print("⚠️ Lỗi khi xử lý user message:", e)
    # # Sự kiện: khi có tin nhắn mới từ user
    # @va.on("conversation_item_added")
    # def on_user_message(ev):
    #      # wrapper sync — tạo task cho handler async
    #     asyncio.create_task(handle_user_message_async(ev))

    # Bắt đầu agent
    await va.start(
        room=ctx.room,
        agent=operator,
        room_input_options=RoomInputOptions(video_enabled=False, close_on_disconnect=True),
    )

    # Kết nối vào phòng LiveKit
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    await va.generate_reply(instructions=WELCOME_MESSAGE)
    @ctx.room.on("disconnected")
    def on_disconnected(reason):
        print("Room đã ngắt:", reason)
        asyncio.create_task(ctx.shutdown())

# ==== Chạy ứng dụng chính ====
if __name__ == "__main__":
    agents.cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
