"""Hormozi creative framework for Stock Alarm.

Implements:
  - StockAlarmAngleMatrix: the 6-angle × 5-hook = 30-creative brief matrix
  - GSOBuilder: Grand Slam Offer generator using the Value Equation

Reference: Plan Phase 1/2 — produce 30 creative briefs covering 6 distinct
emotional angles, each with 5 different opening hooks. This gives Meta's
Andromeda algorithm 30 independent signals to find the buyer pattern.
"""

from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class CreativeBrief:
    """Single creative brief: one angle + one hook = one ad set."""
    angle_id: int
    hook_id: int
    angle_name: str
    angle_description: str
    hook_text: str
    hook_format: str          # talking_head | text_overlay | silent_visual | ugc | notification
    hook_opening: str         # exact first line / visual description
    body_points: List[str]    # 2-3 persuasion points for the ad body
    cta_text: str
    ad_set_name: str          # pre-formatted name for Meta Ads Manager


# ── The 6 Angles ──────────────────────────────────────────────────────────────
# Each angle is a distinct emotional argument. Same product, different story.
# Spread across: Fear, Identity, Transformation, Enemy, Cost Framing, Social Proof.

ANGLES = [
    {
        "id": 1,
        "name": "Fear / Miss",
        "core_argument": (
            "You're finding out about major price moves hours after they happen — "
            "the same day you check your brokerage app. That gap is costing you."
        ),
        "emotional_driver": "fear of missing out / regret",
        "body_points": [
            "Most retail investors check their portfolio after the move already happened",
            "Institutional traders have automated systems — you don't have to be left out",
            "Stock Alarm fires the moment your trigger is hit, not when you happen to look",
        ],
        "cta_text": "Set your first alert free",
    },
    {
        "id": 2,
        "name": "Identity / Serious Investor",
        "core_argument": (
            "Serious investors don't let price moves catch them off guard. "
            "They have systems. You can too."
        ),
        "emotional_driver": "identity / aspiration",
        "body_points": [
            "Professionals don't watch charts all day — they set alerts and get notified",
            "47,000+ investors already use Stock Alarm as their market radar",
            "One alert setup takes 90 seconds. What you do with the signal is up to you.",
        ],
        "cta_text": "Join 47,000 investors",
    },
    {
        "id": 3,
        "name": "Before / After Transformation",
        "core_argument": (
            "Before Stock Alarm: constantly checking prices, missing moves, "
            "stress-watching tickers. After: alerts fire when your criteria hit, "
            "you act on information not anxiety."
        ),
        "emotional_driver": "transformation / relief",
        "body_points": [
            "Before: phone open every 20 minutes checking if anything moved",
            "After: one notification at exactly the price you care about",
            "90-second setup. Free trial. Cancel anytime.",
        ],
        "cta_text": "Try it free for 7 days",
    },
    {
        "id": 4,
        "name": "Enemy / Brokerage Failure",
        "core_argument": (
            "Your brokerage app isn't going to alert you when it matters. "
            "They want you checking manually — it keeps you engaged with their platform. "
            "You need your own system."
        ),
        "emotional_driver": "enemy / betrayal / control",
        "body_points": [
            "Brokerage alerts are basic, delayed, and designed around their UX not your trades",
            "Stock Alarm monitors 13 alert types: price, volume, RSI, earnings, news breaks, and more",
            "Your alerts, your rules, instant delivery — not whenever Fidelity decides to send it",
        ],
        "cta_text": "Take control of your alerts",
    },
    {
        "id": 5,
        "name": "Cost Framing / ROI",
        "core_argument": (
            "Missing one significant move costs more than a year's subscription. "
            "Stock Alarm pays for itself the first time you actually catch a breakout."
        ),
        "emotional_driver": "loss aversion / logical ROI",
        "body_points": [
            "One alert on a 10% move in a $1,000 position = $100. Annual plan = $99.",
            "You don't need to win every trade — you need to stop missing the ones you were watching",
            "Free 7-day trial. If you don't catch at least one move worth the price, cancel.",
        ],
        "cta_text": "Start free — see what you've been missing",
    },
    {
        "id": 6,
        "name": "Social Proof / Real Alerts",
        "core_argument": (
            "47,000 investors got this alert at 8:47 AM last Tuesday. "
            "Here's what the price did by noon. Real alerts, real moves."
        ),
        "emotional_driver": "social proof / FOMO / specificity",
        "body_points": [
            "Screenshot of real alert + real price action (use actual recent example)",
            "47,000+ active users. 4.8 stars on the App Store.",
            "They're not smarter than you — they just get notified first.",
        ],
        "cta_text": "See what they're getting alerted to",
    },
]

