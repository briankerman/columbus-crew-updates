import os
from datetime import datetime
import anthropic
import sendgrid
from sendgrid.helpers.mail import Mail

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
SENDGRID_API_KEY  = os.environ["SENDGRID_API_KEY"]
FROM_EMAIL        = os.environ["FROM_EMAIL"]
TO_EMAIL          = os.environ["TO_EMAIL"]

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

Then write a digest with these four sections — plain text, no markdown symbols, 
no bullet dashes, just clean sentences:

WHERE WE STAND
One punchy paragraph on their position in the table and overall form.

RECENT RESULTS
A sentence or two on each recent result — score, opponent, quick take.

WHAT TO WATCH
Preview the next game or two with any relevant context.

BOTTOM LINE
One sentence overall vibe check on the season.

Keep it under 350 words. Write like a beat reporter, not a press release.
"""
        }]
    )

    # Extract the text response (web search results are also in content blocks)
    text = ""
    for block in msg.content:
        if hasattr(block, "text"):
            text += block.text

    return text


def send_email(digest_text):
    today = datetime.now().strftime("%B %-d, %Y")
    subject = f"⚽ Columbus Crew Weekly Update — {today}"

    html = f"""
    <html>
    <body style="font-family: Georgia, serif; max-width: 600px; margin: 40px auto;
                 color: #1a1a1a; line-height: 1.75;">
      <div style="background:#FCD116; padding:20px 28px; border-radius:8px 8px 0 0;">
        <h1 style="margin:0; font-size:22px; color:#1a1a1a;">⚽ Columbus Crew Weekly Digest</h1>
        <p style="margin:4px 0 0; font-size:13px; color:#333;">{today}</p>
      </div>
      <div style="background:#fff; border:1px solid #e0e0e0; border-top:none;
                  padding:28px; border-radius:0 0 8px 8px; white-space:pre-wrap;
                  font-size:15px;">
{digest_text}
      </div>
      <p style="font-size:11px; color:#999; text-align:center; margin-top:16px;">
        Automated via GitHub Actions + Claude API
      </p>
    </body>
    </html>
    """

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
    digest = generate_digest()
    print("\n--- DIGEST ---")
    print(digest)
    print("\nSending email...")
    send_email(digest)
    print("Done ✓")
