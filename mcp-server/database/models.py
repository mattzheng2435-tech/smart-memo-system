"""
数据库模型定义
"""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass
import uuid


@dataclass
class Memo:
    """备忘录数据模型"""
    id: str
    what: str
    when_due: Optional[datetime]
    who: Optional[str]
    status: str = "pending"
    priority: str = "normal"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    context: Optional[str] = None
    category: Optional[str] = None
    metadata: Optional[dict] = None

    @classmethod
    def from_row(cls, row):
        """从数据库行创建 Memo 对象"""
        if not row:
            return None
        return cls(
            id=str(row['id']),
            what=row['what'],
            when_due=row['when_due'],
            who=row['who'],
            status=row['status'],
            priority=row['priority'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            completed_at=row['completed_at'],
            tags=row['tags'],
            context=row['context'],
            category=row['category'],
            metadata=row['metadata']
        )

    async def create(self, conn):
        """创建新备忘录"""
        from .queries import create_memo
        return await create_memo(
            conn,
            what=self.what,
            when_due=self.when_due,
            who=self.who,
            priority=self.priority,
            tags=self.tags,
            context=self.context,
            category=self.category,
            metadata=self.metadata
        )

    async def update_status(self, conn, new_status: str):
        """更新备忘录状态"""
        self.status = new_status
        if new_status == "completed":
            self.completed_at = datetime.now()

        await conn.execute("""
            UPDATE memos
            SET status = $1, completed_at = $2, updated_at = NOW()
            WHERE id = $3
        """, new_status, self.completed_at, self.id)

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'what': self.what,
            'when_due': self.when_due.isoformat() if self.when_due else None,
            'who': self.who,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'tags': self.tags,
            'context': self.context,
            'category': self.category
        }

    def __repr__(self):
        return f"Memo(id={self.id[:8]}..., what={self.what[:20]}..., status={self.status})"