# ── The 5 Hooks per Angle ──────────────────────────────────────────────────────
# Hook = first 3-5 seconds. Same angle body, five different doors into it.
# Each hook differs on at least two of: format, opening line, visual style.

HOOKS_PER_ANGLE = {
    1: [  # Fear / Miss
        {
            "id": "A",
            "format": "text_overlay",
            "opening": "You missed a 30% move last month. Here's why it won't happen again.",
            "visual": "Dramatic price chart, green candle spike, counter showing % gain",
        },
        {
            "id": "B",
            "format": "talking_head",
            "opening": "Most retail investors find out about big moves hours after they happen.",
            "visual": "Direct to camera, frustrated expression, then phone notification",
        },
        {
            "id": "C",
            "format": "silent_visual",
            "opening": "[No voiceover] — price chart running in real time. Text: 'Did you catch this?'",
            "visual": "Real stock chart, candle by candle, then freeze on breakout moment",
        },
        {
            "id": "D",
            "format": "notification",
            "opening": "[Phone notification sound] — Stock Alarm: $NVDA hit your $500 target.",
            "visual": "Phone lock screen, notification appears, tap to open, price shown",
        },
        {
            "id": "E",
            "format": "ugc",
            "opening": "I missed a $4,000 gain last year because I wasn't watching. Never again.",
            "visual": "Casual, selfie-style video, authentic frustration, then phone showing alert",
        },
    ],
    2: [  # Identity / Serious Investor
        {
            "id": "A",
            "format": "text_overlay",
            "opening": "Serious investors don't watch charts all day. They set alerts.",
            "visual": "Split screen: stressed person watching screen vs. calm person getting notification",
        },
        {
            "id": "B",
            "format": "talking_head",
            "opening": "If you're refreshing your brokerage app every 20 minutes, there's a better way.",
            "visual": "Direct to camera, confident, then shows clean app UI",
        },
        {
            "id": "C",
            "format": "silent_visual",
            "opening": "[Text only] — What separates retail investors from the ones who actually make money.",
            "visual": "Bold text animation, then reveal: 'They have alerts. You don't.'",
        },
        {
            "id": "D",
            "format": "notification",
            "opening": "This is what 47,000 investors see every morning before the market opens.",
            "visual": "App home screen with multiple active alerts, clean UI",
        },
        {
            "id": "E",
            "format": "ugc",
            "opening": "I used to think I had to be glued to my screen to be a good investor.",
            "visual": "Authentic creator, shows before/after of their workflow with the app",
        },
    ],
    3: [  # Before / After Transformation
        {
            "id": "A",
            "format": "text_overlay",
            "opening": "Before: checking your portfolio 10× a day. After: one notification when it matters.",
            "visual": "Before/after split with phone screen comparisons",
        },
        {
            "id": "B",
            "format": "talking_head",
            "opening": "I used to have anxiety every time I opened my brokerage app.",
            "visual": "Direct to camera, relatable stress → then calm after showing the app",
        },
        {
            "id": "C",
            "format": "silent_visual",
            "opening": "[Text] — How I stopped watching the market. And started trading better.",
            "visual": "Calm lifestyle footage, phone buzzes with alert, person checks and acts",
        },
        {
            "id": "D",
            "format": "notification",
            "opening": "Setup takes 90 seconds. Then you stop refreshing apps forever.",
            "visual": "Screen recording of 90-second setup flow in the app",
        },
        {
            "id": "E",
            "format": "ugc",
            "opening": "My trading improved the moment I stopped trying to watch everything.",
            "visual": "Creator shows phone with alerts configured, explains their system",
        },
    ],
    4: [  # Enemy / Brokerage Failure
        {
            "id": "A",
            "format": "text_overlay",
            "opening": "Your brokerage app alerts are not enough. Here's why.",
            "visual": "Side-by-side: generic brokerage alert vs. Stock Alarm's detailed alert",
        },
        {
            "id": "B",
            "format": "talking_head",
            "opening": "I trusted Robinhood's alerts for two years. Then I realized what I was missing.",
            "visual": "Direct to camera, builds case against basic broker alerts",
        },
        {
            "id": "C",
            "format": "silent_visual",
            "opening": "[Text] — What your brokerage doesn't tell you (and when).",
            "visual": "Clock showing time delay between event and broker notification",
        },
        {
            "id": "D",
            "format": "notification",
            "opening": "13 alert types. Your brokerage has 2. Here's the difference.",
            "visual": "List animation showing all 13 alert types Stock Alarm supports",
        },
        {
            "id": "E",
            "format": "ugc",
            "opening": "The day I stopped using Fidelity's alerts and built my own system.",
            "visual": "Creator story, authentic frustration with basic alerts, app as solution",
        },
    ],
    5: [  # Cost Framing / ROI
        {
            "id": "A",
            "format": "text_overlay",
            "opening": "One alert. One move. Paid for a year.",
            "visual": "Bold math on screen: $100 gain vs $99/year cost",
        },
        {
            "id": "B",
            "format": "talking_head",
            "opening": "Let's do the math. Missing one 10% move on $1,000 costs you $100. Annual plan is $99.",
            "visual": "Direct to camera, walks through the ROI math clearly",
        },
        {
            "id": "C",
            "format": "silent_visual",
            "opening": "[Text] — The most expensive thing you can do is miss a move you were watching.",
            "visual": "Opportunity cost visualization — missed gain vs. subscription cost",
        },
        {
            "id": "D",
            "format": "notification",
            "opening": "This alert fired at 9:31 AM. The position was up 8% by 10 AM.",
            "visual": "Real alert screenshot + real price chart from that morning",
        },
        {
            "id": "E",
            "format": "ugc",
            "opening": "I calculated how much money I lost missing alerts before I used this app.",
            "visual": "Creator does honest cost calculation of missed trades, lands on app as solution",
        },
    ],
    6: [  # Social Proof / Real Alerts
        {
            "id": "A",
            "format": "text_overlay",
            "opening": "47,000 investors got this alert at 8:47 AM on Tuesday.",
            "visual": "Real alert screenshot with timestamp, then price chart showing what happened",
        },
        {
            "id": "B",
            "format": "talking_head",
            "opening": "I want to show you a real alert that fired last week and what happened after.",
            "visual": "Screen share of real alert, walks through price action",
        },
        {
            "id": "C",
            "format": "silent_visual",
            "opening": "[Text] — What 47,000 investors saw before the market opened this morning.",
            "visual": "App feed of real alerts, then cut to price charts confirming moves",
        },
        {
            "id": "D",
            "format": "notification",
            "opening": "4.8 stars. 47,000 users. This is what they're getting alerted to.",
            "visual": "App Store rating + review montage + real alert examples",
        },
        {
            "id": "E",
            "format": "ugc",
            "opening": "I've been using Stock Alarm for 6 months. Here are the alerts that mattered most.",
            "visual": "Creator shows real alert history from their account, authentic testimonial",
        },
    ],
}


