# Get your Sarvam AI API subscription key here: https://dashboard.sarvam.ai/admin
import base64, hashlib, html, io, json, mimetypes, os, re, tempfile, time, wave, zipfile
import gradio as gr, requests
from sarvamai import SarvamAI
LANGS = {
    "Hindi (हिन्दी)": ("hi-IN", "कृपया अपना {lbl} बताइए।", "धन्यवाद। आपके फॉर्म का विवरण: ", "क्या यह सारी जानकारी सही है?"),
    "Tamil (தமிழ்)": ("ta-IN", "தயவுசெய்து உங்கள் {lbl} கூறுங்கள்.", "நன்றி. உங்கள் படிவ விவரங்கள்: ", "இந்த விவரங்கள் அனைத்தும் சரியா?"),
    "Telugu (తెలుగు)": ("te-IN", "దయచేసి మీ {lbl} చెప్పండి.", "ధన్యవాదాలు. మీ ఫారమ్ వివరాలు: ", "ఈ వివరాలన్నీ సరైనవేనా?"),
    "Bengali (বাংলা)": ("bn-IN", "অনুগ্রহ করে আপনার {lbl} বলুন।", "ধন্যবাদ। আপনার ফর্মের বিবরণ: ", "এই সব তথ্য কি সঠিক?"),
    "Marathi (मराठी)": ("mr-IN", "कृपया तुमचे {lbl} सांगा.", "धन्यवाद. तुमच्या अर्जाची माहिती: ", "ही सर्व माहिती बरोबर आहे का?"),
    "Gujarati (ગુજરાતી)": ("gu-IN", "કૃપા કરીને તમારું {lbl} જણાવો.", "આભાર. તમારા ફોર્મની વિગતો: ", "શું આ બધી માહિતી સાચી છે?"),
    "Kannada (ಕನ್ನಡ)": ("kn-IN", "ದಯವಿಟ್ಟು ನಿಮ್ಮ {lbl} ಹೇಳಿ.", "ಧন্যವಾದಗಳು. ನಿಮ್ಮ ಅರ್ಜಿಯ ವಿವರಗಳು: ", "ಈ ಎಲ್ಲಾ ಮಾಹಿತಿ ಸರಿಯಾಗಿದೆಯೇ?"),
    "Punjabi (ਪੰਜਾਬੀ)": ("pa-IN", "ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ {lbl} ਦੱਸੋ।", "ਧੰਨਵਾਦ। ਤੁਹਾਡੇ ਫਾਰਮ ਦੇ ਵੇਰਵੇ: ", "ਕੀ ਇਹ ਸਾਰੀ ਜਾਣਕਾਰੀ ਸਹੀ ਹੈ?"),
    "Malayalam (മലയാളം)": ("ml-IN", "ദയവായി നിങ്ങളുടെ {lbl} പറയുക.", "നന്ദി. നിങ്ങളുടെ ഫോം വിവരങ്ങൾ: ", "ഈ വിവരങ്ങളെല്ലാം ശരിയാണോ?"),
    "Odia (ଓଡ଼ିଆ)": ("od-IN", "ଦୟାକରି ଆପଣଙ୍କର {lbl} କୁହନ୍ତୁ।", "ଧନ୍ୟବାଦ। ଆପଣଙ୍କ ଫର୍ମ ବିବରଣୀ: ", "ଏହି ସବୁ ତଥ୍ୟ ଠିକ୍ ଅଛି କି?"),
    "English (India)": ("en-IN", "Please tell me your {lbl}.", "Thank you. Filled form details: ", "Is everything correct?"),
}
SAMPLE_FIELDS = [
    ("full_name", "Full Name", "text", "Applicant name", {"hi-IN": "पूरा नाम", "ta-IN": "முழு பெயர்", "te-IN": "పూర్తి పేరు", "bn-IN": "পুরো নাম", "mr-IN": "पूर्ण नाव", "gu-IN": "પૂરું નામ", "kn-IN": "ಪೂರ್ಣ ಹೆಸರು", "pa-IN": "ਪੂਰਾ ਨਾਮ", "ml-IN": "പൂർണ്ണ നാമം", "od-IN": "ପୂରା ନାମ", "en-IN": "Full Name"}),
    ("guardian_name", "Father / Husband Name", "text", "Parent/spouse", {"hi-IN": "पिता या पति का नाम", "ta-IN": "தந்தை அல்லது கணவர் பெயர்", "te-IN": "తండ్రి లేదా భర్త పేరు", "bn-IN": "পিতা বা স্বামীর নাম", "mr-IN": "वडील किंवा पतीचे नाव", "gu-IN": "પિતા કે પતિનું નામ", "kn-IN": "ತಂದೆ ಅಥವಾ ಪತಿಯ ಹೆಸರು", "pa-IN": "ਪਿਤਾ ਜਾਂ ਪਤੀ ਦਾ ਨਾਮ", "ml-IN": "പിതാവിന്റെ പേര്", "od-IN": "ପିତା କିମ୍ବା ସ୍ୱାମୀଙ୍କ ନାମ", "en-IN": "Father or Husband Name"}),
    ("dob", "Date of Birth", "date", "DD/MM/YYYY", {"hi-IN": "जन्म तिथि", "ta-IN": "பிறந்த தேதி", "te-IN": "పుట్టిన తేదీ", "bn-IN": "জন্ম তারিখ", "mr-IN": "जन्मतारीख", "gu-IN": "જન્મ તારીખ", "kn-IN": "ಜನ್ಮ ದಿನಾಂಕ", "pa-IN": "ਜਨਮ ਮਿਤੀ", "ml-IN": "ജനനത്തീയതി", "od-IN": "ଜନ୍ମ ତାରିଖ", "en-IN": "Date of Birth"}),
    ("mobile", "Mobile Number", "phone", "10 digits", {"hi-IN": "मोबाइल नंबर", "ta-IN": "கைபேசி எண்", "te-IN": "మొబైల్ నంబర్", "bn-IN": "মোবাইল নম্বর", "mr-IN": "मोबाईल नंबर", "gu-IN": "મોબાઇલ નંબર", "kn-IN": "ಮೊಬೈಲ್ ಸಂಖ್ಯೆ", "pa-IN": "ਮੋਬਾਈਲ ਨੰਬਰ", "ml-IN": "മൊബൈൽ നമ്പർ", "od-IN": "ମୋବାଇଲ୍ ନମ୍ବର", "en-IN": "Mobile Number"}),
    ("village_town", "Village / Town", "text", "Locality", {"hi-IN": "गाँव या शहर", "ta-IN": "கிராமம் அல்லது நகரம்", "te-IN": "గ్రామం లేదా పట్టణం", "bn-IN": "গ্রাম বা শহর", "mr-IN": "गाव किंवा शहर", "gu-IN": "ગામ કે શહેર", "kn-IN": "ಗ್ರಾಮ ಅಥವಾ ಪಟ್ಟಣ", "pa-IN": "ਪਿੰਡ ਜਾਂ ਸ਼ਹਿਰ", "ml-IN": "ഗ്രാമം അല്ലെങ്കിൽ പട്ടണം", "od-IN": "ଗାଁ କିମ୍ବା ସହର", "en-IN": "Village or Town"}),
    ("district", "District", "text", "District name", {"hi-IN": "ज़िला", "ta-IN": "மாவட்டம்", "te-IN": "జిల్లా", "bn-IN": "জেলা", "mr-IN": "जिल्हा", "gu-IN": "જિલ્લો", "kn-IN": "ಜಿಲ್ಲೆ", "pa-IN": "ਜ਼ਿਲ੍ਹਾ", "ml-IN": "ജില്ല", "od-IN": "ଜିଲ୍ଲା", "en-IN": "District"}),
    ("pincode", "PIN Code", "number", "6-digit PIN", {"hi-IN": "पिन कोड", "ta-IN": "பின் கோடு", "te-IN": "పిన్ కోడ్", "bn-IN": "পিন কোড", "mr-IN": "पिन कोड", "gu-IN": "પિન કોડ", "kn-IN": "ಪಿನ್ ಕೋಡ್", "pa-IN": "ਪਿੰਨ ਕੋਡ", "ml-IN": "പിൻ കോഡ്", "od-IN": "ପିନ୍ କୋଡ୍", "en-IN": "PIN Code"}),
    ("aadhaar_last4", "Aadhaar Last 4 Digits", "number", "4 digits", {"hi-IN": "आधार के अंतिम 4 अंक", "ta-IN": "ஆதார் கடைசி 4 எண்கள்", "te-IN": "ఆధార్ చివరి 4 అంకెలు", "bn-IN": "আধারের শেষ ৪ সংখ্যা", "mr-IN": "आधारचे शेवटचे ४ अंक", "gu-IN": "આધારના છેલ્લા 4 અંક", "kn-IN": "ಆಧಾರ್ ಕೊನೆಯ 4 ಅಂಕಿಗಳು", "pa-IN": "ਆਧਾਰ ਦੇ ਆਖਰੀ 4 ਅੰਕ", "ml-IN": "ആധാർ അവസാന 4 അക്കങ്ങൾ", "od-IN": "ଆଧାରର ଶେଷ ୪ ଅଙ୍କ", "en-IN": "Aadhaar Last 4 Digits"}),
]
SYS_UNDERSTAND = (
    "You fill an Indian form from a spoken, code-mixed answer. Return ONLY JSON: "
    "{value, display_roman, confident, followup_question_local, is_correction, target_field_id}. "
    "Normalize spoken numbers to digits (phone = 10 digits, Aadhaar = 12, PIN = 6), dates to DD/MM/YYYY, "
    "names in native script AND Roman. If the user corrects an earlier field, set is_correction and target_field_id."
)
FORM_CACHE = {}
def get_client(ui_key=""):
    key = (ui_key or os.environ.get("SARVAM_API_KEY", "")).strip()
    if not key:
        raise ValueError("Missing SARVAM_API_KEY. Set env var SARVAM_API_KEY or paste it in the API Key box.")
    return SarvamAI(api_subscription_key=key)
