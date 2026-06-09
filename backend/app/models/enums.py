import enum


class FactoryStatus(str, enum.Enum):
    trial = "trial"
    active = "active"
    suspended = "suspended"


class AccountStatus(str, enum.Enum):
    active = "active"
    disabled = "disabled"


class DeviceStatus(str, enum.Enum):
    online = "online"
    offline = "offline"
    warning = "warning"
    disabled = "disabled"


class PromptStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class AlertStatus(str, enum.Enum):
    open = "open"
    resolved = "resolved"
    ignored = "ignored"


class SeverityLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
