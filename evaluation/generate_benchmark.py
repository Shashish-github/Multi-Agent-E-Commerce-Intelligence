"""
Script to generate 100 structured benchmark queries for evaluating the Autonomous Multi-Agent E-Commerce Intelligence Platform.
"""
import json
from pathlib import Path

queries = []

# 1. 30 Laptop Queries (Various budgets, RAM, GPU, Battery, Linux, etc.)
laptop_queries = [
    {"query": "Find a laptop under ₹90,000 for machine learning with at least 16GB RAM and great battery life", "expected_category": "laptop", "expected_budget": 90000, "expected_ram": 16, "has_gpu_pref": True},
    {"query": "Need a lightweight coding laptop below 85k with 16GB RAM and Linux support", "expected_category": "laptop", "expected_budget": 85000, "expected_ram": 16, "has_linux_pref": True},
    {"query": "Best ultrabook under 1 lakh with long battery life and at least 512GB SSD", "expected_category": "laptop", "expected_budget": 100000, "expected_storage": 512, "has_battery_pref": True},
    {"query": "Gaming and ML laptop under 90k with dedicated RTX graphics and 16GB RAM", "expected_category": "laptop", "expected_budget": 90000, "expected_ram": 16, "has_gpu_pref": True},
    {"query": "Affordable student laptop under 70000 with OLED screen and 16GB RAM", "expected_category": "laptop", "expected_budget": 70000, "expected_ram": 16},
    {"query": "Premium business laptop under ₹130,000 with 32GB RAM and top tier build quality", "expected_category": "laptop", "expected_budget": 130000, "expected_ram": 32},
    {"query": "Laptop for video editing under 95k with fast CPU and 16GB RAM", "expected_category": "laptop", "expected_budget": 95000, "expected_ram": 16},
    {"query": "Thin and light ultrabook below 75k with minimum 8 hours battery", "expected_category": "laptop", "expected_budget": 75000, "has_battery_pref": True},
    {"query": "MacBook or Apple laptop under 100k with good battery", "expected_category": "laptop", "expected_budget": 100000, "expected_brand": "Apple"},
    {"query": "ThinkPad or Lenovo laptop under 85000 for backend development", "expected_category": "laptop", "expected_budget": 85000, "expected_brand": "Lenovo"},
    {"query": "Laptop under 80k without Dell with at least 16GB RAM", "expected_category": "laptop", "expected_budget": 80000, "expected_ram": 16, "expected_exclusion": "Dell"},
    {"query": "High performance laptop with RTX GPU and 1TB SSD under 90k", "expected_category": "laptop", "expected_budget": 90000, "expected_storage": 1024, "has_gpu_pref": True},
    {"query": "Linux compatible developer laptop under 90000", "expected_category": "laptop", "expected_budget": 90000, "has_linux_pref": True},
    {"query": "Portable laptop under 70k with at least 16GB RAM for Python programming", "expected_category": "laptop", "expected_budget": 70000, "expected_ram": 16},
    {"query": "Fast laptop for Docker and PyTorch under 90k", "expected_category": "laptop", "expected_budget": 90000, "has_gpu_pref": True},
    {"query": "Lightweight laptop below 80000 with crisp display and 16GB RAM", "expected_category": "laptop", "expected_budget": 80000, "expected_ram": 16},
    {"query": "Laptop under 120000 for heavy data science multitasking with 32GB RAM", "expected_category": "laptop", "expected_budget": 120000, "expected_ram": 32},
    {"query": "Budget friendly ultrabook under 65k with good battery", "expected_category": "laptop", "expected_budget": 65000, "has_battery_pref": True},
    {"query": "ASUS laptop under 90k with 16GB RAM for AI projects", "expected_category": "laptop", "expected_budget": 90000, "expected_ram": 16, "expected_brand": "ASUS"},
    {"query": "Laptop with 14 inch screen, 16GB RAM, under 90000", "expected_category": "laptop", "expected_budget": 90000, "expected_ram": 16},
    {"query": "Notebook with minimum 16GB RAM and 512GB SSD under 85k", "expected_category": "laptop", "expected_budget": 85000, "expected_ram": 16, "expected_storage": 512},
    {"query": "Silent laptop with long battery life under 95k", "expected_category": "laptop", "expected_budget": 95000, "has_battery_pref": True},
    {"query": "Laptop under 90000 with Ubuntu Linux compatibility", "expected_category": "laptop", "expected_budget": 90000, "has_linux_pref": True},
    {"query": "Ultrabook under 80000 with 16GB RAM for university student", "expected_category": "laptop", "expected_budget": 80000, "expected_ram": 16},
    {"query": "Laptop under 100k with 1TB SSD and dedicated graphics", "expected_category": "laptop", "expected_budget": 100000, "expected_storage": 1024, "has_gpu_pref": True},
    {"query": "Travel friendly laptop under 75k with at least 8 hours battery", "expected_category": "laptop", "expected_budget": 75000, "has_battery_pref": True},
    {"query": "High RAM laptop under 130000 with 32GB RAM", "expected_category": "laptop", "expected_budget": 130000, "expected_ram": 32},
    {"query": "Laptop under 85k with great keyboard and durable build quality", "expected_category": "laptop", "expected_budget": 85000},
    {"query": "OLED screen laptop under 70k for media consumption and work", "expected_category": "laptop", "expected_budget": 70000},
    {"query": "Laptop under 90k for deep learning models with CUDA support", "expected_category": "laptop", "expected_budget": 90000, "has_gpu_pref": True}
]