def extract_json(raw_text, want_array=False):
    cleaned = re.sub(r"<think>.*?</think>", "", raw_text or "", flags=re.S).strip()
    m = re.search(r"\[.*\]" if want_array else r"\{.*\}", cleaned, flags=re.S)
    return json.loads(m.group(0) if m else cleaned)
def llm_json(client, sys_p, usr_p, want_array=False):
    msgs = [{"role": "system", "content": sys_p}, {"role": "user", "content": usr_p}]
    try:
        r = client.chat.completions(model="sarvam-105b", messages=msgs, reasoning_effort=None, temperature=0.1, max_tokens=1024)
    except TypeError:
        r = client.chat.completions(model="sarvam-105b", messages=msgs, temperature=0.1)
    return extract_json(r.choices[0].message.content, want_array=want_array)
def tts_speak(client, text, lang_code, speaker="priya"):
    if not text:
        return None
    chunks = [text[i : i + 2400] for i in range(0, len(text), 2400)]
    wav_blobs = []
    for chunk in chunks:
        try:
            r = client.text_to_speech.convert(text=chunk, language_code=lang_code, model="bulbul:v3", speaker=speaker)
        except TypeError:
            r = client.text_to_speech.convert(text=chunk, target_language_code=lang_code, model="bulbul:v3", speaker=speaker)
        wav_blobs.append(base64.b64decode("".join(r.audios)))
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    if len(wav_blobs) == 1:
        open(path, "wb").write(wav_blobs[0])
    else:
        with wave.open(path, "wb") as out_w:
            for idx_b, b in enumerate(wav_blobs):
                with wave.open(io.BytesIO(b), "rb") as in_w:
                    if idx_b == 0:
                        out_w.setparams(in_w.getparams())
                    out_w.writeframes(in_w.readframes(in_w.getnframes()))
    return path
