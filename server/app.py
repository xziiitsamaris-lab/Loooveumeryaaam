from flask import Flask, request, jsonify, render_template_string
from threading import Lock
from datetime import datetime, timezone
import os
import secrets
import re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# Demo storage: messages are kept in memory and disappear when the server restarts.
rooms = {}
lock = Lock()
MAX_MESSAGES = 200
MAX_TEXT = 500

QUESTIONS = {
    "رومانسي 🌹": [
        "شنو أول حاجة عجبتك فيا؟",
        "شنو أحلى ذكرى بيناتنا؟",
        "شنو كلمة تحب تسمعها مني؟",
        "كيف تتخيل خرجة مثالية لينا؟",
        "شنو حاجة صغيرة نديرها وتفرحك؟",
        "لو كانت قصتنا فيلم، واش يكون عنوانه؟",
        "شنو أكثر صفة تحبها في شخصيتي؟",
        "واش هي أغنية تفكرك بيا؟",
        "واش حاجة حاب نتعلموها مع بعض؟",
        "كيف نقدر نبيّنلك اهتمامي بطريقة تعجبك؟",
    ],
    "صراحة 🔥": [
        "واش أول انطباع خديتو عليا؟",
        "كاين سؤال حاب تسقسيهولي من زمان؟",
        "واش أكثر حاجة تقوّي الثقة بيناتنا؟",
        "كي تتقلق، تحب نهدر معاك ولا نعطيك وقت؟",
        "واش حاجة نقدر نحسّنها في طريقة تعاملي معاك؟",
        "عمرك غرت وما حبيتش تبيّن؟ إذا حاب تحكي، علاش؟",
        "واش أكثر موقف خلاك تضحك معايا؟",
        "واش الحاجة اللي تخليك تحس بلي راني نسمعلك مليح؟",
        "واش حدودك اللي تحب الطرف الآخر يحترمها؟",
        "قيّم صراحتنا من 1 حتى 10، وعلاش؟",
    ],
    "تحدّي 😈": [
        "ابعث 3 إيموجيات يعبّرو على إحساسك الآن.",
        "قول حاجة مليحة في الطرف الآخر ما قلتهاش من قبل.",
        "اختار أغنية تلخّص مودك اليوم.",
        "اكتب جملة من 5 كلمات تصف علاقتكم.",
        "كل واحد يذكر حاجة يتمنى يجربها مع الآخر في المستقبل.",
        "احكي موقف محرج مضحك إذا كنت مرتاح تحكيه.",
        "خلي الطرف الآخر يختار سؤال تسقسيهولو.",
        "اكتب رسالة لطيفة في سطر واحد.",
        "قول صفة في روحك حاب تطورها.",
        "اختار: سؤال صراحة ولا تحدّي خفيف؟",
    ],
}

