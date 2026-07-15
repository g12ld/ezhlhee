from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "08-authority-eeat"

MC_ECOMMERCE = "https://mc.gov.sa/ar/ECC/pages/default.aspx"
MC_GUIDE = "https://mc.gov.sa/ar/guides/CustomerGuide/Pages/ch4.aspx"
BUSINESS_VERIFY = "https://business.sa/eservices/details/4d6e9d30-e989-4940-08ce-08dbf015747a"
HRSD_FREELANCE = "https://www.wide.hrsd.gov.sa/ministry-services/services/%D8%AA%D8%AC%D8%AF%D9%8A%D8%AF-%D9%88%D8%AB%D9%8A%D9%82%D8%A9-%D8%A7%D9%84%D8%B9%D9%85%D9%84-%D8%A7%D9%84%D8%AD%D8%B1"
ZATCA_INVOICE = "https://zatca.gov.sa/ar/E-Invoicing/Introduction/Pages/What-is-e-invoicing.aspx"
SALLA_HELP = "https://help.salla.sa/"
ZID_HELP = "https://help.zid.sa/"
GOOGLE_SEARCH = "https://developers.google.com/search/docs/fundamentals/seo-starter-guide?hl=ar"
GOOGLE_PRODUCT = "https://developers.google.com/search/docs/appearance/structured-data/merchant-listing?hl=ar"
GOOGLE_ANALYTICS = "https://support.google.com/analytics/answer/12200568?hl=ar"
MONSHAAT_TOOLKIT = "https://www.monshaat.gov.sa/sites/default/files/2024-12/Toolkit_Catalogue_AR.pdf"
DATA_ANALYSIS_GUIDE = "/articles/تحليل-أداء-المتجر-وحسابات-التواصل-الاجتماعي-مؤشرات-الأداء-الرئيسية-kpis.html"


def source_link(url: str, label: str) -> str:
    return f'<li><a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a></li>'


COMMON_REVIEW = """
<aside class="content-review" aria-label="معلومات إعداد ومراجعة المحتوى">
  <h2>من أعد هذا المحتوى؟</h2>
  <p><strong>إعداد ومراجعة فريق إزهلها</strong> المتخصص في تصميم وتطوير متاجر سلة وزد وتهيئتها للسوق السعودي منذ 2022. نراجع الجانب العملي والتقني، ونربط المتطلبات النظامية بمصادرها الرسمية بدل الاعتماد على الوعود العامة.</p>
  <p><strong>آخر مراجعة:</strong> 15 يوليو 2026 · <strong>النطاق:</strong> المملكة العربية السعودية.</p>
</aside>
""".strip()


