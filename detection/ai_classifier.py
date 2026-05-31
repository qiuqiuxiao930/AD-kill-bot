"""AI-based scam message classifier using scikit-learn."""

import re
from typing import Optional

from loguru import logger

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline

    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not installed; AI classifier disabled")


# Pre-built training corpus (small but representative)
_TRAIN_TEXTS = [
    # ── scam / spam ───────────────────────────────────────────
    ("加我微信，稳赚不赔，日收益300%", "scam"),
    ("点击链接领取现金红包，限时抢购", "scam"),
    ("博彩平台注册送88，充值返利50%", "scam"),
    ("兼职刷单日赚500，佣金日结", "scam"),
    ("内部消息，跟我投资翻倍", "scam"),
    ("成人直播私密视频免费看", "scam"),
    ("拉人头赚钱，团队收益无上限", "scam"),
    ("免费送比特币，扫码领取", "scam"),
    ("恭喜你中奖一百万，点击链接领取", "scam"),
    ("零风险高回报投资平台推荐", "scam"),
    ("guaranteed profit no risk investment", "scam"),
    ("double your money in 24 hours", "scam"),
    ("free crypto airdrop click here now", "scam"),
    ("send BTC to this wallet for 200% return", "scam"),
    ("advance fee required wire transfer", "scam"),
    ("棋牌游戏充值返水百家乐", "scam"),
    ("快三时时彩北京赛车官方平台", "scam"),
    ("网赚项目零门槛月入过万", "scam"),
    ("扫码加群领红包，每天分享赚钱", "scam"),
    ("约炮上门服务加微信", "scam"),
    # ── normal ────────────────────────────────────────────────
    ("大家好，今天天气不错", "normal"),
    ("请问这个功能怎么使用？", "normal"),
    ("我觉得这部电影很好看", "normal"),
    ("明天下午三点开会，请大家准时参加", "normal"),
    ("感谢管理员的辛勤维护", "normal"),
    ("hello everyone how are you", "normal"),
    ("can someone help me with this bug", "normal"),
    ("the weather is nice today", "normal"),
    ("i just finished reading a great book", "normal"),
    ("thanks for the update", "normal"),
    ("这个版本修复了很多问题", "normal"),
    ("周末有人一起打球吗", "normal"),
    ("分享一篇很有意思的文章", "normal"),
    ("有没有人用过这个库", "normal"),
    ("刚下载了新版应用，体验不错", "normal"),
]

_LABEL_MAP = {"scam": "诈骗广告", "normal": "正常消息"}


class AIClassifier:
    """Lightweight TF-IDF + Naive Bayes classifier for scam detection."""

    def __init__(self, confidence_threshold: float = 0.85) -> None:
        self.confidence_threshold = confidence_threshold
        self._pipeline: Optional[Pipeline] = None
        if _SKLEARN_AVAILABLE:
            self._train()

    def _train(self) -> None:
        texts = [t for t, _ in _TRAIN_TEXTS]
        labels = [l for _, l in _TRAIN_TEXTS]
        self._pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))),
                ("clf", MultinomialNB(alpha=0.1)),
            ]
        )
        self._pipeline.fit(texts, labels)
        logger.info("AI classifier trained with {} samples", len(texts))

    @property
    def available(self) -> bool:
        return self._pipeline is not None

    def predict(self, text: str) -> Optional[dict]:
        """Return detection result if the text is classified as scam above threshold."""
        if not self.available:
            return None

        cleaned = self._preprocess(text)
        if not cleaned:
            return None

        proba = self._pipeline.predict_proba([cleaned])[0]
        classes = list(self._pipeline.classes_)
        scam_idx = classes.index("scam") if "scam" in classes else -1
        if scam_idx < 0:
            return None

        confidence = float(proba[scam_idx])
        if confidence >= self.confidence_threshold:
            return {
                "type": "AI检测-诈骗广告",
                "confidence": round(confidence, 4),
            }
        return None

    @staticmethod
    def _preprocess(text: str) -> str:
        text = re.sub(r"https?://\S+", " URL ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
