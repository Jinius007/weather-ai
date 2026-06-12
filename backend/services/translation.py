from __future__ import annotations

from typing import Any

TERM_LABELS = {
    "hi": {"short_term": "अल्पकालिक", "medium_term": "मध्यम अवधि", "long_term": "दीर्घकालिक"},
    "te": {"short_term": "అల్పకాలిక", "medium_term": "మధ్యకాలిక", "long_term": "దీర్ఘకాలిక"},
    "ta": {"short_term": "குறுகிய கால", "medium_term": "நடுத்தர கால", "long_term": "நீண்ட கால"},
    "kn": {"short_term": "ಅಲ್ಪಕಾಲಿಕ", "medium_term": "ಮಧ್ಯಮ ಅವಧಿ", "long_term": "ದೀರ್ಘಕಾಲಿಕ"},
    "ml": {"short_term": "ഹ്രസ്വകാല", "medium_term": "ഇടത്തരം", "long_term": "ദീർഘകാല"},
    "mr": {"short_term": "अल्पकालीन", "medium_term": "मध्यम कालावधी", "long_term": "दीर्घकालीन"},
    "gu": {"short_term": "અલ્પકાલીન", "medium_term": "મધ્યમ અવધિ", "long_term": "લાંબા ગાળાનું"},
    "bn": {"short_term": "স্বল্পমেয়াদি", "medium_term": "মধ্যমেয়াদি", "long_term": "দীর্ঘমেয়াদি"},
    "pa": {"short_term": "ਛੋਟੀ ਮਿਆਦ", "medium_term": "ਦਰਮਿਆਨੀ ਮਿਆਦ", "long_term": "ਲੰਬੀ ਮਿਆਦ"},
    "or": {"short_term": "ଅଳ୍ପକାଳୀନ", "medium_term": "ମଧ୍ୟମ", "long_term": "ଦୀର୍ଘକାଳୀନ"},
    "as": {"short_term": "স্বল্পম্যাদ", "medium_term": "মধ্যম্যাদ", "long_term": "দীৰ্ঘম্যাদ"},
}