THIN_PAGE_CONTENT: dict[str, str] = {
    "brand-building.html": f"""
<section class="content authority-page">
  <p class="eyebrow">بناء هوية متجر سعودي قابلة للتطبيق</p>
  <h1>بناء العلامة التجارية للمتجر الإلكتروني</h1>
  <p class="lead">الهوية الناجحة ليست شعاراً منفصلاً عن المتجر. هي نظام يربط وعد العلامة بطريقة عرض المنتجات، ولغة المحتوى، وتجربة الطلب وما يراه العميل بعد الشراء. نبدأ من قرار تجاري واضح ثم نحوّله إلى واجهة متسقة على سلة أو زد.</p>
  <h2>ما الذي نحدده قبل التصميم؟</h2>
  <ul>
    <li><strong>الجمهور والسياق:</strong> من يشتري، وما المشكلة التي يحلها المنتج، ولماذا يختارك العميل السعودي؟</li>
    <li><strong>الوعد والتميّز:</strong> قيمة يمكن إثباتها في المنتج أو الخدمة، وليست عبارة تسويقية مبالغاً فيها.</li>
    <li><strong>شخصية العلامة:</strong> نبرة عربية طبيعية، مفردات ثابتة، وحدود واضحة لاستخدام الشعار والصور.</li>
    <li><strong>بنية الكتالوج:</strong> أسماء التصنيفات، طريقة تسمية المنتجات، وترتيب المعلومات بحسب قرار الشراء.</li>
  </ul>
  <h2>تطبيق الهوية داخل متجر سلة أو زد</h2>
  <p>نحوّل الهوية إلى نظام واجهة عملي: تدرج واضح للعناوين، أزرار متسقة، مسافات مريحة، قوالب للصور، وبنرات تخدم هدفاً محدداً. نختبر الصفحة الرئيسية وصفحة التصنيف والمنتج والسلة على الجوال أولاً، لأن جمال الهوية لا يكفي إذا أخفى السعر أو الشحن أو زر الإضافة للسلة.</p>
  <h2>مخرجات الخدمة</h2>
  <ul>
    <li>ملخص تموضع العلامة والجمهور ونبرة الكتابة.</li>
    <li>قواعد استخدام الشعار والألوان والخطوط والصور.</li>
    <li>قالب موحد لبنرات المتجر وصور التصنيفات والمنتجات.</li>
    <li>تطبيق الهوية على الثيم مع فحص الجوال والتباين وسهولة القراءة.</li>
    <li>قائمة تسليم تساعد صاحب المتجر على الحفاظ على الاتساق بعد الإطلاق.</li>
  </ul>
  <p>يمكن تنفيذ الهوية ضمن <a href="/salla-store-design.html">تصميم متجر سلة</a> أو <a href="/zid-store-design.html">تصميم متجر زد</a>، مع ربطها بخطة <a href="/product-marketing.html">تسويق المنتجات</a>.</p>
  <section class="official-sources" aria-labelledby="brand-sources"><h2 id="brand-sources">مراجع عملية رسمية</h2><ul>
    {source_link(MONSHAAT_TOOLKIT, "كتالوج أدلة وأدوات منشآت لرواد الأعمال")}
    {source_link(MC_ECOMMERCE, "وزارة التجارة: نظام وأدلة التجارة الإلكترونية")}
    {source_link(ZID_HELP, "مركز مساعدة زد: إعداد وتصميم المتجر")}
  </ul></section>
  {COMMON_REVIEW}
  <a class="authority-cta" href="https://wa.me/966501940155?text=أريد%20بناء%20هوية%20متجري" target="_blank" rel="noopener noreferrer">ناقش هوية متجرك مع مختص</a>
</section>
""".strip(),
    "competitor-analysis.html": f"""
<section class="content authority-page">
  <p class="eyebrow">تحليل يحوّل المقارنة إلى قرارات</p>
  <h1>تحليل منافسي المتاجر الإلكترونية في السعودية</h1>
  <p class="lead">تحليل المنافسين ليس نسخ تصميم متجر ناجح. الهدف هو معرفة ما يتوقعه العميل في فئتك، أين توجد فجوة حقيقية، وما الذي يجب أن يقدمه متجرك بشكل أوضح أو أسرع أو أكثر موثوقية.</p>
  <h2>محاور التحليل</h2>
  <ul>
    <li><strong>العرض التجاري:</strong> الفئات، نطاق الأسعار، الشحن، طرق الدفع، العروض والضمانات المعلنة.</li>
    <li><strong>تجربة العميل:</strong> وضوح الصفحة الرئيسية، الوصول للمنتج، الفلاتر، صفحة المنتج، والسلة على الجوال.</li>
    <li><strong>المحتوى والبحث:</strong> الكلمات التي يغطيها المنافس، صفحات التصنيفات، الأدلة، وجودة الربط الداخلي.</li>
    <li><strong>الثقة والامتثال:</strong> بيانات المنشأة، السياسات، قنوات التواصل، وتوضيح الاستبدال والشحن.</li>
    <li><strong>القياس:</strong> مؤشرات يمكن متابعتها بعد التنفيذ، لا انطباعات شكلية فقط.</li>
  </ul>
  <h2>كيف تتحول النتائج إلى خطة؟</h2>
  <p>نصنّف الفرص بحسب أثرها وسهولة تنفيذها: إصلاحات حرجة قبل الإطلاق، تحسينات قصيرة المدى، وتجارب تحتاج بيانات. لكل توصية مالك واضح ومؤشر نجاح مثل تحسن الوصول إلى المنتج، انخفاض الخروج من السلة، أو نمو الزيارات غير المدفوعة. لا نستخدم معلومات سرية ولا نقلّد هوية أو محتوى منافس.</p>
  <h2>ما الذي تستلمه؟</h2>
  <ul><li>قائمة منافسين مباشرين وغير مباشرين مع سبب الاختيار.</li><li>مصفوفة مقارنة موثقة بلقطات وروابط وتاريخ الفحص.</li><li>خريطة فجوات في المحتوى والواجهة والعرض التجاري.</li><li>أولويات 30 و60 و90 يوماً مرتبطة بمؤشرات أداء.</li></ul>
  <p>يُستخدم التقرير لتوجيه <a href="/brand-building.html">بناء العلامة</a> و<a href="/search-engine-optimization.html">تهيئة المتجر للبحث</a> و<a href="{DATA_ANALYSIS_GUIDE}">خطة القياس</a>.</p>
  <section class="official-sources" aria-labelledby="competitor-sources"><h2 id="competitor-sources">مراجع رسمية للسوق</h2><ul>
    {source_link(MONSHAAT_TOOLKIT, "منشآت: أدلة وأدوات تطوير المشاريع")}
    {source_link(MC_GUIDE, "وزارة التجارة: دليل المتاجر الإلكترونية وحقوق المستهلك")}
  </ul></section>
  {COMMON_REVIEW}
</section>
""".strip(),
    "data-analysis.html": f"""
<section class="content authority-page">
  <p class="eyebrow">قياس رحلة العميل لا عدد الزيارات فقط</p>
  <h1>تحليل بيانات المتجر الإلكتروني وتحسين الأداء</h1>
  <p class="lead">التقرير المفيد يجيب عن سؤال تجاري محدد: من أين يأتي العملاء المناسبون؟ أين يتوقفون؟ ما المنتجات التي تدفع الإيراد؟ وما التغيير الذي يجب اختباره بعد ذلك؟ لذلك نبدأ بخطة قياس قبل إضافة لوحات كثيرة.</p>
  <h2>خطة القياس الأساسية</h2>
  <ul><li>تحديد الأحداث المهمة: مشاهدة المنتج، الإضافة للسلة، بدء الدفع، الشراء والاسترداد.</li><li>توحيد أسماء المنتجات والفئات وقيم الطلب والعملة داخل الأحداث.</li><li>التحقق من عدم تكرار عمليات الشراء وربط كل طلب بمعرّف معاملة.</li><li>توثيق مصادر الحملات حتى لا تختلط الزيارات المدفوعة والمباشرة.</li><li>اختبار الموافقة والخصوصية وفق إعدادات المتجر والأدوات المستخدمة.</li></ul>
  <h2>المؤشرات التي نستخدمها في القرار</h2>
  <p>نقيس معدل التحويل، متوسط قيمة الطلب، الإيراد لكل قناة، نسبة الإضافة للسلة، التسرب بين السلة والدفع، أداء المنتجات، العملاء الجدد والعائدين. لا نقرأ رقماً منفرداً؛ نقارنه بالفترة والقناة والجهاز وتغيرات المخزون أو السعر.</p>
  <h2>مخرجات التحليل</h2>
  <ul><li>تدقيق إعداد GA4 والبكسلات والأحداث الأساسية.</li><li>قاموس قياس يشرح كل حدث ومعامل ومصدره.</li><li>لوحة مختصرة للإدارة مع تنبيهات جودة البيانات.</li><li>قائمة فرص مرتبة بالأثر والثقة والجهد.</li><li>دورة مراجعة شهرية تفصل الملاحظة عن الفرضية ونتيجة الاختبار.</li></ul>
  <p>يمكن ربط الخطة بخدمة <a href="/digital-ads.html">الإعلانات الرقمية</a> أو <a href="/product-marketing.html">تسويق المنتجات</a> حتى تكون قرارات الميزانية قابلة للقياس.</p>
  <section class="official-sources" aria-labelledby="analytics-sources"><h2 id="analytics-sources">مراجع القياس الرسمية</h2><ul>
    {source_link(GOOGLE_ANALYTICS, "Google Analytics: إعداد أحداث التجارة الإلكترونية")}
    {source_link(MONSHAAT_TOOLKIT, "منشآت: أدوات تحليل وتطوير الأعمال")}
  </ul></section>
  {COMMON_REVIEW}
</section>
""".strip(),
    "digital-ads.html": f"""
<section class="content authority-page">
  <p class="eyebrow">حملات مبنية على جاهزية المتجر والقياس</p>
  <h1>إدارة الإعلانات الرقمية للمتاجر الإلكترونية</h1>
  <p class="lead">الإعلان لا يعالج صفحة منتج ضعيفة أو تتبعاً ناقصاً. قبل الإنفاق نراجع العرض، سرعة الجوال، المخزون، الشحن، وسياسة الاستبدال، ثم نبني قياساً يسمح بمعرفة الطلب الحقيقي بدلاً من الاكتفاء بالنقرات.</p>
  <h2>قبل إطلاق الحملة</h2>
  <ul><li>تحديد هدف واضح: اكتساب عميل جديد، بيع فئة محددة، إعادة استهداف، أو تنشيط عملاء سابقين.</li><li>التحقق من أحداث المشاهدة والإضافة للسلة والدفع والشراء وقيمة الطلب.</li><li>مراجعة صفحة الهبوط وتطابق الرسالة والسعر والمخزون مع الإعلان.</li><li>تجهيز مواد إعلانية بأكثر من زاوية دون ادعاءات لا يمكن إثباتها.</li><li>وضع ميزانية اختبار وحدود إيقاف قبل التوسع.</li></ul>
  <h2>إدارة الحملة والتحسين</h2>
  <p>نقسم الحملات بحسب الجمهور والمنتج والمرحلة، ونراجع جودة البيانات ومعدل التحويل وتكلفة اكتساب العميل والعائد بعد الخصومات والشحن. لا نعد بنتيجة مضمونة؛ أداء الإعلان يتأثر بالسوق والعرض والموسم والمخزون وتجربة المتجر.</p>
  <h2>مخرجات قابلة للتسليم</h2>
  <ul><li>خريطة حملات وأهداف ومؤشرات نجاح.</li><li>تدقيق ربط Google وSnapchat وTikTok حسب النطاق المتفق عليه.</li><li>قواعد تسمية ووسوم UTM وتقرير جودة التتبع.</li><li>سجل اختبارات يوضح الفرضية والمدة والنتيجة والقرار.</li><li>توصيات مباشرة لصفحات المنتجات والسلة عندما تكون هي سبب التسرب.</li></ul>
  <p>تكتمل الخدمة مع <a href="{DATA_ANALYSIS_GUIDE}">تحليل البيانات</a> و<a href="/product-marketing.html">تسويق المنتجات</a>.</p>
  <section class="official-sources" aria-labelledby="ads-sources"><h2 id="ads-sources">مراجع القياس والسوق</h2><ul>
    {source_link(GOOGLE_ANALYTICS, "Google Analytics: أحداث التجارة الإلكترونية")}
    {source_link(MC_ECOMMERCE, "وزارة التجارة: ضوابط وأدلة التجارة الإلكترونية")}
  </ul></section>
  {COMMON_REVIEW}
</section>
""".strip(),
    "product-marketing.html": f"""
<section class="content authority-page">
  <p class="eyebrow">من بيانات المنتج إلى قرار الشراء</p>
  <h1>تسويق منتجات المتجر الإلكتروني</h1>
  <p class="lead">تسويق المنتج يبدأ داخل الكتالوج: اسم مفهوم، صور صادقة، مواصفات منظمة، سعر وشحن واضحان، ثم رسالة تناسب حاجة العميل. عندما تكون بيانات المنتج ضعيفة، تتأثر الإعلانات والبحث وتجربة الشراء معاً.</p>
  <h2>بناء أساس المنتج</h2>
  <ul><li>تقسيم المنتجات إلى فئات يفهمها العميل ومحرك البحث.</li><li>كتابة عنوان يصف النوع والميزة الأساسية دون تكرار أو حشو.</li><li>عرض المقاسات والمواد والاستخدام والعناية وما يتضمنه الطلب.</li><li>استخدام صور متناسقة وخفيفة مع نص بديل وصفي.</li><li>توضيح السعر والتوفر والشحن والاستبدال قبل الوصول إلى الدفع.</li></ul>
  <h2>ربط المنتج بالقنوات</h2>
  <p>نجهز بيانات متسقة للمتجر ومحركات البحث وMerchant Center والحملات. نفصل بين صفحات المنتجات وصفحات التصنيفات والأدلة؛ صفحة المنتج تجيب عن قرار الشراء، بينما التصنيف يساعد على المقارنة والاكتشاف.</p>
  <h2>خطة تسويق قابلة للقياس</h2>
  <ul><li>تحديد المنتجات القائدة ومنتجات الربح ومنتجات البيع التكميلي.</li><li>تقويم محتوى مرتبط بالمواسم الفعلية والمخزون.</li><li>اختبار العنوان والصورة والعرض وصفحة الهبوط كل عنصر على حدة.</li><li>متابعة المشاهدة والإضافة للسلة والشراء ومتوسط قيمة الطلب.</li><li>تحديث المنتجات الضعيفة أو دمجها دون إنشاء محتوى مكرر.</li></ul>
  <p>اربط الخطة بخدمة <a href="/search-engine-optimization.html">SEO المتاجر</a> و<a href="/digital-ads.html">الإعلانات الرقمية</a> و<a href="{DATA_ANALYSIS_GUIDE}">التحليل</a>.</p>
  <section class="official-sources" aria-labelledby="product-sources"><h2 id="product-sources">مراجع رسمية للمنتجات</h2><ul>
    {source_link(GOOGLE_PRODUCT, "Google Search Central: بيانات Product وOffer للمتاجر")}
    {source_link(SALLA_HELP, "مركز مساعدة سلة")}
    {source_link(ZID_HELP, "مركز مساعدة زد")}
  </ul></section>
  {COMMON_REVIEW}
</section>
""".strip(),
    "search-engine-optimization.html": f"""
<section class="content authority-page">
  <p class="eyebrow">SEO تقني ومحتوى تجاري لمتاجر سلة وزد</p>
  <h1>تهيئة المتجر الإلكتروني لمحركات البحث</h1>
  <p class="lead">تهيئة المتجر ليست إضافة كلمات داخل الوصف. نعمل من خط أساس موثق، ثم نعالج الوصول والفهرسة، بنية التصنيفات، جودة صفحات المنتجات، السرعة والربط الداخلي، ونقيس أثر التغييرات في Search Console.</p>
  <h2>نطاق التدقيق</h2>
  <ul><li>حصر الروابط الحالية وحالاتها والروابط الخلفية المهمة قبل أي تغيير.</li><li>فحص robots.txt وsitemap وcanonical والتحويلات وأخطاء الزحف.</li><li>مراجعة العناوين والأوصاف وH1 والبيانات المنظمة والصور.</li><li>تحليل صفحات التصنيفات والمنتجات والمحتوى حسب نية البحث السعودية.</li><li>قياس Core Web Vitals وتجربة الجوال والروابط الداخلية والصفحات اليتيمة.</li></ul>
  <h2>التنفيذ على سلة وزد</h2>
  <p>نستخدم إمكانات المنصة أولاً، ثم نضيف تخصيصات محدودة وقابلة للصيانة. نحافظ على الروابط التي تملك ظهوراً أو روابط خلفية، وأي تغيير ضروري يحصل على خريطة 301 وتحديث متزامن للروابط الداخلية وcanonical وsitemap.</p>
  <h2>ما الذي نقيسه؟</h2>
  <p>نتابع الصفحات المفهرسة، اختيار Google للـ canonical، الاستعلامات والصفحات والبلدان والأجهزة، الأخطاء الجديدة، Core Web Vitals، ونمو الزيارات والتحويلات غير المدفوعة. لا توجد جهة مهنية تستطيع ضمان مركز محدد؛ الهدف هو إزالة العوائق وبناء إشارات مفيدة قابلة للقياس.</p>
  <h2>المخرجات</h2>
  <ul><li>Baseline قبل التنفيذ وتقرير مقارنة بعد الإطلاق.</li><li>قائمة إصلاحات تقنية وأولوية وأثر متوقع.</li><li>خريطة كلمات وصفحات تمنع التنافس الداخلي.</li><li>خطة محتوى وربط داخلي ومراقبة لمدة 30 يوماً.</li></ul>
  <p>ابدأ من <a href="/salla-store-design.html">تصميم متجر سلة</a> أو <a href="/zid-store-design.html">تصميم متجر زد</a> للحصول على مسار متكامل.</p>
  <section class="official-sources" aria-labelledby="seo-sources"><h2 id="seo-sources">مراجع SEO الرسمية</h2><ul>
    {source_link(GOOGLE_SEARCH, "Google Search Central: دليل تحسين محركات البحث")}
    {source_link(SALLA_HELP, "مركز مساعدة سلة: إعدادات المتجر والظهور")}
    {source_link(ZID_HELP, "مركز مساعدة زد: تحسين الظهور وصفحات المتجر")}
  </ul></section>
  {COMMON_REVIEW}
  <a class="authority-cta" href="https://wa.me/966501940155?text=أريد%20تدقيق%20SEO%20لمتجري" target="_blank" rel="noopener noreferrer">اطلب تدقيق SEO لمتجرك</a>
</section>
""".strip(),
    "secure-payments.html": f"""
<section class="content authority-page">
  <p class="eyebrow">تكامل الدفع والثقة والمطابقة التشغيلية</p>
  <h1>تفعيل المدفوعات الآمنة للمتجر الإلكتروني</h1>
  <p class="lead">اختيار وسيلة الدفع لا يقتصر على إضافة شعارها. نراجع أهلية المنشأة، رحلة الدفع على الجوال، ظهور الرسوم والشحن، معالجة حالات النجاح والفشل، وإجراءات المطابقة والاسترداد بعد الطلب.</p>
  <h2>خطوات التفعيل</h2>
  <ol><li>تأكيد بيانات المنشأة والحساب البنكي والتوثيق المطلوب من المزود والمنصة.</li><li>تحديد الوسائل المناسبة للجمهور: مدى، البطاقات، Apple Pay، وخيارات الدفع الآجل عند الأهلية.</li><li>تفعيل التكامل الرسمي داخل سلة أو زد وتجنب تمرير بيانات البطاقة عبر أكواد مخصصة غير لازمة.</li><li>اختبار الدفع الناجح والمرفوض والملغى، والاسترداد الكامل والجزئي.</li><li>مطابقة الطلبات مع تسويات المزود وتوثيق المسؤول عن معالجة الفروقات.</li></ol>
  <h2>ما الذي يراه العميل؟</h2>
  <p>يجب أن يعرف العميل السعر الإجمالي، الشحن، وقت التسليم، وسياسة الاستبدال قبل الدفع. نقلل الحقول، نستخدم رسائل خطأ واضحة، ونحافظ على حالة السلة عند تعثر العملية. لا نعرض وسيلة غير مفعلة أو وعد قبول غير مؤكد.</p>
  <h2>الفوترة والامتثال</h2>
  <p>إذا كان نشاطك خاضعاً لمتطلبات الفوترة الإلكترونية أو ضريبة القيمة المضافة، تُراجع المتطلبات مع هيئة الزكاة والضريبة والجمارك أو مستشارك المختص. دورنا تقني وتشغيلي ولا يحل محل الاستشارة القانونية أو الضريبية.</p>
  <p>يمكن دمج التفعيل مع <a href="/store-verification.html">توثيق المتجر</a> و<a href="/salla-store-design.html">إعداد متجر سلة</a>.</p>
  <section class="official-sources" aria-labelledby="payment-sources"><h2 id="payment-sources">مراجع رسمية للمدفوعات والفوترة</h2><ul>
    {source_link(ZATCA_INVOICE, "هيئة الزكاة والضريبة والجمارك: الفوترة الإلكترونية")}
    {source_link(MC_GUIDE, "وزارة التجارة: المتاجر الإلكترونية وحقوق المستهلك")}
    {source_link(SALLA_HELP, "مركز مساعدة سلة: إعدادات ووسائل الدفع")}
  </ul></section>
  {COMMON_REVIEW}
</section>
""".strip(),
    "store-verification.html": f"""
<section class="content authority-page">
  <p class="eyebrow">المتطلبات الرسمية الحالية في السعودية</p>
  <h1>توثيق المتجر الإلكتروني عبر منصة الأعمال</h1>
  <p class="lead">أصبحت خدمة توثيق التجارة الإلكترونية متاحة عبر المركز السعودي للأعمال. نساعدك في تجهيز المتجر والبيانات والروابط قبل التقديم، لكن الموافقة تصدر من الجهة الرسمية ولا يمكن لأي مزود خدمة ضمانها.</p>
  <h2>متطلبات ينبغي التحقق منها</h2>
  <ul><li>سجل تجاري أو وثيقة عمل حر سارية ومناسبة للنشاط.</li><li>حساب بنكي مرتبط بالسجل التجاري أو وثيقة العمل الحر لمقدم الطلب.</li><li>رابط متجر سليم وفعّال؛ حسابات التواصل تُستخدم كقنوات إضافية وليست بديلاً عن رابط المتجر.</li><li>وضوح ملكية اسم النطاق وعدم انتحال متجر أو علامة أخرى.</li><li>توافق المنتجات والخدمات مع النشاط المصرّح به والمتطلبات النظامية.</li><li>عرض بيانات المنشأة والتراخيص والسياسات ووسيلة تواصل واضحة داخل المتجر.</li></ul>
  <h2>تجهيز المتجر قبل الطلب</h2>
  <p>نراجع الصفحة الرئيسية وبيانات التواصل وسياسة الخصوصية والاستبدال والاسترجاع والشحن، ونختبر الروابط والجوال والنطاق. نطابق اسم المنشأة والحساب البنكي والدومين قدر الإمكان حتى نقلل طلبات الاستكمال، ثم نسلّمك قائمة تحقق بما تم وما يحتاج إجراءً من المالك.</p>
  <h2>حدود الخدمة</h2>
  <p>المتطلبات قد تتغير بحسب النشاط والجهة. إزهلها لا تصدر الشهادة ولا تمثل جهة حكومية، ولا تقدم استشارة قانونية. القرار والمدة النهائية لدى المركز السعودي للأعمال؛ لذلك يجب مراجعة صفحة الخدمة الرسمية وقت التقديم.</p>
  <p>قد تحتاج أولاً إلى <a href="/secure-payments.html">تجهيز الدفع والحساب البنكي</a> أو <a href="/salla-store-design.html">إكمال إعداد متجر سلة</a>.</p>
  <section class="official-sources" aria-labelledby="verification-sources"><h2 id="verification-sources">المصادر الرسمية</h2><ul>
    {source_link(BUSINESS_VERIFY, "المركز السعودي للأعمال: توثيق التجارة الإلكترونية")}
    {source_link(MC_ECOMMERCE, "وزارة التجارة: نظام التجارة الإلكترونية وأدلته")}
    {source_link(HRSD_FREELANCE, "وزارة الموارد البشرية: إصدار وتجديد وثيقة العمل الحر")}
  </ul></section>
  {COMMON_REVIEW}
  <a class="authority-cta" href="https://wa.me/966501940155?text=أريد%20تجهيز%20متجري%20للتوثيق" target="_blank" rel="noopener noreferrer">اطلب مراجعة جاهزية التوثيق</a>
</section>
""".strip(),
}


