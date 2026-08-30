"""PII detection rules."""
from compliance.rules.secrets import Rule

PII_RULES: list[Rule] = [
    Rule(r'\b4[0-9]{15}\b', "CRITICAL", "TF-PII-001", "Potential Visa PAN (card number)"),
    Rule(r'\b5[1-5][0-9]{14}\b', "CRITICAL", "TF-PII-002", "Potential Mastercard PAN"),
    Rule(r'\b3[47][0-9]{13}\b', "CRITICAL", "TF-PII-003", "Potential Amex PAN"),
    Rule(r'\b\d{3}-\d{2}-\d{4}\b', "CRITICAL", "TF-PII-004", "Potential SSN"),
    Rule(r'(?i)iban\s*[:=]\s*[A-Z]{2}\d{2}[A-Z0-9]{4,30}', "CRITICAL", "TF-PII-005", "IBAN detected"),
    Rule(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', "HIGH", "TF-PII-006", "Email address in code"),
    Rule(r'[a-zA-Z0-9.\-_]{2,256}@(?:okaxis|oksbi|okicici|okhdfc|upi|ybl|ibl|axl|paytm|freecharge|apl|waaxis|waksbi)[a-zA-Z0-9]*', "HIGH", "TF-PII-007", "Virtual Payment Address (VPA)"),
    Rule(r'\b[2-9][0-9]{9}\b', "MEDIUM", "TF-PII-008", "Potential Indian mobile number"),
]