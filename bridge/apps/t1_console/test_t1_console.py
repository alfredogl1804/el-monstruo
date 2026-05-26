import os

HTML_PATH = "/home/ubuntu/el-monstruo-bridge/bridge/apps/t1_console/t1_console_static.html"


def test_html_exists():
    assert os.path.exists(HTML_PATH), "T1 Console HTML not found"


def test_no_remote_scripts():
    with open(HTML_PATH, "r") as f:
        content = f.read()
    assert "<script src=" not in content, "HTML contains remote scripts"
    assert "fetch(" not in content, "HTML contains fetch calls"
    assert "XMLHttpRequest" not in content, "HTML contains XHR"


def test_no_supabase():
    with open(HTML_PATH, "r") as f:
        content = f.read()
    # It's okay if the word supabase appears in text, but not as an import or URL
    assert "supabase.co" not in content, "HTML contains Supabase URL"
    assert "@supabase" not in content, "HTML contains Supabase import"


def test_buttons_disabled():
    with open(HTML_PATH, "r") as f:
        content = f.read()
    assert '<button class="btn btn-approve" disabled>' in content, "Approve button is not disabled"


if __name__ == "__main__":
    test_html_exists()
    test_no_remote_scripts()
    test_no_supabase()
    test_buttons_disabled()
    print("T1 Console tests passed: 4/4")