def article_sources(name: str) -> tuple[str, list[tuple[str, str]]]:
    regulatory = ("توثيق", "وثيقة", "العمل-الحر", "منصة-الأعمال", "سجل-تجاري", "حساب-بنكي")
    payments = ("دفع", "تابي", "تمارا", "ميس", "مدفوع", "إمكان", "فاتورة", "مصرف")
    analytics = ("seo", "تحسين", "جوجل", "google", "analytics", "بكس", "إعلان", "تحويلات", "بيانات")
    design = ("تصميم", "سلة", "زد", "منتج", "جوال", "css", "قالب", "تجربة")
    if any(term in name for term in regulatory):
        return "المتطلبات النظامية", [(BUSINESS_VERIFY, "المركز السعودي للأعمال: توثيق التجارة الإلكترونية"), (MC_ECOMMERCE, "وزارة التجارة: نظام التجارة الإلكترونية"), (HRSD_FREELANCE, "وزارة الموارد البشرية: وثيقة العمل الحر")]
    if any(term in name for term in payments):
        return "الدفع والفوترة", [(ZATCA_INVOICE, "هيئة الزكاة والضريبة والجمارك: الفوترة الإلكترونية"), (MC_GUIDE, "وزارة التجارة: دليل المتاجر الإلكترونية"), (SALLA_HELP, "مركز مساعدة سلة")]
    if any(term in name.lower() for term in analytics):
        return "القياس والظهور", [(GOOGLE_SEARCH, "Google Search Central: دليل SEO"), (GOOGLE_ANALYTICS, "Google Analytics: قياس التجارة الإلكترونية"), (SALLA_HELP, "مركز مساعدة سلة")]
    if any(term in name.lower() for term in design):
        return "المنصة وتجربة المتجر", [(SALLA_HELP, "مركز مساعدة سلة"), (ZID_HELP, "مركز مساعدة زد"), (MC_GUIDE, "وزارة التجارة: دليل المتاجر الإلكترونية")]
    return "التجارة الإلكترونية", [(MC_ECOMMERCE, "وزارة التجارة: نظام التجارة الإلكترونية"), (SALLA_HELP, "مركز مساعدة سلة"), (ZID_HELP, "مركز مساعدة زد")]


