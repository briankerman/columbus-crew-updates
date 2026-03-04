import os
from datetime import datetime
import anthropic
import sendgrid
from sendgrid.helpers.mail import Mail

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
SENDGRID_API_KEY  = os.environ["SENDGRID_API_KEY"]
FROM_EMAIL        = os.environ["FROM_EMAIL"]
TO_EMAIL          = os.environ["TO_EMAIL"]

# Official Columbus Crew crest from their CDN
CREW_LOGO_URL = "https://upload.wikimedia.org/wikipedia/en/thumb/9/9e/Columbus_Crew_logo_2021.svg/336px-Columbus_Crew_logo_2021.svg.png"

def generate_digest():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = datetime.now().strftime("%B %-d, %Y")

    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"""
Today is {today}. Search for the latest Columbus Crew MLS news and write a
weekly digest for a fan.

Search for:
1. Columbus Crew recent match results (last 2-3 games with scores)
2. Columbus Crew upcoming fixtures
3. Current MLS Eastern Conference standings
4. Any notable Crew news (injuries, transfers, form)

Return your response as ONLY the following HTML snippet — no preamble, no explanation,
just the HTML between the markers. Use this exact structure:

<!--START-->
<div class="section">
  <div class="section-title">Where We Stand</div>
  <p>One punchy paragraph on their position in the table and overall form.</p>
</div>

<div class="section">
  <div class="section-title">Recent Results</div>
  <div class="result">
    <span class="match">Columbus Crew 2–1 Opponent</span>
    <span class="result-tag win">WIN</span>
  </div>
  <p class="result-note">One sentence takeaway on the game.</p>
  <!-- repeat for each recent result, use class="result-tag loss" for losses, "result-tag draw" for draws -->
</div>

<div class="section">
  <div class="section-title">What To Watch</div>
  <p>Preview of next game or two with relevant context.</p>
</div>

<div class="section">
  <div class="section-title">Bottom Line</div>
  <p>One sentence overall vibe check on the season.</p>
</div>
<!--END-->

Write like a beat reporter, not a press release. Under 350 words total.
"""
        }]
    )

    # Extract text from response
    full_text = ""
    for block in msg.content:
        if hasattr(block, "text"):
            full_text += block.text

    # Pull out just the HTML between the markers
    if "<!--START-->" in full_text and "<!--END-->" in full_text:
        start = full_text.index("<!--START-->") + len("<!--START-->")
        end = full_text.index("<!--END-->")
        return full_text[start:end].strip()
    else:
        # Fallback: return raw text wrapped in a paragraph
        return f"<div class='section'><p>{full_text}</p></div>"


def send_email(digest_html):
    today = datetime.now().strftime("%B %-d, %Y")
    subject = f"⚽ Columbus Crew Weekly Digest — {today}"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{
    margin: 0; padding: 0;
    background-color: #f0f0f0;
    font-family: 'Helvetica Neue', Arial, sans-serif;
  }}
  .wrapper {{
    max-width: 600px;
    margin: 32px auto;
    background: #ffffff;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.12);
  }}

  /* Header */
  .header {{
    background-color: #FCD116;
    padding: 28px 32px 20px;
    display: flex;
    align-items: center;
    gap: 18px;
  }}
  .header img {{
    width: 64px;
    height: 64px;
    object-fit: contain;
  }}
  .header-text h1 {{
    margin: 0 0 4px;
    font-size: 22px;
    font-weight: 800;
    color: #111111;
    letter-spacing: -0.3px;
  }}
  .header-text p {{
    margin: 0;
    font-size: 13px;
    color: #444444;
    font-weight: 500;
  }}

  /* Black bar */
  .subheader {{
    background: #111111;
    padding: 9px 32px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #FCD116;
  }}

  /* Body */
  .body {{
    padding: 28px 32px 8px;
  }}

  .section {{
    margin-bottom: 24px;
  }}

  .section-title {{
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: #FCD116;
    background: #111111;
    display: inline-block;
    padding: 4px 10px;
    border-radius: 3px;
    margin-bottom: 10px;
  }}

  p {{
    margin: 0 0 10px;
    font-size: 15px;
    line-height: 1.75;
    color: #222222;
  }}

  /* Result rows */
  .result {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
  }}
  .match {{
    font-size: 15px;
    font-weight: 700;
    color: #111111;
  }}
  .result-tag {{
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
    padding: 2px 7px;
    border-radius: 3px;
    text-transform: uppercase;
  }}
  .win  {{ background: #d4edda; color: #155724; }}
  .loss {{ background: #f8d7da; color: #721c24; }}
  .draw {{ background: #fff3cd; color: #856404; }}
  .result-note {{
    font-size: 14px;
    color: #555555;
    margin: 0 0 14px;
    padding-left: 0;
  }}

  /* Divider */
  .divider {{
    border: none;
    border-top: 1px solid #eeeeee;
    margin: 4px 0 24px;
  }}

  /* Footer */
  .footer {{
    background: #111111;
    padding: 16px 32px;
    text-align: center;
    font-size: 11px;
    color: #777777;
    letter-spacing: 0.3px;
  }}
  .footer span {{ color: #FCD116; font-weight: 600; }}
</style>
</head>
<body>
<div class="wrapper">

  <div class="header">
    <img src="{CREW_LOGO_URL}" alt="Columbus Crew">
    <div class="header-text">
      <h1>Columbus Crew Weekly Digest</h1>
      <p>{today}</p>
    </div>
  </div>

  <div class="subheader">MLS 2026 Season Update</div>

  <div class="body">
    {digest_html}
  </div>

  <div class="footer">
    Automated weekly update &nbsp;·&nbsp; <span>Crew</span> nation forever
  </div>

</div>
</body>
</html>"""

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject=subject,
        html_content=html,
    )
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    response = sg.send(message)
    print(f"Email sent — status {response.status_code}")


if __name__ == "__main__":
    print("Asking Claude for Crew update...")
    digest_html = generate_digest()
    print("\n--- DIGEST HTML ---")
    print(digest_html)
    print("\nSending email...")
    send_email(digest_html)
    print("Done ✓")
