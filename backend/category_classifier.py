# -*- coding: utf-8 -*-
"""
News category classifier based on title keywords.
Provides dynamic classification for news from mixed sources.
"""
import re

# Category keyword patterns (case-insensitive)
# Order matters - more specific patterns first
CATEGORY_PATTERNS = {
    '前端': [
        r'\breact\b', r'\bvue\.?js?\b', r'\bangular\b', r'\bsvelte\b', r'\bsolid\.?js\b',
        r'\bcss\b', r'\bjavascript\b', r'\btypescript\b', r'\bjs\b(?!\w)', r'\bes6\b', r'\bes202\d\b',
        r'\bwebpack\b', r'\bvite\b', r'\brollup\b', r'\bparcel\b', r'\besbuild\b',
        r'\bbabel\b', r'\bhtml5?\b', r'\bdom\b', r'\bsvg\b(?!lib)', r'\bcanvas\b',
        r'\bwebgl\b', r'\bthree\.js\b', r'\bd3\.js\b', r'\bwebgpu\b',
        r'\bnpm\b', r'\byarn\b', r'\bpnpm\b', r'\bnode\.js\b', r'\bdeno\b', r'\bbun\b',
        r'\bnext\.js\b', r'\bnuxt\b', r'\bgatsby\b', r'\bastro\b', r'\bremix\b',
        r'\btailwind\b', r'\bsass\b', r'\bless\b(?!\s+than)', r'\bstylus\b', r'\bpostcss\b',
        r'\bfrontend\b', r'\bfront-end\b', r'前端', r'\bspa\b', r'\bpwa\b',
        r'\bui\s+design', r'\bui\s+component', r'\buser\s+interface', r'\bux\s+design',
        r'浏览器', r'\bchrome\b', r'\bfirefox\b', r'\bsafari\b', r'\bedge\b',
        r'\bweb\s+component', r'\bshadow\s+dom', r'\bweb\s+worker', r'\bservice\s+worker',
        r'\bjsx\b', r'\btsx\b', r'\bjquery\b', r'\bootstrap\b', r'\bmaterial\s+ui\b',
    ],
    '后端': [
        r'\bjava\b(?!script)', r'\bspring\b', r'\bspringboot\b', r'\bspring\s+cloud\b',
        r'\bgolang\b', r'\bgo\s+语言', r'\bwritten\s+in\s+go\b', r'\bgo\s+module\b',
        r'\bpython\b(?!\s*script)', r'\bdjango\b', r'\bflask\b', r'\bfastapi\b', r'\btornado\b',
        r'\bruby\b', r'\brails\b', r'\bphp\b', r'\blaravel\b', r'\bsymfony\b',
        r'\brust\b', r'\bactix\b', r'\brocket\b', r'\baxum\b',
        r'\bc\+\+\b', r'\bc\#\b', r'\.net\b', r'\basp\.net\b',
        r'\b数据库', r'\bmysql\b', r'\bpostgresql\b', r'\bredis\b', r'\bmongodb\b',
        r'\belasticsearch\b', r'\bcassandra\b', r'\bmariadb\b', r'\bsqlite\b',
        r'\boracle\b(?!\s*拒绝)', r'\bsql\s+server\b', r'\bclickhouse\b', r'\btidb\b',
        r'微服务', r'\bapi\s+gateway', r'\brest\s*api', r'\bgraphql\b', r'\bgrpc\b',
        r'\bkafka\b', r'\brabbitmq\b', r'\brocketmq\b', r'\bpulsar\b',
        r'后端', r'\bbackend\b', r'\bback-end\b', r'\bserver\s+side',
        r'\bnginx\b', r'\bapache\b(?!\s+dolphin)', r'\btomcat\b', r'\bjetty\b', r'\bundertow\b',
        r'\blinux\b', r'\bubuntu\b', r'\bcentos\b', r'\bdebian\b', r'\bfedora\b',
        r'\bsystemd\b', r'\bshell\s+script', r'\bbash\b', r'\bzsh\b',
        r'\borm\b', r'\bmybatis\b', r'\bhibernate\b', r'\bjpa\b',
    ],
    '云原生': [
        r'\bdocker\b', r'\bcontainer\b', r'\bcontainerd\b', r'\bcri-o\b',
        r'\bkubernetes\b', r'\bk8s\b', r'\bhelm\b', r'\bkustomize\b',
        r'\bistio\b', r'\blinkerd\b', r'\benvoy\b', r'\bconsul\b',
        r'\bprometheus\b', r'\bgrafana\b', r'\bjaeger\b', r'\bzipkin\b',
        r'\bopentelemetry\b', r'\bfluentd\b', r'\belk\b', r'\bloki\b',
        r'\bterraform\b', r'\bansible\b', r'\bpulumi\b', r'\bvagrant\b',
        r'\bci/cd\b', r'\bjenkins\b', r'\bgitlab\s*ci\b', r'\bgithub\s*actions\b',
        r'\bargo\s*cd\b', r'\btekton\b', r'\bspinnaker\b', r'\bflux\b',
        r'\bdevops\b', r'\bsre\b', r'\bsite\s+reliability',
        r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\balicloud\b', r'\btencent\s+cloud\b',
        r'云原生', r'容器', r'微服务架构', r'服务网格', r'不可变基础设施',
    ],
    'AI': [
        r'\bmachine\s+learning\b', r'\bdeep\s+learning\b', r'\bneural\s+network',
        r'\btensorflow\b', r'\bpytorch\b', r'\bkeras\b', r'\bjax\b', r'\bpaddle\b',
        r'\bhuggingface\b', r'\btransformers?\b', r'\bllm\b', r'\blarge\s+language\s+model',
        r'\bgpt\b', r'\bchatgpt\b', r'\bclaude\b', r'\bgemini\b', r'\bcopilot\b',
        r'\bopenai\b', r'\banthropic\b', r'\bmistral\b', r'\bollama\b', r'\bllama\b',
        r'\blangchain\b', r'\bllamaindex\b', r'\bvector\s+database', r'\bvector\s+db',
        r'\bembeddings?\b', r'\bsemantic\s+search', r'\brag\b', r'\bprompt\s+engineering',
        r'\bcomputer\s+vision\b', r'\bcv\b', r'\bnlp\b', r'\bnatural\s+language',
        r'\bstable\s+diffusion\b', r'\bmidjourney\b', r'\bdall-e\b', r'\bstable\s+video',
        r'\bautonomous\b', r'\brobotics?\b', r'\b强化学习', r'\b迁移学习', r'\b联邦学习',
        r'人工智能', r'机器学习', r'深度学习', r'神经网络', r'大模型', r'生成式\s*ai', r'\bgenai\b',
        r'\bmoe\b', r'\bmulti-modal\b', r'多模态', r'\bagent\b', r'智能体',
    ],
    '区块链': [
        r'\bblockchain\b', r'\bcryptocurrency\b', r'\bbitcoin\b', r'\bethereum\b',
        r'\bsmart\s+contract\b', r'\bnft\b', r'\bdefi\b', r'\bdao\b', r'\bdex\b',
        r'\bweb3\b', r'\bsolidity\b', r'\bmining\b', r'\bwallet\b', r'\bmetaverse\b',
        r'区块链', r'比特币', r'以太坊', r'加密货币', r'数字货币', r'虚拟货币',
        r'\bsolana\b', r'\bpolkadot\b', r'\bcosmos\b', r'\bavalanche\b',
        r'\bzero\s+knowledge\b', r'\bzk-rollup\b', r'\blayer\s*2\b',
    ],
}