class StockAlarmAngleMatrix:
    """The 6×5 creative brief matrix for Stock Alarm.

    Usage:
        matrix = StockAlarmAngleMatrix()
        briefs = matrix.get_all_briefs()          # all 30
        brief = matrix.get_brief(angle_id=1, hook_id="A")
        names = matrix.get_ad_set_names()         # for Meta Ads Manager
    """

    def __init__(self):
        self._briefs = self._build_briefs()

    def _build_briefs(self) -> List[CreativeBrief]:
        briefs = []
        for angle in ANGLES:
            for hook in HOOKS_PER_ANGLE[angle["id"]]:
                ad_set_name = (
                    f"SA | A{angle['id']} {angle['name'][:12]} | H{hook['id']} {hook['format'][:8]}"
                )
                briefs.append(CreativeBrief(
                    angle_id=angle["id"],
                    hook_id=hook["id"],
                    angle_name=angle["name"],
                    angle_description=angle["core_argument"],
                    hook_text=hook["opening"],
                    hook_format=hook["format"],
                    hook_opening=hook["opening"],
                    body_points=angle["body_points"],
                    cta_text=angle["cta_text"],
                    ad_set_name=ad_set_name,
                ))
        return briefs

    def get_all_briefs(self) -> List[CreativeBrief]:
        return self._briefs

    def get_brief(self, angle_id: int, hook_id: str) -> CreativeBrief:
        for brief in self._briefs:
            if brief.angle_id == angle_id and brief.hook_id == hook_id:
                return brief
        raise ValueError(f"Brief not found: angle={angle_id}, hook={hook_id}")

    def get_by_angle(self, angle_id: int) -> List[CreativeBrief]:
        return [b for b in self._briefs if b.angle_id == angle_id]

    def get_ad_set_names(self) -> List[str]:
        return [b.ad_set_name for b in self._briefs]

    def to_dict(self) -> List[Dict]:
        result = []
        for b in self._briefs:
            result.append({
                "angle_id": b.angle_id,
                "hook_id": b.hook_id,
                "angle_name": b.angle_name,
                "hook_format": b.hook_format,
                "hook_opening": b.hook_opening,
                "body_points": b.body_points,
                "cta_text": b.cta_text,
                "ad_set_name": b.ad_set_name,
            })
        return result

    def summary(self) -> str:
        lines = [f"Stock Alarm Creative Matrix: {len(self._briefs)} briefs\n"]
        for angle in ANGLES:
            hooks = self.get_by_angle(angle["id"])
            lines.append(f"Angle {angle['id']}: {angle['name']}")
            lines.append(f"  Argument: {angle['core_argument'][:80]}...")
            for b in hooks:
                lines.append(f"  Hook {b.hook_id} [{b.hook_format:15s}] — {b.hook_opening[:60]}...")
            lines.append("")
        return "\n".join(lines)


