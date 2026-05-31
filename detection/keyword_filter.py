"""Keyword-based scam detection using a rule file."""

from pathlib import Path
from typing import Optional

from loguru import logger


class KeywordFilter:
    """Load keywords from a text file and match against incoming messages."""

    def __init__(self, keywords_file: str = "rules/keywords.txt") -> None:
        self.keywords: list[str] = []
        self._load_keywords(keywords_file)

    def _load_keywords(self, filepath: str) -> None:
        path = Path(filepath)
        if not path.exists():
            logger.warning("Keywords file not found: {}", filepath)
            return
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    self.keywords.append(line.lower())
        logger.info("Loaded {} keywords from {}", len(self.keywords), filepath)

    def check(self, text: str) -> Optional[dict]:
        """Return detection info if the text matches any keyword, else None."""
        text_lower = text.lower()
        for keyword in self.keywords:
            if keyword in text_lower:
                return {
                    "type": self._classify_keyword(keyword),
                    "matched_keyword": keyword,
                    "confidence": 1.0,
                }
        return None

    @staticmethod
    def _classify_keyword(keyword: str) -> str:
        categories = {
            "投资诈骗": [
                "稳赚", "收益", "保本", "回报", "翻倍", "内部消息",
                "跟单", "带你赚", "投资平台", "理财平台", "guaranteed",
                "no risk", "double your money", "profit",
            ],
            "博彩广告": [
                "博彩", "赌博", "彩票", "开奖", "下注", "赔率",
                "百家乐", "棋牌", "六合彩", "时时彩", "快三",
                "赛车", "返水", "充值返利",
            ],
            "色情引流": [
                "约炮", "一夜情", "上门服务", "成人直播", "私密视频",
                "裸聊", "色情", "小姐姐约",
            ],
            "刷单兼职": [
                "刷单", "兼职", "日赚", "佣金", "刷好评",
                "网赚", "薅羊毛", "零门槛", "动动手指", "轻松月入",
            ],
            "钓鱼链接": [
                "免费领取", "中奖", "恭喜", "限时优惠", "点击链接",
                "扫码领取", "红包雨", "抽奖", "验证码", "账号异常",
                "click here", "act now", "free giveaway",
            ],
            "传销资金盘": [
                "拉人头", "层级奖励", "团队收益", "分销", "推广奖励",
                "静态收益", "动态收益",
            ],
        }
        for category, fragments in categories.items():
            for fragment in fragments:
                if fragment in keyword:
                    return category
        return "其他违规"
