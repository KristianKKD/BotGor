from django.utils.html import escape


def render_index_page(initial_text:str) -> str:
    escaped_initial_text:str = escape(initial_text)
    return f"""<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>BotGor WebUI</title>
</head>
<body>
    <pre id=\"content\">{escaped_initial_text}</pre>
    <script>
        async function refreshText() {{
            try {{
                const response = await fetch('/text', {{ cache: 'no-store' }});
                if (!response.ok) return;

                const text = await response.text();
                const contentElement = document.getElementById('content');
                if (contentElement.textContent !== text) {{
                    contentElement.textContent = text;
                }}
            }} catch (_) {{}}
        }}

        setInterval(refreshText, 500);
        refreshText();
    </script>
</body>
</html>
"""