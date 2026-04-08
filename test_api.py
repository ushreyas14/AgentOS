"""
test_api.py
───────────
Diagnostic utilities — run BEFORE starting the agent system.

Tests covered:
  1. API key presence check
  2. Live Gemini API call (sanity check)
  3. Quota / rate-limit detection
  4. Billing error detection
  5. Vertex AI vs AI Studio mode detection

Run:
    python test_api.py
"""

import os
import sys
import time

# ── Try to import the Google GenAI SDK ────────────────────────────────────────
try:
    import google.generativeai as genai
except ImportError:
    print("[ERROR] 'google-generativeai' is not installed.")
    print("        Run:  pip install google-generativeai")
    sys.exit(1)

from config import GEMINI_MODEL


# ═══════════════════════════════════════════════════════════════════════════════
# Helper: pretty-print test results
# ═══════════════════════════════════════════════════════════════════════════════

def _pass(msg: str) -> None:
    print(f"  ✅  {msg}")

def _fail(msg: str) -> None:
    print(f"  ❌  {msg}")

def _warn(msg: str) -> None:
    print(f"  ⚠️   {msg}")

def _section(title: str) -> None:
    print(f"\n{'─' * 55}")
    print(f"  {title}")
    print(f"{'─' * 55}")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 1 — API Key presence
# ═══════════════════════════════════════════════════════════════════════════════

def test_api_key_present() -> bool:
    """Check that GOOGLE_API_KEY is set in the environment."""
    _section("TEST 1 — API Key Presence")
    key = os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        _fail("GOOGLE_API_KEY environment variable is NOT set.")
        print("\n  How to fix:")
        print("    export GOOGLE_API_KEY='your-key-here'   # Linux / macOS")
        print("    set    GOOGLE_API_KEY=your-key-here      # Windows CMD")
        return False
    # Mask the key for display
    masked = key[:6] + "..." + key[-4:]
    _pass(f"GOOGLE_API_KEY found: {masked}")
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# Test 2 — Live Gemini API call
# ═══════════════════════════════════════════════════════════════════════════════

def test_gemini_call() -> bool:
    """Send a minimal prompt to Gemini and verify a response arrives."""
    _section("TEST 2 — Live Gemini API Call")
    key = os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        _fail("Skipped — no API key.")
        return False

    # NEW SDK INITIALIZATION
    client = genai.Client(api_key=key)

    try:
        start = time.time()
        # NEW SDK GENERATION CALL
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents='Reply with exactly one word: OK'
        )
        elapsed = round(time.time() - start, 2)
        text = response.text.strip()
        _pass(f"Response received in {elapsed}s: '{text}'")
        return True

    except Exception as exc:
        error_str = str(exc)
        _fail(f"API call failed: {error_str}")
        _classify_error(error_str)
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Test 3 — Quota / rate-limit detection
# ═══════════════════════════════════════════════════════════════════════════════

def test_quota_detection() -> bool:
    """
    Intentionally send rapid requests to surface quota errors,
    then classify the response. Uses a tiny prompt to minimise token cost.
    """
    _section("TEST 3 — Quota / Rate-Limit Detection")
    key = os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        _fail("Skipped — no API key.")
        return False

    # NEW SDK INITIALIZATION
    client = genai.Client(api_key=key)
    prompt = "1+1="

    quota_hit = False
    for i in range(3):          # 3 rapid calls — enough to observe quota headers
        try:
            # NEW SDK GENERATION CALL
            client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            _pass(f"Request {i + 1}/3 succeeded")
        except Exception as exc:
            error_str = str(exc)
            if "quota" in error_str.lower() or "429" in error_str:
                _warn(f"Quota limit hit on request {i + 1}: {error_str}")
                quota_hit = True
                break
            else:
                _fail(f"Unexpected error on request {i + 1}: {error_str}")
                _classify_error(error_str)
                return False

    if not quota_hit:
        _pass("No quota errors — you have healthy quota headroom.")
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# Test 4 — Billing / project error detection
# ═══════════════════════════════════════════════════════════════════════════════

