from app.databases.db import Base

from sqlalchemy import String, Text, DateTime, Uuid, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import text
from sqlalchemy import UniqueConstraint

from uuid import UUID
from datetime import datetime

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