# 2. 25 Smartphone Queries
phone_queries = [
    {"query": "Find a flagship smartphone under 80000 with best camera", "expected_category": "smartphone", "expected_budget": 80000},
    {"query": "Android phone under 90k with 12GB RAM and clean OS", "expected_category": "smartphone", "expected_budget": 90000, "expected_ram": 12},
    {"query": "Google Pixel phone under 85000 for low light photography", "expected_category": "smartphone", "expected_budget": 85000, "expected_brand": "Google"},
    {"query": "Samsung phone under 120000 with stylus and 256GB storage", "expected_category": "smartphone", "expected_budget": 120000, "expected_brand": "Samsung", "expected_storage": 256},
    {"query": "Smartphone under 80k with 5000 mAh battery and fast charging", "expected_category": "smartphone", "expected_budget": 80000},
    {"query": "Mobile under 75000 with 128GB storage and 120Hz display", "expected_category": "smartphone", "expected_budget": 75000, "expected_storage": 128},
    {"query": "Camera phone below 80000 with 50MP sensor", "expected_category": "smartphone", "expected_budget": 80000},
    {"query": "Smartphone under 100k with 12GB RAM for multitasking", "expected_category": "smartphone", "expected_budget": 100000, "expected_ram": 12},
    {"query": "Phone with anti reflective screen under 120k", "expected_category": "smartphone", "expected_budget": 120000},
    {"query": "Premium phone with 7 years OS updates under 80k", "expected_category": "smartphone", "expected_budget": 80000},
    {"query": "Smartphone with great night mode camera under 85k", "expected_category": "smartphone", "expected_budget": 85000},
    {"query": "Smartphone under 125000 with titanium frame", "expected_category": "smartphone", "expected_budget": 125000},
    {"query": "Android mobile under 80000 for AI photography", "expected_category": "smartphone", "expected_budget": 80000},
    {"query": "Phone with 6.7 inch OLED screen under 80k", "expected_category": "smartphone", "expected_budget": 80000},
    {"query": "Smartphone under 90000 with excellent battery endurance", "expected_category": "smartphone", "expected_budget": 90000},
    {"query": "Pixel phone under 80k with stock Android", "expected_category": "smartphone", "expected_budget": 80000, "expected_brand": "Google"},
    {"query": "Smartphone with 12GB RAM and 256GB storage under 120k", "expected_category": "smartphone", "expected_budget": 120000, "expected_ram": 12, "expected_storage": 256},
    {"query": "Best mobile for outdoor visibility under 120k", "expected_category": "smartphone", "expected_budget": 120000},
    {"query": "Phone with triple camera system under 80k", "expected_category": "smartphone", "expected_budget": 80000},
    {"query": "Smartphone under 85000 for video recording and vlogging", "expected_category": "smartphone", "expected_budget": 85000},
    {"query": "Phone with high refresh rate AMOLED display under 80k", "expected_category": "smartphone", "expected_budget": 80000},
    {"query": "Smartphone under 115000 with 5000mAh battery", "expected_category": "smartphone", "expected_budget": 115000},
    {"query": "Smartphone under 80k with computational zoom", "expected_category": "smartphone", "expected_budget": 80000},
    {"query": "Mobile phone under 90k for software developers", "expected_category": "smartphone", "expected_budget": 90000},
    {"query": "Smartphone under 120k with S-Pen support", "expected_category": "smartphone", "expected_budget": 120000}
]

