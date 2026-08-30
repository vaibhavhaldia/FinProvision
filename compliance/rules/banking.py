"""Banking compliance rules — SOX, PCI-DSS, RBI."""
from compliance.rules.secrets import Rule

BANKING_RULES: list[Rule] = [
    Rule(r'(?i)(net_revenue|gross_profit|ebitda|net_pnl)\s*=\s*\d', "HIGH", "TF-SOX-001", "Hardcoded financial figure — SOX audit risk"),
    Rule(r'(?i)(print|logger\.(info|warning|error|debug)|logging\.(info|warning))\s*\(.*card', "CRITICAL", "TF-PCI-001", "Card data in print/log statement"),
    Rule(r'settlement_amount\s*=\s*\d+\s*$', "MEDIUM", "TF-RBI-001", "Untraced settlement amount (RBI T+1)"),
    Rule(r'(?i)account_?number\s*[=:]\s*["\']?\d{9,18}["\']?', "CRITICAL", "TF-PCI-002", "Hardcoded account number"),
    Rule(r'(?i)(cvv|cvv2|cvc|cvc2)\s*[=:]\s*["\']?\d{3,4}["\']?', "CRITICAL", "TF-PCI-003", "Hardcoded CVV/CVC"),
    Rule(r'(?i)#\s*(todo|fixme|hack)\s*.*?(auth|security|token|bypass)', "HIGH", "TF-SOX-002", "Security bypass TODO in code"),
]