# Sources that should use dynamic classification
DYNAMIC_CLASSIFICATION_SOURCES = {
    'Hacker News', 'Reddit r/programming', '开源中国', 'InfoQ',
    '阿里云开发者社区', '阮一峰的网络日志', '尚硅谷', '黑马程序员',
    'Tech With Tim', 'Computerphile'
}

# Category name mapping for backward compatibility (old -> new)
CATEGORY_NAME_MAP = {
    '人工智能': 'AI',
    '其他技术': '其他'
}


def classify_by_title(title, default_category='其他技术'):
    """
    Classify news based on title keywords.
    
    Args:
        title: News title
        default_category: Default category if no match found
        
    Returns:
        Best matching category or default_category
    """
    if not title:
        return default_category
    
    title_lower = title.lower()
    
    # Check each category's patterns
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, title_lower):
                return category
    
    return default_category


def should_use_dynamic_classification(source_name):
    """
    Check if a source should use dynamic classification.
    
    Args:
        source_name: Name of the RSS source
        
    Returns:
        True if dynamic classification should be used
    """
    return source_name in DYNAMIC_CLASSIFICATION_SOURCES


def get_category_for_article(title, source_name, default_category):
    """
    Get the appropriate category for an article.
    Uses dynamic classification for mixed sources.
    
    Args:
        title: Article title
        source_name: RSS source name
        default_category: Category from RSS source mapping
        
    Returns:
        Final category for the article
    """
    # If source is in dynamic classification list, use title-based classification
    if should_use_dynamic_classification(source_name):
        return classify_by_title(title, default_category)
    
    # Otherwise, use the source's default category
    return default_category


# For testing
if __name__ == '__main__':
    test_titles = [
        ("React 19 Beta Released", "Hacker News"),
        ("Building Microservices with Go", "开源中国"),
        ("Kubernetes 1.30 New Features", "Reddit r/programming"),
        ("Machine Learning Basics", "阮一峰的网络日志"),
        ("Bitcoin Price Analysis", "InfoQ"),
        ("CSS Grid Layout Tutorial", "Hacker News"),
    ]
    
    for title, source in test_titles:
        category = get_category_for_article(title, source, '其他技术')
        print(f"[{source}] {title[:40]}... -> {category}")