# 3. 25 Monitor Queries
monitor_queries = [
    {"query": "Find a 4K monitor under 60000 for graphic design with USB-C", "expected_category": "monitor", "expected_budget": 60000},
    {"query": "27-inch 4K monitor under 55000 with 90W power delivery", "expected_category": "monitor", "expected_budget": 55000},
    {"query": "Color accurate monitor with 98% DCI-P3 under 60k", "expected_category": "monitor", "expected_budget": 60000},
    {"query": "Dell 4K monitor under 55000 for Mac workstation", "expected_category": "monitor", "expected_budget": 55000, "expected_brand": "Dell"},
    {"query": "IPS Black monitor under 60000 with deep contrast", "expected_category": "monitor", "expected_budget": 60000},
    {"query": "Monitor under 55k with built in USB hub and ethernet", "expected_category": "monitor", "expected_budget": 55000},
    {"query": "27 inch screen for programming and multitasking under 60k", "expected_category": "monitor", "expected_budget": 60000},
    {"query": "4K display under 55000 with single cable laptop charging", "expected_category": "monitor", "expected_budget": 55000},
    {"query": "Monitor for photo editing under 60000 with sRGB 100%", "expected_category": "monitor", "expected_budget": 60000},
    {"query": "UHD monitor under 55k with adjustable ergonomic stand", "expected_category": "monitor", "expected_budget": 55000},
    {"query": "27 inch monitor under 60k with USB Type C 90W PD", "expected_category": "monitor", "expected_budget": 60000},
    {"query": "4K productivity screen under 55000 for software engineer", "expected_category": "monitor", "expected_budget": 55000},
    {"query": "Monitor under 60k with high contrast and wide viewing angles", "expected_category": "monitor", "expected_budget": 60000},
    {"query": "UltraSharp monitor under 55000 with factory color calibration", "expected_category": "monitor", "expected_budget": 55000},
    {"query": "Display under 60000 for dual monitor setup with daisy chaining", "expected_category": "monitor", "expected_budget": 60000},
    {"query": "4K monitor under 55k with HDR support", "expected_category": "monitor", "expected_budget": 55000},
    {"query": "Office monitor under 55000 with USB hub and KVM switch", "expected_category": "monitor", "expected_budget": 55000},
    {"query": "27 inch 4K display under 60000 for video color grading", "expected_category": "monitor", "expected_budget": 60000},
    {"query": "Monitor with anti glare screen and 4K resolution under 55k", "expected_category": "monitor", "expected_budget": 55000},
    {"query": "Dell UltraSharp 27 inch under 55000", "expected_category": "monitor", "expected_budget": 55000, "expected_brand": "Dell"},
    {"query": "High resolution 4K screen under 60000 for coding", "expected_category": "monitor", "expected_budget": 60000},
    {"query": "Monitor with USB-C 90W charging under 55000", "expected_category": "monitor", "expected_budget": 55000},
    {"query": "27 inch IPS display under 55k with 4K clarity", "expected_category": "monitor", "expected_budget": 55000},
    {"query": "Studio monitor under 60000 for graphic artists", "expected_category": "monitor", "expected_budget": 60000},
    {"query": "USB-C monitor under 55000 for clean desk setup", "expected_category": "monitor", "expected_budget": 55000}
]

# 4. 20 Audio & Edge Case Queries
audio_and_edge_queries = [
    {"query": "Noise cancelling headphones under 30000 with long battery", "expected_category": "audio", "expected_budget": 30000},
    {"query": "Wireless audio earbuds under 20k with ANC and transparency mode", "expected_category": "audio", "expected_budget": 20000},
    {"query": "Studio monitor speakers under 40000 for home recording", "expected_category": "audio", "expected_budget": 40000},
    {"query": "Over ear headphones under 25k with multipoint bluetooth", "expected_category": "audio", "expected_budget": 25000},
    {"query": "Audiophile headphones under 35000 with deep bass", "expected_category": "audio", "expected_budget": 35000},
    {"query": "Headphones with 30 hours battery under 25000", "expected_category": "audio", "expected_budget": 25000},
    {"query": "Wireless earphones under 15k for workout and running", "expected_category": "audio", "expected_budget": 15000},
    {"query": "Premium sound audio headset under 30k", "expected_category": "audio", "expected_budget": 30000},
    {"query": "Noise cancelling earbuds under 20000 for travel", "expected_category": "audio", "expected_budget": 20000},
    {"query": "Audio headphones under 28k with LDAC codec support", "expected_category": "audio", "expected_budget": 28000},
    # Ambiguous & Edge Case Queries
    {"query": "laptop with good screen", "expected_category": "laptop", "is_ambiguous": True},
    {"query": "best smartphone", "expected_category": "smartphone", "is_ambiguous": True},
    {"query": "cheap programming machine", "expected_category": "laptop", "is_ambiguous": True},
    {"query": "laptop under 90k without Lenovo and no HP", "expected_category": "laptop", "expected_budget": 90000, "expected_exclusion": "Lenovo"},
    {"query": "Find a device under 80000 with 16GB RAM for ML", "expected_category": "laptop", "expected_budget": 80000, "expected_ram": 16},
    {"query": "Need a powerful machine under 90000", "expected_category": "laptop", "expected_budget": 90000, "is_ambiguous": True},
    {"query": "4K display", "expected_category": "monitor", "is_ambiguous": True},
    {"query": "phone with best battery life", "expected_category": "smartphone", "is_ambiguous": True},
    {"query": "laptop for university student under 70k with 16GB RAM", "expected_category": "laptop", "expected_budget": 70000, "expected_ram": 16},
    {"query": "lightweight developer machine under 85k with Linux", "expected_category": "laptop", "expected_budget": 85000, "has_linux_pref": True}
]

all_queries = laptop_queries + phone_queries + monitor_queries + audio_and_edge_queries
out_path = Path(__file__).parent / "benchmark_dataset.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(all_queries, f, indent=2)

print(f"Generated {len(all_queries)} benchmark queries in {out_path}")