PAGE = r"""
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>مصارحة 💕</title>
<style>
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:linear-gradient(145deg,#180f2c,#35163c 55%,#17142e);color:#fff;min-height:100vh}
.wrap{max-width:760px;margin:auto;padding:18px}
header{text-align:center;padding:12px 0 18px}
h1{margin:0;font-size:2rem} .sub{color:#d8c9e8}
.panel{background:#ffffff10;border:1px solid #ffffff20;border-radius:18px;padding:16px;margin:12px 0;backdrop-filter:blur(8px)}
.row{display:flex;gap:8px;flex-wrap:wrap}
input,select,button{font:inherit;border:0;border-radius:12px;padding:12px}
input,select{background:#211a35;color:white;min-width:0;flex:1}
button{background:#e879f9;color:#210d2b;font-weight:700;cursor:pointer}
button.secondary{background:#35264a;color:#fff;border:1px solid #ffffff20}
button:disabled{opacity:.5}
#messages{height:42vh;min-height:260px;overflow-y:auto;display:flex;flex-direction:column;gap:9px}
.msg{max-width:90%;padding:10px 13px;border-radius:15px;background:#ffffff12;align-self:flex-start;overflow-wrap:anywhere}
.msg.mine{align-self:flex-end;background:#713f8e}
.who{font-size:.78rem;color:#f2c9ff;margin-bottom:3px}
.question{font-size:1.1rem;line-height:1.7;text-align:center}
.small{font-size:.85rem;color:#d8c9e8}
#status{font-size:.85rem;color:#c9f7d4}
.hidden{display:none!important}
footer{text-align:center;color:#c9b8d8;font-size:.8rem;padding:12px}
</style>
</head>
<body>
<div class="wrap">
<header><h1>مصارحة 💕</h1><div class="sub">دردشة وأسئلة بين زوج أشخاص</div></header>

<section class="panel" id="joinPanel">
  <label for="name">اسمك</label>
  <div class="row" style="margin:6px 0 12px"><input id="name" maxlength="24" placeholder="مثلاً: أنا"></div>
  <label for="room">كود الغرفة</label>
  <div class="row" style="margin:6px 0 12px"><input id="room" maxlength="24" placeholder="مثلاً: LOVE2026"><button id="joinBtn">دخول</button></div>
  <div class="small">اتفقوا على نفس كود الغرفة. ما تستعملوش معلومات شخصية ككود.</div>
</section>

<section class="panel hidden" id="gamePanel">
  <div class="row" style="justify-content:space-between;align-items:center">
    <b id="roomTitle">الغرفة</b><span id="status">جاري الاتصال…</span>
  </div>
  <div class="row" style="margin-top:12px">
    <select id="level">
      <option>رومانسي 🌹</option><option>صراحة 🔥</option><option>تحدّي 😈</option>
    </select>
    <button id="questionBtn">سؤال جديد 🎲</button>
  </div>
  <div class="panel question" id="questionBox">اختارو مستوى واضغطو «سؤال جديد».</div>
  <div id="messages" class="panel" aria-live="polite"></div>
  <form id="chatForm" class="row">
    <input id="message" maxlength="500" autocomplete="off" placeholder="اكتب رسالتك…" required>
    <button type="submit">إرسال</button>
  </form>
  <div class="small">احترموا حدود بعضاكم؛ أي واحد يقدر يفوّت سؤال ما يرتاحلوش.</div>
</section>
<footer>نسخة تجريبية: الرسائل مؤقتة وقد تختفي عند إعادة تشغيل السيرفر. ما تبعثوش معلومات خاصة.</footer>
</div>
<script>
let myName="", myRoom="", lastId=0, polling=false;
const $ = id => document.getElementById(id);
function safeText(el, value){ el.textContent = value; }
function addMessage(m){
  if(m.id <= lastId) return;
  lastId = m.id;
  const box=$("messages"), div=document.createElement("div");
  div.className="msg"+(m.name===myName?" mine":"");
  const who=document.createElement("div"); who.className="who";
  who.textContent=m.name+" · "+m.time;
  const body=document.createElement("div"); body.textContent=m.text;
  div.append(who,body); box.append(div); box.scrollTop=box.scrollHeight;
}
async function api(path, data){
  const res=await fetch(path,{method:data?"POST":"GET",headers:data?{"Content-Type":"application/json"}:{},body:data?JSON.stringify(data):undefined});
  const result=await res.json();
  if(!res.ok) throw new Error(result.error||"صار خطأ");
  return result;
}
async function poll(){
  if(polling) return;
  polling=true;
  try{
    const data=await api(`/api/messages?room=${encodeURIComponent(myRoom)}&after=${lastId}`);
    data.messages.forEach(addMessage);
    $("status").textContent="متصل بالسيرفر";
  }catch(e){ $("status").textContent="الاتصال انقطع؛ نحاول نعاود…"; }
  finally{polling=false;setTimeout(poll,1800);}
}
$("joinBtn").addEventListener("click", async()=>{
  myName=$("name").value.trim().slice(0,24)||"مشارك";
  myRoom=$("room").value.trim().toUpperCase().replace(/[^A-Z0-9_-]/g,"").slice(0,24);
  if(myRoom.length<4){alert("اكتب كود غرفة من 4 أحرف على الأقل.");return;}
  $("joinBtn").disabled=true;
  try{
    await api("/api/join",{name:myName,room:myRoom});
    $("roomTitle").textContent="غرفة: "+myRoom;
    $("joinPanel").classList.add("hidden"); $("gamePanel").classList.remove("hidden");
    poll();
  }catch(e){alert(e.message);}
  finally{$("joinBtn").disabled=false;}
});
$("chatForm").addEventListener("submit",async e=>{
  e.preventDefault(); const text=$("message").value.trim(); if(!text)return;
  $("message").value="";
  try{await api("/api/send",{name:myName,room:myRoom,text,type:"chat"});}
  catch(err){alert(err.message);}
});
$("questionBtn").addEventListener("click",async()=>{
  try{
    const result=await api("/api/question",{name:myName,room:myRoom,level:$("level").value});
    safeText($("questionBox"),result.question);
  }catch(e){alert(e.message);}
});
</script>
</body>
</html>
"""