def translate_label(client, text, lang_code):
    if lang_code == "en-IN":
        return text
    try:
        return client.text.translate(input=text, source_language_code="auto", target_language_code=lang_code, speaker_gender="Male").translated_text or text
    except Exception:
        return text
def build_view(state):
    fields, vals, idx = state["fields"], state["values"], state["idx"]
    rows = []
    for i, f in enumerate(fields):
        v = vals.get(f["id"], {})
        val, rom = v.get("value", ""), v.get("display_roman", "")
        disp = f"{val} ({rom})" if rom and rom != val else val
        st = "✅ Filled" if v.get("status") == "filled" else ("⏭️ Skipped" if v.get("status") == "skipped" else ("🎙️ Current" if i == idx else "⏳ Pending"))
        rows.append([f["label_original"], f["label_local"], disp, st])
    done = sum(1 for f in fields if vals.get(f["id"], {}).get("status") in ("filled", "skipped"))
    prog = f"**Progress:** {done} / {len(fields)} fields | **Language:** `{state['lang']}`"
    if not fields:
        return rows, prog, None, ""
    out_data = {f["id"]: {"label": f["label_original"], "label_local": f["label_local"], **vals.get(f["id"], {})} for f in fields}
    fd, jpath = tempfile.mkstemp(suffix="_bolobharo.json")
    with os.fdopen(fd, "w", encoding="utf-8") as jf:
        json.dump(out_data, jf, ensure_ascii=False, indent=2)
    trs = "".join(f"<tr><td><b>{html.escape(r[0])}</b><br><small>{html.escape(r[1])}</small></td><td>{html.escape(r[2])}</td><td>{html.escape(r[3])}</td></tr>" for r in rows)
    hview = f"<div style='padding:14px;border:1px solid #cbd5e1;border-radius:8px;background:#fff;color:#0f172a'><h3>BoloBharo Printable Form</h3><table style='width:100%;border-collapse:collapse' border='1' cellpadding='8'><tr style='background:#f1f5f9'><th>Field</th><th>Value</th><th>Status</th></tr>{trs}</table></div>"
    return rows, prog, jpath, hview