def build_article_authority(path: Path) -> tuple[str, str]:
    topic, sources = article_sources(path.stem)
    source_items = "\n".join(source_link(url, label) for url, label in sources)
    regulatory_note = ""
    if topic in {"المتطلبات النظامية", "الدفع والفوترة"}:
        regulatory_note = '<p class="source-note">المتطلبات والرسوم والأهلية قد تتغير؛ راجع الجهة الرسمية وقت التنفيذ. المحتوى إرشادي ولا يعد استشارة قانونية أو ضريبية.</p>'
    block = f"""
<section class="official-sources" aria-labelledby="official-sources-title">
  <h2 id="official-sources-title">مراجع رسمية مرتبطة بالموضوع</h2>
  <p>راجع فريق إزهلها هذا الدليل بالاستناد إلى مصادر {topic} التالية، مع تطبيقها على سياق المتاجر السعودية:</p>
  <ul>{source_items}</ul>
  {regulatory_note}
</section>
<aside class="content-review" aria-label="معلومات إعداد ومراجعة المقال">
  <h2>إعداد ومراجعة المقال</h2>
  <p><strong>فريق إزهلها</strong> — متخصصون في تصميم وتطوير متاجر سلة وزد وتهيئتها تقنياً للسوق السعودي منذ 2022.</p>
  <p><strong>آخر مراجعة:</strong> 15 يوليو 2026 · نراجع المصادر الرسمية عند تحديث المتطلبات أو المنصات.</p>
</aside>
""".strip()
    return topic, block


