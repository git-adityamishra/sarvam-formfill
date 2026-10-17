"""Generate mic-free demo WAV answers in 2 languages (Hindi + Tamil) using Sarvam Bulbul v3 TTS.
Get your Sarvam AI API subscription key here: https://dashboard.sarvam.ai/admin
Run:
  export SARVAM_API_KEY="your_key_here"
  python make_samples.py
"""
import base64, os, pathlib
from sarvamai import SarvamAI

SAMPLE_ANSWERS = {
    "hi-IN": {
        "speaker": "shubh",
        "utterances": [
            ("01_full_name.wav", "मेरा नाम रमेश कुमार शर्मा है"),
            ("02_guardian_name.wav", "मेरे पिताजी का नाम सुरेश चंद्र शर्मा है"),
            ("03_dob.wav", "मेरी जन्म तिथि पंद्रह अगस्त उन्नीस सौ अट्ठासी है, यानी 15 08 1988"),
            ("04_mobile.wav", "मेरा मोबाइल नंबर है 9876543210"),
            ("05_village_town.wav", "मैं सांगानेर गाँव में रहता हूँ"),
            ("06_district.wav", "मेरा ज़िला जयपुर है"),
            ("07_pincode.wav", "हमारा पिन कोड 302029 है"),
            ("08_aadhaar_last4.wav", "मेरे आधार के आखिरी चार अंक 4821 हैं"),
            ("09_correction_name.wav", "नहीं, मेरा नाम रमेश नहीं, मुरुगेसन है"),
        ],
    },
    "ta-IN": {
        "speaker": "ritu",
        "utterances": [
            ("01_full_name.wav", "என் பெயர் முருகேசன் சுப்பிரமணியன்"),
            ("02_guardian_name.wav", "என் தந்தையின் பெயர் சுப்பிரமணியன்"),
            ("03_dob.wav", "என் பிறந்த தேதி பத்து மே ஆயிரத்து தொள்ளாயிரத்து தொண்ணூறு, 10 05 1990"),
            ("04_mobile.wav", "என் கைபேசி எண் 9443122334"),
            ("05_village_town.wav", "எங்கள் ஊர் மேலூர்"),
            ("06_district.wav", "மதுரை மாவட்டம்"),
            ("07_pincode.wav", "பின் கோடு 625106"),
            ("08_aadhaar_last4.wav", "ஆதார் கடைசி நான்கு எண்கள் 7392"),
        ],
    },
}

def main():
    key = os.environ.get("SARVAM_API_KEY", "").strip()
    if not key:
        raise SystemExit("ERROR: Set SARVAM_API_KEY environment variable first.\nExample: export SARVAM_API_KEY='your_key'")
    client = SarvamAI(api_subscription_key=key)
    out_root = pathlib.Path("samples")
    for lang_code, cfg in SAMPLE_ANSWERS.items():
        lang_dir = out_root / lang_code
        lang_dir.mkdir(parents=True, exist_ok=True)
        speaker = cfg["speaker"]
        for fname, text in cfg["utterances"]:
            try:
                res = client.text_to_speech.convert(
                    text=text,
                    language_code=lang_code,
                    model="bulbul:v3",
                    speaker=speaker,
                )
            except TypeError:
                res = client.text_to_speech.convert(
                    text=text,
                    target_language_code=lang_code,
                    model="bulbul:v3",
                    speaker=speaker,
                )
            wav_bytes = base64.b64decode("".join(res.audios))
            out_path = lang_dir / fname
            out_path.write_bytes(wav_bytes)
            print(f"[OK] Wrote {out_path} ({len(wav_bytes)} bytes) — speaker={speaker}")

if __name__ == "__main__":
    main()