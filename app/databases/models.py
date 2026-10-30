from app.databases.db import Base

from sqlalchemy import String, Text, DateTime, Uuid, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import text
from sqlalchemy import UniqueConstraint, CheckConstraint

from uuid import UUID
from datetime import datetime

from typing import Literal

JobStatus=Literal["pending","succeeded","in flight","exhausted"]

class Documents(Base):
    __tablename__="documents"
    id: Mapped[UUID] = mapped_column(Uuid, 
                                     primary_key=True, 
                                     server_default=text("gen_random_uuid()"))
    
    title: Mapped[str] = mapped_column(String, 
                                       nullable=False)
    
    content: Mapped[str] = mapped_column(Text, 
                                         nullable=False)
    
    version: Mapped[int] = mapped_column(Integer, 
                                         server_default=text("1"), 
                                         nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), 
                                                 server_default=text("now()"),
                                                 nullable=False)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), 
                                                 server_default=text("now()"),
                                                 nullable=False)

    __mapper_args__={
        "version_id_col":version
    }

class DocumentHistory(Base):
    __tablename__="document_history"

    __table_args__=(
        UniqueConstraint(
            "document_id",
            "version",
            name="unique_doc_version_doc_name_comb"
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, 
                                     primary_key=True,
                                     server_default=text("gen_random_uuid()"))
    document_id: Mapped[UUID] = mapped_column(Uuid, 
                                    ForeignKey("documents.id"),
                                    nullable=False)
    title: Mapped[str] = mapped_column(String, 
                                       nullable=False)
    content:Mapped[str] = mapped_column(Text, 
                                        nullable=False)
    version:Mapped[int] = mapped_column(Integer,
                                        nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 nullable=False,
                                                 server_default=text("now()"))

class Jobs(Base):
    __tablename__="jobs"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','succeeded','in flight','exhausted')",
            name="check_job_status"
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid,
                                     primary_key=True,
                                     nullable=False,
                                     server_default=text("gen_random_uuid()"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 nullable=False,
                                                 server_default=text("now()"))
    document_id: Mapped[UUID] = mapped_column(Uuid,
                                              ForeignKey("documents.id"),
                                              nullable=False)
    celery_task_id:Mapped[UUID] = mapped_column(Uuid,
                                                nullable=False)
    attempt_no: Mapped[int] = mapped_column(Integer,
                                            nullable=False,
                                            server_default=text("1"))
    status: Mapped[JobStatus] = mapped_column(String,
                                              nullable=False,
                                              default="pending")
    error_message: Mapped[str | None] = mapped_column(String)
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True),
                                                   nullable=True)

class JobHistory(Base):
    __tablename__="jobhistory"

    __table_args__ = (
        CheckConstraint(
            "status in ('pending','succeeded','in flight','exhausted')",
            name="check_job_status"
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid,
                                     primary_key=True,
                                     server_default=text("gen_random_uuid()"))
    job_id: Mapped[UUID] = mapped_column(Uuid,
                                         ForeignKey("jobs.id"),
                                         nullable=False)
    attempt_no: Mapped[int] = mapped_column(Integer,
                                            nullable=False)
    status: Mapped[JobStatus] = mapped_column(String,
                                              nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 nullable=False,
                                                 server_default=text("now()"))