def test_billing_detection() -> bool:
    """
    Make an API call and look for billing / project misconfiguration errors.
    This doesn't test billing directly (we can't), but classifies the error
    so the user knows what to fix.
    """
    _section("TEST 4 — Billing / Project Error Detection")
    key = os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        _fail("Skipped — no API key.")
        return False

    # NEW SDK INITIALIZATION
    client = genai.Client(api_key=key)

    try:
        # NEW SDK GENERATION CALL
        client.models.generate_content(
            model=GEMINI_MODEL,
            contents='ping'
        )
        _pass("No billing errors detected — project appears healthy.")
        return True
    except Exception as exc:
        error_str = str(exc)
        billing_keywords = [
            "billing", "payment", "403", "project", "disabled",
            "service account", "iam", "permission denied",
        ]
        if any(kw in error_str.lower() for kw in billing_keywords):
            _fail(f"Possible billing / project issue: {error_str}")
            print("\n  How to fix (GCP Console steps):")
            print("    1. Go to console.cloud.google.com")
            print("    2. Navigate: Billing → Link a billing account to your project")
            print("    3. Navigate: APIs & Services → Enable 'Generative Language API'")
            print("    4. Navigate: IAM → confirm your service account has 'AI Platform User' role")
        else:
            _classify_error(error_str)
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Helper — classify common error codes
# ═══════════════════════════════════════════════════════════════════════════════

def _classify_error(error_str: str) -> None:
    """Print a human-readable explanation for common API errors."""
    s = error_str.lower()
    if "api_key_invalid" in s or "invalid api key" in s:
        _warn("Your API key is invalid or revoked.")
        print("        → Re-generate it at: https://aistudio.google.com/app/apikey")
    elif "403" in s or "permission" in s:
        _warn("Permission denied — check IAM roles and billing.")
    elif "429" in s or "quota" in s or "resource_exhausted" in s:
        _warn("Quota exhausted — wait a minute or upgrade your plan.")
        print("        → Check quotas: console.cloud.google.com/iam-admin/quotas")
    elif "404" in s or "not found" in s:
        _warn("Model or endpoint not found — check the model name.")
    elif "500" in s or "503" in s:
        _warn("Google server error — this is temporary, retry in a moment.")
    elif "timeout" in s or "deadline" in s:
        _warn("Request timed out — check your network or increase timeout.")
    else:
        _warn(f"Unrecognised error type — full message: {error_str}")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 5 — Environment summary
# ═══════════════════════════════════════════════════════════════════════════════

def test_environment_summary() -> None:
    """Print a summary of the detected runtime environment."""
    _section("TEST 5 — Environment Summary")

    key = os.environ.get("GOOGLE_API_KEY", "")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "")

    print(f"  Python version  : {sys.version.split()[0]}")
    print(f"  API key set     : {'Yes' if key else 'No'}")
    print(f"  GCP project     : {project if project else '(not set — using AI Studio mode)'}")
    print(f"  GCP location    : {location if location else '(not set)'}")

    if project:
        _warn("Vertex AI mode detected — ensure Vertex AI API is enabled in GCP.")
    else:
        _pass("AI Studio mode — no GCP project required.")


# ═══════════════════════════════════════════════════════════════════════════════
# Run all tests
# ═══════════════════════════════════════════════════════════════════════════════

def run_all_tests() -> None:
    print("\n" + "═" * 55)
    print("  MULTI-AGENT SYSTEM — API DIAGNOSTICS")
    print("═" * 55)

    results = {}
    results["api_key"]  = test_api_key_present()
    results["api_call"] = test_gemini_call()
    results["quota"]    = test_quota_detection()
    results["billing"]  = test_billing_detection()
    test_environment_summary()

    # ── Final summary ─────────────────────────────────────────────────────────
    _section("SUMMARY")
    all_pass = all(results.values())
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}")

    if all_pass:
        print("\n  🎉  All tests passed! You're ready to run main.py")
    else:
        print("\n  ⚠️   Fix the failing tests above before running main.py")
    print()


if __name__ == "__main__":
    run_all_tests()