ADVISORY_TEMPLATES = {
    "hi": {
        "header": "{district}, {state} — {term} मौसम सलाह",
        "forecast": "मौसम: {weather}. तापमान {tmin}°C से {tmax}°C. {days} दिन में {rain} mm बारिश संभव।",
        "sowing": {"good": "बुवाई: मिट्टी में नमी अच्छी है। बुवाई के लिए अनुकूल समय।", "avoid": "बुवाई: भारी बारिश की संभावना। खेत सूखने तक बुवाई टालें।", "caution": "बुवाई: गर्म और शुष्क मौसम। सिंचाई की व्यवस्था के साथ ही बुवें।", "neutral": "बुवाई: मौसम मिश्रित है। सावधानी से फैसला लें।"},
        "fertilizer": {"good": "खाद: स्थिर मौसम। नम मिट्टी में खाद डालना उपयुक्त।", "avoid": "खाद: भारी बारिश खाद बहा सकती है। बारिश रुकने के बाद डालें।", "caution": "खाद: अत्यधिक गर्मी। दोपहर में यूरिया न डालें।", "neutral": "खाद: शाम को खाद डालें और हल्की सिंचाई करें।"},
        "harvest": {"good": "कटाई: सूखा मौसम। कटाई और सुखाने के लिए अच्छा समय।", "avoid": "कटाई: बारिश से फसल गीली हो सकती है। कटाई टालें।", "caution": "कटाई: तेज हवा से फसल गिर सकती है। पहले खड़ी फसल काटें।", "neutral": "कटाई: रोज मौसम देखकर कटाई की योजना बनाएं।"},
        "irrigation": {"good": "सिंचाई: बारिश पर्याप्त हो सकती है। पानी बचाएं।", "urgent": "सिंचाई: गर्म और शुष्क मौसम। सुबह या शाम सिंचाई करें।", "caution": "सिंचाई: कम बारिश। मिट्टी की नमी बनाए रखें।", "neutral": "सिंचाई: मिट्टी की नमी देखकर सिंचाई करें।"},
    },
    "te": {
        "header": "{district}, {state} — {term} వాతావరణ సలహా",
        "forecast": "వాతావరణం: {weather}. ఉష్ణోగ్రత {tmin}°C–{tmax}°C. {days} రోజుల్లో {rain} mm వర్షం.",
        "sowing": {"good": "విత్తనం: నేల తేమ బాగుంది. విత్తడానికి అనుకూల సమయం.", "avoid": "విత్తనం: భారీ వర్షం ఉంది. నేల ఎండిన తర్వాత విత్తండి.", "caution": "విత్తనం: వేడి, పొడిగా ఉంది. నీటితో మాత్రమే విత్తండి.", "neutral": "విత్తనం: జాగ్రత్తగా నిర్ణయం తీసుకోండి."},
        "fertilizer": {"good": "ఎరువులు: స్థిరమైన వాతావరణం. ఎరువులు వేయడానికి అనుకూలం.", "avoid": "ఎరువులు: భారీ వర్షం ఎరువులు కడిపేస్తుంది.", "caution": "ఎరువులు: అధిక వేడి. మధ్యాహ్నం యూరియా వేయవద్దు.", "neutral": "ఎరువులు: సాయంత్రం వేసి తేలికగా నీರು పోయండి."},
        "harvest": {"good": "పంట: పొడి వాతావరణం. కోతకు అనుకూలం.", "avoid": "పంట: వర్షం వల్ల తిరigi పంట నష్టం.", "caution": "పంట: gale winds lodging risk.", "neutral": "పంట: రోజువారీ వాతావరణం చూసి నిర్ణయించండి."},
        "irrigation": {"good": "నీటిపారుదల: వర్షం సరిపోతుంది. నీరు ఆదా చేయండి.", "urgent": "నీటిపారుదల: వేడి, పొడి. ఉదయం/సాయంత్రం నీరు.", "caution": "నీటిపారుదల: తక్కువ వర్షం. తేమ నిల్వ.", "neutral": "నీటిపారుదల: నేల తేమ చూసి నీరు."},
    },
    "ta": {
        "header": "{district}, {state} — {term} வானிலை ஆலோசனை",
        "forecast": "வானிலை: {weather}. வெப்பம் {tmin}°C–{tmax}°C. {days} நாட்களில் {rain} mm மழை.",
        "sowing": {"good": "விதைப்பு: மண் ஈரம் நல்லது. விதைக்க ஏற்ற நேரம்.", "avoid": "விதைப்பு: கனமழை. வயல் உலர்ந்த பின் விதைக்கவும்.", "caution": "விதைப்பு: வெப்பம், வறட்சி. பாசனத்துடன் மட்டும்.", "neutral": "விதைப்பு: எச்சரிக்கையுடன் முடிவு எடுங்கள்."},
        "fertilizer": {"good": "உரம்: நிலையான வானிலை. உரமிட ஏற்றது.", "avoid": "உரம்: கனமழை உரத்தை கழுவும்.", "caution": "உரம்: அதிக வெப்பம். மதியம் யூரியா வேண்டாம்.", "neutral": "உரம்: மாலை உரமிட்டு லேசாக பாசனம்."},
        "harvest": {"good": "அறுவடை: வறண்ட வானிலை. அறுவடைக்கு ஏற்றது.", "avoid": "அறுவடை: மழையால் crop damage.", "caution": "அறுவடai: க fuerte காற்று.", "neutral": "அறுவடை: தினசரி வானிலை பார்த்து திட்டமிடுங்கள்."},
        "irrigation": {"good": "பாசனம்: மழை போதுமானது. நீர் சேமிக்கவும்.", "urgent": "பாசனம்: வெப்பம், வறட்சி. காலை/மாலை பாசனம்.", "caution": "பாசனம்: குறைந்த மழை. ஈரம் பராமரிக்கவும்.", "neutral": "பாசனம்: மண் ஈரம் பார்த்து பாசனம்."},
    },
    "mr": {
        "header": "{district}, {state} — {term} हवामान सल्ला",
        "forecast": "हवामान: {weather}. तापमान {tmin}°C–{tmax}°C. {days} दिवसांत {rain} mm पाऊस.",
        "sowing": {"good": "पेरणी: मातीची ओलसरता चांगली. पेरणीस अनुकूल.", "avoid": "पेरणी: जोरदार पाऊस. शेत सुटेपर्यंत थांबा.", "caution": "पeriणi: उष्ण व कोरडे. सिंचन असल्यासच.", "neutral": "पेरणी: काळजीपूर्वक निर्णय घ्या."},
        "fertilizer": {"good": "खत: स्थिर हवामान. खत घालण्यास योग्य.", "avoid": "खत: जोरदार पाऊस खत वाहून नेईल.", "caution": "खत: अत्यंत उष्णता. दुपारी युरिया नको.", "neutral": "खत: संध्याकाळी खत व हलके सिंचन."},
        "harvest": {"good": "कापणी: कोरडे हवामान. कापणीस अनुकूल.", "avoid": "कापणी: पाऊस पikala होऊ शकते.", "caution": "कापणी: जोरदार वारा.", "neutral": "कापणी: दररोज हवामान पाहून ठरवा."},
        "irrigation": {"good": "सिंचन: पाऊस पुरesa. पाणी वाचवा.", "urgent": "सिंचन: उष्ण व कोरडे. सकाळ/संध्याकाळ.", "caution": "सिंचन: कमी पाऊस. ओलावा ठेवा.", "neutral": "सिंचन: मातीचा ओलावा पाहून."},
    },
    "bn": {
        "header": "{district}, {state} — {term} আবহাওয়া পরামর্শ",
        "forecast": "আবহাওয়া: {weather}. তাপমাত্রা {tmin}°C–{tmax}°C. {days} দিনে {rain} mm বৃষ্টি।",
        "sowing": {"good": "বপন: মাটিতে আর্দ্রতা ভালো। বপনের উপযুক্ত সময়।", "avoid": "বপন: heavy rain. মাঠ শুকিয়ে যাওয়ার পর বপন করুন।", "caution": "বপon: গরম ও শুষ্ক। সেচ থাকলে বপন।", "neutral": "বপon: সতর্কতার সাথে সিদ্ধান্ত নিন।"},
        "fertilizer": {"good": "সার: স্থিতিশীল আবহাওয়া। সার প্রয়োগ উপযুক্ত।", "avoid": "সার: heavy rain সার ধুয়ে নিতে পারে।", "caution": "সার: extreme heat.", "neutral": "সার: সন্ধ্যায় সার দিন।"},
        "harvest": {"good": "ফসল তোলা: শুষ্ক আবহাওয়া।", "avoid": "ফসল তোলা: বৃষ্টিতে ক্ষতি।", "caution": "ফসল তোলা: strong wind.", "neutral": "ফসল তোলা: daily weather check."},
        "irrigation": {"good": "সেচ: বৃষ্টি যথেষ্ট।", "urgent": "সেচ: গরম ও শুষ্ক।", "caution": "সেচ: কম বৃষ্টি।", "neutral": "সেচ: মাটির আর্দ্রতা দেখে।"},
    },
}