def ask_current(state, ui_key):
    fields, idx, lang = state["fields"], state["idx"], state["lang"]
    _, q_tpl, fin_intro, fin_ask = next(v for v in LANGS.values() if v[0] == lang)
    if not fields:
        return state, "Click **Use Sample Form** or upload a form image/PDF to begin.", None, *build_view(state)
    if idx >= len(fields):
        parts = [f"{f['label_local']}: {state['values'].get(f['id'], {}).get('value', '-')}" for f in fields]
        text = f"{fin_intro}{'; '.join(parts)}. {fin_ask}"
        try:
            audio = tts_speak(get_client(ui_key), text, lang)
        except Exception as e:
            audio, text = None, f"{text} (TTS error: {e})"
        return state, f"🎉 **Form Complete!**\n\n🔊 {text}", audio, *build_view(state)
    cur = fields[idx]
    q_text = q_tpl.format(lbl=cur["label_local"])
    try:
        audio = tts_speak(get_client(ui_key), q_text, lang)
    except Exception as e:
        audio, q_text = None, f"{q_text}\n*(TTS note: {e})*"
    return state, f"### 🗣️ Field {idx+1}/{len(fields)}: **{cur['label_original']}** (`{cur['label_local']}`)\n🔊 **Question:** {q_text}", audio, *build_view(state)
def load_sample(lang_label, ui_key):
    lang = LANGS[lang_label][0]
    fields = [{"id": i, "label_original": lo, "label_local": lc.get(lang, lo), "type": t, "hint": h} for i, lo, t, h, lc in SAMPLE_FIELDS]
    return ask_current({"fields": fields, "idx": 0, "values": {}, "lang": lang, "retries": {}}, ui_key)