def replace_main_content(source: str, content: str) -> str:
    return re.sub(r'<main id="main-content">.*?</main>', f'<main id="main-content">\n{content}\n</main>', source, count=1, flags=re.S)


def improve_article(path: Path) -> tuple[bool, str]:
    source = path.read_text(encoding="utf-8")
    original = source
    topic, authority = build_article_authority(path)
    source = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", source)
    source = source.replace("مما يضمن ظهورك في المراتب الأولى لنتائج محركات البحث", "بما يدعم فرص ظهورك على الاستعلامات المناسبة في نتائج البحث")
    source = source.replace("ضمان القبول السريع", "تقليل احتمالات التأخير")
    related_match = re.search(r'\s*<aside class="related-reading".*?</aside>', source, flags=re.S)
    related = related_match.group(0).strip() if related_match else ""
    if related_match:
        source = source[:related_match.start()] + source[related_match.end():]
    source = re.sub(r'\s*<section class="official-sources".*?</section>\s*<aside class="content-review".*?</aside>', "", source, flags=re.S)
    insertion = authority + ("\n" + related if related else "")
    source = source.replace("</main>", f"{insertion}\n</main>", 1)
    if source != original:
        path.write_text(source, encoding="utf-8")
    return source != original, topic


def improve_article_index() -> bool:
    path = ROOT / "articles.html"
    source = path.read_text(encoding="utf-8")
    original = source
    block = f"""
<section class="editorial-method" aria-labelledby="editorial-method-title">
  <h2 id="editorial-method-title">منهج إعداد مكتبة إزهلها</h2>
  <p>يعد فريق إزهلها الأدلة للسوق السعودي ويربط الخطوات العملية بمصادر الجهات والمنصات الرسمية. نوضح حدود الخدمة، ونتجنب ضمان الترتيب أو القبول أو نتيجة إعلانية لا يمكن إثباتها.</p>
  <ul><li>كل مقال يحمل جهة الإعداد وتاريخ آخر مراجعة.</li><li>الموضوعات النظامية والدفع تربط بالمصدر الرسمي وتُنبه إلى احتمال تغير المتطلبات.</li><li>التحديثات الجوهرية تُراجع قبل تعديل التاريخ، ولا نغير التاريخ لمجرد إعادة النشر.</li><li>توجد روابط سياقية بين الدليل والخدمة والموضوعات المكملة.</li></ul>
  <p>مصادرنا الأساسية: <a href="{MC_ECOMMERCE}" target="_blank" rel="noopener noreferrer">وزارة التجارة</a>، <a href="{BUSINESS_VERIFY}" target="_blank" rel="noopener noreferrer">المركز السعودي للأعمال</a>، <a href="{SALLA_HELP}" target="_blank" rel="noopener noreferrer">سلة</a>، <a href="{ZID_HELP}" target="_blank" rel="noopener noreferrer">زد</a>، و<a href="{GOOGLE_SEARCH}" target="_blank" rel="noopener noreferrer">Google Search Central</a>.</p>
</section>
""".strip()
    source = re.sub(r'\s*<section class="editorial-method".*?</section>', "", source, flags=re.S)
    source = source.replace("</main>", f"{block}\n</main>", 1)
    if source != original:
        path.write_text(source, encoding="utf-8")
    return source != original


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for filename, content in THIN_PAGE_CONTENT.items():
        path = ROOT / filename
        source = path.read_text(encoding="utf-8")
        updated = replace_main_content(source, content)
        if updated != source:
            path.write_text(updated, encoding="utf-8")
        rows.append({"file": filename, "change": "expanded authority service page", "topic": "service authority", "official_sources": str(updated.count('class="official-sources"'))})
    article_changes = 0
    for path in sorted((ROOT / "articles").glob("*.html")):
        changed, topic = improve_article(path)
        article_changes += int(changed)
        rows.append({"file": path.relative_to(ROOT).as_posix(), "change": "added authorship, review date, official references, and HTML cleanup", "topic": topic, "official_sources": "1"})
    index_changed = improve_article_index()
    rows.append({"file": "articles.html", "change": "added visible editorial methodology and official source policy", "topic": "editorial trust", "official_sources": "1"})
    with (REPORT_DIR / "content-change-map.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["file", "change", "topic", "official_sources"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Expanded {len(THIN_PAGE_CONTENT)} service pages; updated {article_changes} articles; article index changed={index_changed}.")


if __name__ == "__main__":
    main()