# Fallback to Hindi templates for languages without full coverage
for code in ("kn", "ml", "gu", "pa", "or", "as"):
    if code not in ADVISORY_TEMPLATES:
        ADVISORY_TEMPLATES[code] = ADVISORY_TEMPLATES["hi"]


def translate_forecast_entry(entry: dict[str, Any]) -> dict[str, Any]:
    lang = entry.get("language_code", "hi")
    templates = ADVISORY_TEMPLATES.get(lang, ADVISORY_TEMPLATES["hi"])
    term_labels = TERM_LABELS.get(lang, TERM_LABELS["hi"])

    localized_forecasts = {}
    for term_key, slice_data in entry.get("forecasts", {}).items():
        term_label = term_labels.get(term_key, term_key)
        header = templates["header"].format(
            district=entry["district_name"],
            state=entry["state"],
            term=term_label,
        )
        forecast_line = templates["forecast"].format(
            weather=slice_data.get("dominant_weather", ""),
            tmin=slice_data.get("avg_temp_min_c", ""),
            tmax=slice_data.get("avg_temp_max_c", ""),
            days=slice_data.get("days", 0),
            rain=slice_data.get("total_rainfall_mm", 0),
        )

        advisories_local = {}
        for adv_key, adv_data in slice_data.get("advisories", {}).items():
            level = adv_data.get("level", "neutral")
            adv_templates = templates.get(adv_key, {})
            local_msg = adv_templates.get(level) or adv_data.get("message_en", "")
            advisories_local[adv_key] = {
                "level": level,
                "message_local": local_msg,
                "message_en": adv_data.get("message_en", ""),
            }

        localized_forecasts[term_key] = {
            **slice_data,
            "term_label_local": term_label,
            "message_local": f"{header}\n{forecast_line}",
            "advisories": advisories_local,
        }

    return {
        **entry,
        "forecasts": localized_forecasts,
    }