def load_uploaded_form(file_path, lang_label, ui_key):
    if not file_path:
        return load_sample(lang_label, ui_key)
    lang = LANGS[lang_label][0]
    try:
        client = get_client(ui_key)
        fhash = hashlib.sha256(open(file_path, "rb").read()).hexdigest()[:16]
        if fhash not in FORM_CACHE:
            mime = mimetypes.guess_type(file_path)[0] or "application/pdf"
            with open(file_path, "rb") as f:
                job = client.doc_ai.digitise(file=[(os.path.basename(file_path), f, mime)], language=lang, output_format="md")
            for _ in range(30):
                st = getattr(client.doc_ai.get_status(job_id=job.job_id), "status", "").lower()
                if st in {"completed", "partially_completed", "failed", "rejected"}:
                    break
                time.sleep(3)
            if st in {"failed", "rejected"}:
                raise RuntimeError(f"Vision job status: {st}")
            dl = client.doc_ai.get_download_url(job_id=job.job_id)
            zf = zipfile.ZipFile(io.BytesIO(requests.get(dl.url, timeout=30).content))
            md = "\n".join(zf.read(n).decode("utf-8", errors="ignore") for n in zf.namelist() if n.endswith(".md"))
            sys_p = "Extract up to 12 fillable fields in order from this form markdown (skip stamps, instructions, signatures). Return ONLY JSON array: [{\"id\":\"...\",\"label_original\":\"...\",\"type\":\"text|date|phone|number|choice\",\"hint\":\"...\"}]."
            FORM_CACHE[fhash] = llm_json(client, sys_p, md[:12000], want_array=True)[:12]
        fields = [{"id": x["id"], "label_original": x["label_original"], "label_local": translate_label(client, x["label_original"], lang), "type": x.get("type", "text"), "hint": x.get("hint", "")} for x in FORM_CACHE[fhash]]
        return ask_current({"fields": fields, "idx": 0, "values": {}, "lang": lang, "retries": {}}, ui_key)
    except Exception as e:
        st = {"fields": [], "idx": 0, "values": {}, "lang": lang, "retries": {}}
        return st, f"⚠️ **Reading Error:** {e} — Click **Use Sample Form** for instant fallback.", None, *build_view(st)
def handle_voice(audio_path, state, ui_key):
    if not state.get("fields") or not audio_path:
        return state, "⚠️ Load a form and record/upload an audio answer first.", None, *build_view(state)
    fields, idx, lang = state["fields"], state["idx"], state["lang"]
    cur = fields[min(idx, len(fields) - 1)]
    keyterms = list({f["label_original"][:64] for f in fields} | {f["label_local"][:64] for f in fields})[:50]
    try:
        client = get_client(ui_key)
        with open(audio_path, "rb") as af:
            try:
                stt = client.speech_to_text.transcribe(file=af, model="saaras:v4", mode="codemix", keyterms=keyterms)
            except TypeError:
                af.seek(0)
                stt = client.speech_to_text.transcribe(file=af, model="saaras:v4", mode="codemix")
        tx = (stt.transcript or "").strip()
        if not tx:
            raise ValueError("Could not hear speech clearly. Please try again.")
        payload = json.dumps({"current_field": cur, "fields": [{"id": f["id"], "label": f["label_original"]} for f in fields], "values": state["values"], "lang": lang, "transcript": tx}, ensure_ascii=False)
        parsed = llm_json(client, SYS_UNDERSTAND, payload)
        if parsed.get("is_correction") and parsed.get("target_field_id") in {f["id"] for f in fields}:
            tid = parsed["target_field_id"]
            state["values"][tid] = {"value": str(parsed.get("value", tx)), "display_roman": str(parsed.get("display_roman", "")), "status": "filled"}
            return ask_current(state, ui_key)
        retries = state["retries"].get(cur["id"], 0)
        if not parsed.get("confident", True) and retries < 1 and parsed.get("followup_question_local"):
            state["retries"][cur["id"]] = retries + 1
            fq = parsed["followup_question_local"]
            return state, f"🤔 **Heard:** `{tx}`\n🔊 **Clarification (1 retry):** {fq}", tts_speak(client, fq, lang), *build_view(state)
        val = str(parsed.get("value") or tx)
        state["values"][cur["id"]] = {"value": val, "display_roman": str(parsed.get("display_roman") or val), "status": "filled"}
        state["idx"] = min(idx + 1, len(fields))
        return ask_current(state, ui_key)
    except Exception as e:
        return state, f"⚠️ **API Error:** {e} (State preserved — retry anytime)", None, *build_view(state)
