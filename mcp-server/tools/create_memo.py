"""
创建备忘录工具 - 支持追问式补全缺失信息
"""

import re
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from ..database import Memo, create_memo


async def handle(pool, args):
    """
    处理创建备忘录请求

    Args:
        pool: 数据库连接池
        args: 用户参数 {what, when, who, priority, tags, context}

    Returns:
        str: 响应消息
    """
    what = args.get("what")
    when_str = args.get("when")
    who = args.get("who")
    priority = args.get("priority", "normal")
    tags = args.get("tags", [])
    context = args.get("context", "")

    # 分析缺失字段
    missing = []
    if not when_str:
        # 尝试从内容中推断时间
        when_str = extract_time_hint(what)
        if not when_str:
            missing.append("when")

    if not who:
        # 尝试从内容中推断人名
        who = extract_people(what)
        if not who:
            missing.append("who")

    # 如果仍有缺失字段，返回追问
    if missing:
        return generate_followup_questions(what, when_str, who, missing)

    # 解析时间
    when_due = parse_when(when_str)

    # 创建备忘录
    async with pool.acquire() as conn:
        row = await create_memo(
            conn,
            what=what,
            when_due=when_due,
            who=who,
            priority=priority,
            tags=tags,
            context=context
        )

    memo = Memo.from_row(row)

    # 格式化响应
    when_str_fmt = when_due.strftime("%Y-%m-%d %H:%M") if when_due else "无截止时间"
    response = f"""✅ 已创建备忘录:

  内容: {memo.what}
  时间: {when_str_fmt}"""

    if who:
        response += f"\n  相关人: {who}"

    return response


def parse_when(when_str: str) -> datetime:
    """
    智能解析时间字符串

    支持格式:
    - ISO 8601: "2026-01-23T10:00:00"
    - 自然语言: "tomorrow 3pm", "next Monday", "下周五"
    - 相对时间: "今天", "明天", "后天"
    """
    if not when_str:
        # 默认: 明天上午9:30
        return datetime.now().replace(hour=9, minute=30, second=0, microsecond=0) + timedelta(days=1)

    try:
        # 尝试 ISO 8601 格式
        return datetime.fromisoformat(when_str.replace('Z', '+00:00'))
    except:
        try:
            # 尝试自然语言解析
            result = date_parser.parse(when_str, fuzzy=True)
            # 如果解析出的时间是过去的，假设是未来的
            if result < datetime.now():
                # 尝试添加年份或月份
                if "小时" in when_str or "hour" in when_str.lower():
                    return datetime.now() + timedelta(hours=int(re.findall(r'\d+', when_str)[0]) if re.findall(r'\d+', when_str) else datetime.now() + timedelta(hours=1)
                else:
                    # 默认加一天
                    return result + timedelta(days=1)
            return result
        except:
            # 解析失败，使用默认值
            return datetime.now().replace(hour=9, minute=30, second=0, microsecond=0) + timedelta(days=1)


def extract_time_hint(text: str) -> str:
    """
    从文本中提取时间提示

    Examples:
        "明天下午3点" -> "tomorrow 3pm"
        "后天" -> "后天" (会被 parse_when 处理)
    """
    if not text:
        return None

    text_lower = text.lower()

    # 简单规则匹配
    patterns = [
        (r'今天', 'today'),
        (r'明天', 'tomorrow'),
        (r'后天', '后天'),
        (r'下周', 'next week'),
        (r'(\d+)月(\d+)日', None),  # 特殊处理
        (r'(\d+)点', None),  # 特殊处理
    ]

    for pattern, replacement in patterns:
        if re.search(pattern, text):
            if replacement:
                return replacement
            else:
                # 返回原始匹配，让 parse_when 处理
                match = re.search(pattern, text)
                return match.group(0)

    return None


def extract_people(text: str) -> str:
    """
    从文本中提取人名

    简单实现: 查找大写开头的单词
    后续可以集成更复杂的 NER 模型
    """
    if not text:
        return None

    # 常见英文名模式
    people = re.findall(r'\b[A-Z][a-z]+\b', text)

    if people:
        # 返回第一个人名（通常是主要对象）
        return people[0]

    # 尝试中文人名（简单规则：2-3个汉字）
    chinese_people = re.findall(r'[\u4e00-\u9fff]{2,3}', text)
    if chinese_people:
        return chinese_people[0]

    return None


def generate_followup_questions(what, when, who, missing):
    """
    生成追问问题

    Args:
        what: 任务内容
        when: 已知时间（可能为None）
        who: 已知人员（可能为None）
        missing: 缺失字段列表 ['when', 'who']

    Returns:
        str: 追问消息
    """
    questions = []

    if "when" in missing:
        questions.append("📅 这个任务什么时候需要完成？\n   例如: '明天下午3点', '下周五', '2026-01-25'")

    if "who" in missing:
        questions.append("👥 这个任务涉及谁？\n   例如: '给Paul', '产品总监'")

    return """❓ 需要更多信息才能创建备忘录:

""" + "\n\n".join(f"{q}" for q in questions)


def smart_infer(text: str) -> dict:
    """
    智能推断: 从文本中提取尽可能多的信息

    Returns:
        dict: {what, when, who, confidence}
    """
    result = {
        'what': text,
        'when': None,
        'who': None,
        'confidence': 0.0
    }

    # 提取时间
    when = extract_time_hint(text)
    if when:
        result['when'] = when
        result['confidence'] += 0.3

    # 提取人名
    who = extract_people(text)
    if who:
        result['who'] = who
        result['confidence'] += 0.3

    # 如果既有时间又有人名，置信度较高
    if result['when'] and result['who']:
        result['confidence'] += 0.2

    return result
