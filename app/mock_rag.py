from __future__ import annotations

import time

from .incidents import STATE
from .tracing import observe

CORPUS = {
    "paracetamol": ["Paracetamol (hay acetaminophen) là thuốc giảm đau, hạ sốt. Không nên dùng chung với Efferalgan do có cùng hoạt chất gây quá liều."],
    "hồ sơ": ["Hồ sơ bệnh án được bảo mật chặt chẽ. Bạn cần đến trực tiếp quầy để xác minh danh tính."],
    "sốt": ["Sốt trên 38.5 độ C cần dùng thuốc hạ sốt theo cân nặng và lau mát. Nên đưa đến viện nếu không hạ."],
    "dạ dày": ["Omeprazole là thuốc ức chế bơm proton. Tác dụng phụ: nhức đầu, buồn nôn."],
    "tương tác": ["Một số thuốc giảm đau NSAID có thể gây tương tác xấu với kháng sinh nhóm Quinolone."],
}


@observe(as_type="generation")
def retrieve(message: str) -> list[str]:
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)
    lowered = message.lower()
    for key, docs in CORPUS.items():
        if key in lowered:
            return docs
    return ["No domain document matched. Use general fallback answer."]