# ── Grand Slam Offer Builder ───────────────────────────────────────────────────

class GSOBuilder:
    """Generates the Grand Slam Offer for Stock Alarm.

    Applies Hormozi's Value Equation:
        Value = (Dream Outcome × Perceived Likelihood) / (Time Delay × Effort)

    Maximizes numerator (outcome + belief) and minimizes denominator
    (speed + simplicity) to build the offer stack.
    """

    OFFER_COMPONENTS = {
        "core": {
            "name": "Stock Alarm Pro — All Alert Types",
            "description": (
                "Every alert type unlocked: price targets, volume spikes, RSI crossings, "
                "earnings calendar, breaking news, 52-week highs/lows, moving average "
                "crosses, and more. Unlimited alerts on unlimited tickers."
            ),
            "value_delivered": "Never miss a move you were watching",
        },
        "fast_start_bonus": {
            "name": "Pre-Built Alert Templates for Top 20 Stocks",
            "description": (
                "Instant value on day one — pre-configured alerts for the 20 most-watched "
                "tickers (AAPL, NVDA, TSLA, SPY, QQQ, and more). Import in one tap."
            ),
            "perceived_value": "$0 extra — included in trial",
        },
        "education_layer": {
            "name": "What Each Alert Type Means + When to Look",
            "description": (
                "Short in-app guide: what RSI alerts signal, when volume spikes matter, "
                "how to interpret earnings alerts. Reduces the effort of acting on signals."
            ),
            "perceived_value": "Reduces learning curve to minutes",
        },
        "risk_reversal": {
            "name": "7-Day Free Trial — No Credit Card Required",
            "description": (
                "Full access to every feature for 7 days. No card at signup. "
                "Cancel in the app with one tap. Zero risk."
            ),
            "objection_handled": "What if it doesn't work for me?",
        },
        "social_proof": {
            "name": "47,000+ Active Investors + 4.8-Star Rating",
            "description": (
                "Join 47,000 investors who get alerted before they check their brokerage. "
                "4.8 stars on the App Store from thousands of real reviews."
            ),
            "objection_handled": "Does this actually work?",
        },
    }

    VALUE_EQUATION = {
        "dream_outcome": (
            "Know about significant price moves the moment they happen — before you would "
            "have checked manually. Never again find out about a move you were watching "
            "hours after it started."
        ),
        "perceived_likelihood": [
            "47,000 active users — they're getting alerted right now",
            "Real alert screenshots with real price action timestamps",
            "4.8-star App Store rating from thousands of real investors",
            "Specific: 'Our users got the $NVDA alert at 8:47 AM on Tuesday'",
        ],
        "time_delay": (
            "First alert fires within hours of setup. 90-second onboarding. "
            "Pre-built templates mean zero configuration for the first 20 tickers."
        ),
        "effort_sacrifice": (
            "Set up in 90 seconds. No manual watching required. "
            "The app does the monitoring — you act on the notification."
        ),
    }

    COMPLIANCE_NOTES = [
        "Frame outcomes as information access, NOT financial returns",
        "NEVER show P&L screenshots or imply the app generates profits",
        "NEVER say 'buy' or 'sell' signals — say 'alerts' and 'notifications'",
        "Social proof: use subscriber count and ratings, NOT trading performance",
        "Approved framing: 'Know when to look' / 'Never miss a move you were watching'",
        "Avoid: 'Make money' / 'Beat the market' / 'Guaranteed gains'",
    ]

    def get_offer_stack(self) -> Dict:
        return {
            "offer_components": self.OFFER_COMPONENTS,
            "value_equation": self.VALUE_EQUATION,
            "compliance_notes": self.COMPLIANCE_NOTES,
        }

    def get_headline_variants(self) -> List[str]:
        """Pre-written GSO headlines for ad copy (Meta 40-char limit)."""
        return [
            "Never Miss a Move Again",           # 24 chars
            "Your Stock Alerts, Upgraded",       # 29 chars
            "Know Before Your Brokerage Does",   # 33 chars (slightly over — use shorter)
            "47,000 Investors Can't Be Wrong",   # 32 chars
            "Set Alerts. Stop Watching.",         # 26 chars
            "One Alert Can Pay the Year",         # 27 chars
            "Stop Refreshing. Start Alerting.",  # 33 chars
        ]

    def get_primary_text_variants(self) -> List[str]:
        """Pre-written primary text (125-char limit)."""
        return [
            "Find out about major moves the moment they happen — not hours later. 90-second setup. Free trial.",
            "47,000 investors get alerted before they check their brokerage. Join them free for 7 days.",
            "One alert pays for a year. 13 alert types, unlimited tickers. Try free — no card needed.",
            "Stop missing moves you were watching. Set your first alert in 90 seconds. Cancel anytime.",
            "Your brokerage tells you after the fact. Stock Alarm tells you when it happens. Try free.",
        ]

    def get_cta_options(self) -> List[str]:
        """Best-performing CTA types for financial subscription apps."""
        return ["LEARN_MORE", "SIGN_UP", "DOWNLOAD", "GET_QUOTE"]

    def summary(self) -> str:
        lines = ["=== Stock Alarm Grand Slam Offer ===\n"]
        lines.append("VALUE EQUATION:")
        lines.append(f"  Dream Outcome: {self.VALUE_EQUATION['dream_outcome'][:100]}...")
        lines.append(f"  Time to Value: {self.VALUE_EQUATION['time_delay']}")
        lines.append(f"  Effort: {self.VALUE_EQUATION['effort_sacrifice']}")
        lines.append("\nOFFER STACK:")
        for key, comp in self.OFFER_COMPONENTS.items():
            lines.append(f"  {comp['name']}")
        lines.append("\nCOMPLIANCE (Meta Financial Ad Policy):")
        for note in self.COMPLIANCE_NOTES:
            lines.append(f"  - {note}")
        return "\n".join(lines)
