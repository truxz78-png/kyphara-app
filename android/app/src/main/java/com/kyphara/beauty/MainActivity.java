package com.kyphara.beauty;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import androidx.activity.OnBackPressedCallback;
import androidx.appcompat.app.AppCompatActivity;
import androidx.browser.customtabs.CustomTabColorSchemeParams;
import androidx.browser.customtabs.CustomTabsIntent;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

public class MainActivity extends AppCompatActivity {
    private static final String HOME = "https://truxz78-png.github.io/kyphara-app/";
    private static final String HOST = "truxz78-png.github.io";
    private static final String PATH = "/kyphara-app";
    private static final int PINK = Color.parseColor("#E8175D");
    private static final int BG = Color.parseColor("#FFF4F7");
    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(BG);
        web = new WebView(this);
        web.setBackgroundColor(BG);
        root.addView(web);
        setContentView(root);

        // Android 15+ draws edge to edge: keep content clear of the system bars
        ViewCompat.setOnApplyWindowInsetsListener(root, (v, insets) -> {
            Insets bars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(bars.left, bars.top, bars.right, bars.bottom);
            return WindowInsetsCompat.CONSUMED;
        });

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return handle(request.getUrl());
            }
        });

        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                if (web.canGoBack()) {
                    web.goBack();
                } else {
                    setEnabled(false);
                    getOnBackPressedDispatcher().onBackPressed();
                }
            }
        });

        if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            web.loadUrl(HOME);
        }
    }

    // Own pages stay inside the app. Stores open in a Chrome Custom Tab:
    // the phone's Back button closes the store and returns to Kyphara.
    private boolean handle(Uri uri) {
        String scheme = uri.getScheme() == null ? "" : uri.getScheme();
        if (("https".equals(scheme) || "http".equals(scheme))
                && HOST.equals(uri.getHost())
                && uri.getPath() != null && uri.getPath().startsWith(PATH)) {
            return false;
        }
        try {
            if ("mailto".equals(scheme)) {
                startActivity(new Intent(Intent.ACTION_SENDTO, uri));
            } else if ("intent".equals(scheme)) {
                Intent i = Intent.parseUri(uri.toString(), Intent.URI_INTENT_SCHEME);
                try {
                    startActivity(i);
                } catch (ActivityNotFoundException e) {
                    String fb = i.getStringExtra("browser_fallback_url");
                    if (fb != null) openTab(Uri.parse(fb));
                }
            } else if ("https".equals(scheme) || "http".equals(scheme)) {
                openTab(uri);
            } else {
                startActivity(new Intent(Intent.ACTION_VIEW, uri));
            }
        } catch (Exception ignored) {
        }
        return true;
    }

    private void openTab(Uri uri) {
        try {
            CustomTabsIntent tab = new CustomTabsIntent.Builder()
                    .setDefaultColorSchemeParams(new CustomTabColorSchemeParams.Builder()
                            .setToolbarColor(PINK).build())
                    .setShowTitle(true)
                    .build();
            tab.launchUrl(this, uri);
        } catch (Exception e) {
            startActivity(new Intent(Intent.ACTION_VIEW, uri));
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        web.saveState(outState);
    }
}
