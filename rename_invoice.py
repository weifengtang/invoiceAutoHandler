#!/usr/bin/env python3
# rename_invoice.py
# 自动分类、提取日期金额、重命名发票

import os
import re
import sys
import time
import json
import hashlib
import pdfplumber

# 配置和日志文件路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(SCRIPT_DIR, "settings.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "invoice_log.json")

# 全局配置
SETTINGS = {}

def load_settings():
    """加载配置文件"""
    global SETTINGS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                SETTINGS = json.load(f)
        except:
            SETTINGS = get_default_settings()
    else:
        SETTINGS = get_default_settings()
    return SETTINGS

def get_default_settings():
    """默认配置"""
    return {
        "default_directory": "./",
        "categories": {},
        "default_category": "其他"
    }

def load_log():
    """加载处理日志"""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_log(log):
    """保存处理日志"""
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def get_file_id(pdf_path):
    """生成文件唯一标识：路径+大小+修改时间"""
    size = os.path.getsize(pdf_path)
    mtime = os.path.getmtime(pdf_path)
    return hashlib.md5(f"{pdf_path}_{size}_{mtime}".encode()).hexdigest()

def classify_invoice(text, filename):
    """判断发票类型"""
    text_lower = text.lower()
    filename_lower = filename.lower()
    categories = SETTINGS.get("categories", {})
    default_category = SETTINGS.get("default_category", "其他")
    
    # 按配置顺序匹配（同时匹配文本和文件名）
    for category, keywords in categories.items():
        if any(k.lower() in text_lower or k.lower() in filename_lower for k in keywords):
            return category
    
    return default_category

def extract_info(pdf_path):
    """提取日期、金额、类别"""
    filename = os.path.basename(pdf_path)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages[:3]:
                text += page.extract_text() or ""
    except:
        return None
    
    # 1. 类别
    category = classify_invoice(text, filename)
    
    # 2. 日期
    date_match = re.search(r'开票日期[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日', text)
    if not date_match:
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if not date_match:
        # 用文件修改日期
        mtime = os.path.getmtime(pdf_path)
        date = time.strftime("%Y%m%d", time.localtime(mtime))
    else:
        if len(date_match.groups()) == 3:
            date = f"{date_match.group(1)}{date_match.group(2).zfill(2)}{date_match.group(3).zfill(2)}"
        else:
            date = "未知日期"
    
    # 3. 金额 - 优先匹配价税合计（小写）格式
    amount_match = re.search(r'价税合计[^￥¥]*[￥¥]\s*(\d+\.?\d*)', text)
    if not amount_match:
        amount_match = re.search(r'价税合计[：:]\s*[￥¥]?\s*(\d+\.?\d*)', text)
    if not amount_match:
        amount_match = re.search(r'合计[：:]\s*[￥¥]?\s*(\d+\.?\d*)', text)
    if not amount_match:
        amount_match = re.search(r'总计[：:]\s*[￥¥]?\s*(\d+\.?\d*)', text)
    if not amount_match:
        amount_match = re.search(r'[￥¥]\s*(\d+\.\d{2})', text)
    if not amount_match:
        amount_match = re.search(r'(\d+\.\d{2})\s*元', text)

    amount = amount_match.group(1) if amount_match else "未知"
    
    # 4. 发票号码
    invoice_no_match = re.search(r'发票号码[：:\s]*(\d{8,20})', text)
    if not invoice_no_match:
        invoice_no_match = re.search(r'号码[：:\s]*(\d{8,20})', text)
    if not invoice_no_match:
        invoice_no_match = re.search(r'No[.:：\s]*(\d{8,20})', text, re.IGNORECASE)
    
    invoice_no = invoice_no_match.group(1) if invoice_no_match else ""
    
    return {
        'category': category,
        'date': date,
        'amount': amount,
        'invoice_no': invoice_no
    }

def rename_pdf(pdf_path, log):
    """重命名单个PDF"""
    # 检查是否已处理
    file_id = get_file_id(pdf_path)
    if file_id in log:
        print(f"⏭️  已处理过，跳过: {os.path.basename(pdf_path)}")
        return
    
    dir_path = os.path.dirname(pdf_path)
    info = extract_info(pdf_path)
    if not info:
        print(f"❌ 解析失败: {pdf_path}")
        return
    
    # 命名格式：类型-开票日期-开票金额-发票号码.pdf
    invoice_no_part = f"-{info['invoice_no']}" if info['invoice_no'] else ""
    base_name = f"{info['category']}-{info['date']}-{info['amount']}{invoice_no_part}"
    new_name = f"{base_name}.pdf"
    new_path = os.path.join(dir_path, new_name)

    # 避免重名
    counter = 1
    while os.path.exists(new_path):
        new_name = f"{base_name}_{counter}.pdf"
        new_path = os.path.join(dir_path, new_name)
        counter += 1
    
    os.rename(pdf_path, new_path)
    print(f"✅ {os.path.basename(pdf_path)} → {new_name}")
    
    # 记录到日志
    log[file_id] = {
        'original_name': os.path.basename(pdf_path),
        'new_name': new_name,
        'original_path': pdf_path,
        'new_path': new_path,
        'processed_time': time.strftime("%Y-%m-%d %H:%M:%S"),
        'category': info['category'],
        'invoice_no': info['invoice_no'],
        'date': info['date'],
        'amount': info['amount']
    }
    save_log(log)

if __name__ == "__main__":
    # 加载配置
    load_settings()
    print(f"配置加载完成，分类数: {len(SETTINGS.get('categories', {}))}")
    
    # 获取目标路径
    if len(sys.argv) >= 2:
        target = sys.argv[1]
    else:
        target = SETTINGS.get("default_directory", "./")
        print(f"使用默认目录: {target}")
    
    # 转换相对路径为绝对路径
    if not os.path.isabs(target):
        target = os.path.join(SCRIPT_DIR, target)
    
    log = load_log()
    
    if os.path.isfile(target):
        rename_pdf(target, log)
    elif os.path.isdir(target):
        for root, dirs, files in os.walk(target):
            for f in files:
                if f.lower().endswith('.pdf'):
                    rename_pdf(os.path.join(root, f), log)
    else:
        print(f"❌ 路径不存在: {target}")
        sys.exit(1)