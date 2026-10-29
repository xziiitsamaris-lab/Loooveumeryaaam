# مصارحة 💕 — مشروع السيرفر وAPK

هذا المشروع يحتوي على:
- `server/`: لعبة الويب والسيرفر Flask.
- `android/`: تطبيق Android WebView يفتح رابط اللعبة بعد نشره.
- `.github/workflows/build-apk.yml`: يبني APK تلقائياً عبر GitHub Actions.
- `render.yaml`: إعداد نشر السيرفر على Render.

**مهم:** هذا ZIP ليس APK بحد ذاته. يلزم رفع المشروع إلى GitHub، نشر `server` على Render، ثم تشغيل بناء APK من تبويب Actions. لا تحتاج كمبيوتر، لكن تحتاج حساب GitHub وRender ومتصفح الهاتف.

## 1) رفع المشروع إلى GitHub من الهاتف
1. نزّل وفك ضغط `musarha_full.zip` باستعمال ZArchiver.
2. افتح GitHub في المتصفح وأنشئ Repository جديد باسم `musarha-online`، واجعله Public أو Private، ولا تضف README من GitHub (خليه فارغ).
3. أسهل طريقة لرفع المجلدات المتداخلة من الهاتف هي استعمال Termux من مصدره الرسمي، ثم تشغيل:

```sh
pkg update -y
pkg install git unzip -y
termux-setup-storage
cd ~/storage/downloads
unzip musarha_full.zip -d musarha_upload
cd musarha_upload/musarha_full
```

إذا كان ZIP في مجلد آخر، بدّل المسار حسب مكانه. بعد ذلك، في GitHub افتح المستودع واضغط Code ثم انسخ رابط HTTPS، وبعدها نفّذ:

```sh
git init
git add .
git commit -m "Add Musarha game and Android app"
git branch -M main
git remote add origin https://github.com/USERNAME/musarha-online.git
git push -u origin main
```

بدّل `USERNAME` باسم حسابك. إذا طلب تسجيل الدخول، اتبع صفحة GitHub؛ كلمة مرور حساب GitHub العادية لا تعمل مع Git عبر HTTPS، وقد تحتاج رمز وصول أو تسجيل الدخول عبر مدير بيانات الاعتماد.

## 2) نشر السيرفر على Render
1. أنشئ حساباً في Render واربطه بحساب GitHub.
2. اختر **New + → Blueprint** وحدد المستودع `musarha-online`.
3. وافق على إعداد `render.yaml` وانتظر النشر.
4. افتح خدمة `musarha-online` وانسخ رابط HTTPS، مثلاً `https://اسم-الخدمة.onrender.com`.
5. افتح الرابط في متصفح الهاتف. إذا ظهرت صفحة مصارحة، السيرفر يعمل.

قد يتوقف السيرفر المجاني مؤقتاً عند عدم الاستخدام ويحتاج وقتاً ليبدأ من جديد. الرسائل محفوظة مؤقتاً في ذاكرة السيرفر وقد تختفي عند إعادة تشغيله؛ لا ترسلوا معلومات خاصة.

## 3) بناء APK عبر GitHub Actions
1. في المستودع على GitHub افتح تبويب **Actions**.
2. اختر **Build Musarha APK**.
3. اضغط **Run workflow** ثم زر Run الأخضر.
4. انتظر حتى تصبح العملية خضراء، وافتح نتيجة التشغيل.
5. في قسم **Artifacts** نزّل `musarha-debug-apk` وفك ضغطه. داخله الملف `app-debug.apk`.
6. افتح APK على هاتف أندرويد واسمح بالتثبيت من هذا المصدر إذا طلب النظام ذلك.

## 4) ربط التطبيق بالسيرفر
عند فتح التطبيق أول مرة، الصق رابط HTTPS الذي نسخته من Render واضغط **فتح اللعبة**. يحفظ التطبيق الرابط على الهاتف. صديقك يقدر يدخل من متصفح الكمبيوتر أو الهاتف إلى نفس رابط Render، ثم يستعمل نفس كود الغرفة.

## ملاحظات
- APK الناتج نسخة Debug للتجربة وليس نسخة متجر Play موقّعة للنشر.
- لا تضع كلمة مرور أو أسراراً داخل ملفات المشروع.
- لا يمكن إكمال إنشاء حسابات GitHub/Render أو الموافقة على النشر نيابةً عنك؛ يلزم تنفيذ هذه الخطوات من حساباتك.