def nav_step(act, state, ui_key):
    if act == "skip" and state.get("fields") and state["idx"] < len(state["fields"]):
        state["values"].setdefault(state["fields"][state["idx"]]["id"], {"value": "—", "display_roman": "Skipped", "status": "skipped"})
        state["idx"] += 1
    elif act == "back":
        state["idx"] = max(0, state["idx"] - 1)
    elif act == "restart":
        state["idx"], state["values"], state["retries"] = 0, {}, {}
    return ask_current(state, ui_key)
def change_lang(lang_label, state, ui_key):
    lang = LANGS[lang_label][0]
    state["lang"] = lang
    smap = {i: lc.get(lang, lo) for i, lo, _, _, lc in SAMPLE_FIELDS}
    for f in state.get("fields", []):
        f["label_local"] = smap.get(f["id"]) or translate_label(get_client(ui_key), f["label_original"], lang)
    return ask_current(state, ui_key)
with gr.Blocks(title="BoloBharo: bolo, form bharo", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎙️ BoloBharo: *bolo, form bharo*\n**Voice-first Indian form-filling agent on Sarvam AI** (`Vision` • `Translate` • `Bulbul` • `Saaras v4` • `Sarvam-105B`)")
    state = gr.State({"fields": [], "idx": 0, "values": {}, "lang": "hi-IN", "retries": {}})
    with gr.Row():
        lang_dd = gr.Dropdown(list(LANGS.keys()), value="Hindi (हिन्दी)", label="🌐 Language (11 Indic + English)", scale=2)
        api_key_box = gr.Textbox(label="🔑 SARVAM_API_KEY (optional override; uses env var by default)", type="password", scale=2)
    with gr.Row():
        sample_btn = gr.Button("📋 Use Sample Form (8 Fields — 0 Vision Calls)", variant="primary")
        form_file = gr.File(label="📄 Upload Form Image/PDF (Sarvam Vision)", file_types=[".pdf", ".png", ".jpg", ".jpeg"], type="filepath")
    progress_md = gr.Markdown("**Progress:** 0 / 0 fields")
    question_md = gr.Markdown("### 👋 Click **Use Sample Form** or upload a form to begin.")
    with gr.Row():
        tts_audio = gr.Audio(label="🔊 Spoken Question / Read-Back (Bulbul)", autoplay=True, interactive=False)
        mic_audio = gr.Audio(sources=["microphone", "upload"], type="filepath", label="🎤 Record Answer (up to 25s) or Upload WAV")
    with gr.Row():
        sub_btn = gr.Button("✅ Submit Voice Answer", variant="primary", size="lg")
        skip_btn = gr.Button("⏭️ Skip")
        back_btn = gr.Button("⬅️ Go Back")
        rst_btn = gr.Button("🔄 Restart")
    live_table = gr.Dataframe(headers=["Field (Original)", "Field (Local)", "Value", "Status"], interactive=False, label="📊 Live Form")
    with gr.Row():
        json_dl = gr.File(label="📥 Download JSON")
        printable_html = gr.HTML(label="🖨️ Printable View")
    outs = [state, question_md, tts_audio, live_table, progress_md, json_dl, printable_html]
    sample_btn.click(load_sample, [lang_dd, api_key_box], outs)
    form_file.change(load_uploaded_form, [form_file, lang_dd, api_key_box], outs, show_progress="full")
    mic_audio.stop_recording(handle_voice, [mic_audio, state, api_key_box], outs)
    sub_btn.click(handle_voice, [mic_audio, state, api_key_box], outs)
    skip_btn.click(lambda s, k: nav_step("skip", s, k), [state, api_key_box], outs)
    back_btn.click(lambda s, k: nav_step("back", s, k), [state, api_key_box], outs)
    rst_btn.click(lambda s, k: nav_step("restart", s, k), [state, api_key_box], outs)
    lang_dd.change(change_lang, [lang_dd, state, api_key_box], outs)
if __name__ == "__main__":
    demo.launch()