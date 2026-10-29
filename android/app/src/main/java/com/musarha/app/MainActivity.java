package com.musarha.app;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebResourceRequest;
import android.graphics.Color;
import android.view.View;
import android.view.Gravity;
import android.view.inputmethod.InputMethodManager;
import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private WebView webView;
    private SharedPreferences prefs;
    private static final String PREFS = "musarha_settings";
    private static final String URL_KEY = "game_url";
    private final int bg = Color.rgb(24, 15, 44);

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);
        String savedUrl = prefs.getString(URL_KEY, "");
        if (savedUrl.isEmpty()) showSetupScreen("");
        else loadGame(savedUrl);
    }

    private void showSetupScreen(String previous) {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER_VERTICAL);
        root.setPadding(28, 36, 28, 36);
        root.setBackgroundColor(bg);

        TextView title = new TextView(this);
        title.setText("مصارحة 💕");
        title.setTextColor(Color.WHITE);
        title.setTextSize(30);
        title.setGravity(Gravity.CENTER);
        root.addView(title, new LinearLayout.LayoutParams(-1, -2));

        TextView info = new TextView(this);
        info.setText("أدخل رابط لعبة مصارحة بعد نشر السيرفر. لازم يبدأ الرابط بـ https://\n\nإذا ما عندكش الرابط، انشر مجلد server على Render أولاً.");
        info.setTextColor(Color.LTGRAY);
        info.setTextSize(16);
        info.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams infoParams = new LinearLayout.LayoutParams(-1, -2);
        infoParams.setMargins(0, 24, 0, 20);
        root.addView(info, infoParams);

        EditText urlInput = new EditText(this);
        urlInput.setSingleLine(true);
        urlInput.setText(previous);
        urlInput.setHint("https://اسم-اللعبة.onrender.com");
        urlInput.setHintTextColor(Color.GRAY);
        urlInput.setTextColor(Color.WHITE);
        urlInput.setLinkTextColor(Color.WHITE);
        urlInput.setPadding(14, 12, 14, 12);
        urlInput.setBackgroundColor(Color.rgb(53, 38, 74));
        root.addView(urlInput, new LinearLayout.LayoutParams(-1, -2));

        Button open = new Button(this);
        open.setText("فتح اللعبة");
        LinearLayout.LayoutParams btnParams = new LinearLayout.LayoutParams(-1, -2);
        btnParams.setMargins(0, 16, 0, 0);
        root.addView(open, btnParams);
        open.setOnClickListener(v -> {
            String url = urlInput.getText().toString().trim();
            if (!url.startsWith("https://") || url.length() < 13 || url.contains(" ")) {
                Toast.makeText(this, "أدخل رابط HTTPS صحيح بعد نشر السيرفر.", Toast.LENGTH_LONG).show();
                return;
            }
            ((InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE))
                    .hideSoftInputFromWindow(urlInput.getWindowToken(), 0);
            prefs.edit().putString(URL_KEY, url.replaceAll("/+$", "")).apply();
            loadGame(url.replaceAll("/+$", ""));
        });

        Button change = new Button(this);
        change.setText("حفظ الرابط فقط لاحقاً");
        change.setOnClickListener(v -> {
            String url = urlInput.getText().toString().trim();
            if (url.startsWith("https://") && !url.contains(" ")) {
                prefs.edit().putString(URL_KEY, url.replaceAll("/+$", "")).apply();
                Toast.makeText(this, "تم حفظ الرابط على هذا الهاتف.", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(this, "أدخل رابط HTTPS صحيح.", Toast.LENGTH_SHORT).show();
            }
        });
        root.addView(change, new LinearLayout.LayoutParams(-1, -2));
        setContentView(root);
    }

    private void loadGame(String url) {
        webView = new WebView(this);
        webView.setBackgroundColor(bg);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setLoadsImagesAutomatically(true);
        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                if ("https".equalsIgnoreCase(uri.getScheme())) return false;
                Toast.makeText(MainActivity.this, "لأمانك، التطبيق يفتح روابط HTTPS فقط.", Toast.LENGTH_SHORT).show();
                return true;
            }
        });
        setContentView(webView);
        webView.loadUrl(url);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else showSetupScreen(prefs.getString(URL_KEY, ""));
    }
}