def clean(value, limit=500):
    return str(value or "").strip()[:limit]

def room_messages(room):
    return rooms.setdefault(room, [])

def append_message(room, name, text, kind="chat"):
    with lock:
        messages = room_messages(room)
        new_id = messages[-1]["id"] + 1 if messages else 1
        msg = {
            "id": new_id,
            "name": clean(name, 24) or "مشارك",
            "text": clean(text, MAX_TEXT),
            "time": datetime.now().strftime("%H:%M"),
            "type": kind,
        }
        messages.append(msg)
        del messages[:-MAX_MESSAGES]
        return msg

@app.get("/")
def home():
    return render_template_string(PAGE)

@app.post("/api/join")
def join():
    data = request.get_json(silent=True) or {}
    room = clean(data.get("room"), 24).upper()
    name = clean(data.get("name"), 24) or "مشارك"
    if not re.fullmatch(r"[A-Z0-9_-]{4,24}", room):
        return jsonify(error="كود الغرفة لازم يكون 4 إلى 24 حرف/رقم."), 400
    append_message(room, "النظام", f"{name} دخل/دخلت للغرفة 💕", "system")
    return jsonify(ok=True)

@app.get("/api/messages")
def messages():
    room = clean(request.args.get("room"), 24).upper()
    try:
        after = max(0, int(request.args.get("after", "0")))
    except ValueError:
        after = 0
    if not re.fullmatch(r"[A-Z0-9_-]{4,24}", room):
        return jsonify(error="كود غرفة غير صالح."), 400
    with lock:
        result = [m for m in room_messages(room) if m["id"] > after]
    return jsonify(messages=result)

@app.post("/api/send")
def send():
    data = request.get_json(silent=True) or {}
    room = clean(data.get("room"), 24).upper()
    name = clean(data.get("name"), 24) or "مشارك"
    message = clean(data.get("text"), MAX_TEXT)
    if not re.fullmatch(r"[A-Z0-9_-]{4,24}", room):
        return jsonify(error="كود غرفة غير صالح."), 400
    if not message:
        return jsonify(error="الرسالة فارغة."), 400
    append_message(room, name, message)
    return jsonify(ok=True)

@app.post("/api/question")
def question():
    data = request.get_json(silent=True) or {}
    room = clean(data.get("room"), 24).upper()
    name = clean(data.get("name"), 24) or "مشارك"
    level = clean(data.get("level"), 40)
    if not re.fullmatch(r"[A-Z0-9_-]{4,24}", room):
        return jsonify(error="كود غرفة غير صالح."), 400
    if level not in QUESTIONS:
        return jsonify(error="اختار مستوى صحيح."), 400
    q = secrets.choice(QUESTIONS[level])
    append_message(room, name, f"🎲 سؤال ({level}): {q}", "question")
    return jsonify(ok=True, question=q)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
