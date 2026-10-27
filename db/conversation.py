import uuid
from datetime import datetime, timezone
from typing import Optional,Dict,Any


from pymongo import DESCENDING


from db.mongo import get_collection_name

conversations = get_collection_name("conversations")
conversations.create_index([("last_interacted",DESCENDING)])

# _____ HELPERS __________
def utc_now():
    return datetime.now(timezone.utc)

def create_conversation_id():
    return str(uuid.uuid4())


def create_new_conversation(title :Optional[str]=None,role :Optional[str]=None,content :Optional[str]=None):
    conversation_id = create_conversation_id()
    ts = utc_now()
    doc = {
        "_id" : conversation_id,
        "title":title or "Untitled Conversation",
        "messages": [],
        "last_interacted": ts
    }
    if role and content:
        doc["messages"].append({"role":role, "content": content,"ts": ts})
    conversations.insert_one(doc)
    return conversation_id


def add_message(conversation_id:str, role:str, content:str):
    ts = utc_now()
    res = conversations.update_one(
        {"_id":conversation_id},
        {
            "$push": {"messages":{"role":role,"content":content}},
            "$set" : {"last_interacted": ts},
        },
    )
    return res.matched_count==1

def get_conversation(conversation_id:str):
    ts = utc_now()
    doc = conversations.find_one_and_update(
        {"_id":conversation_id},
        {
            "$set":{"last_interacted":ts}
        },
        return_document=True
    )
    return doc


def get_all_conversations():
    ts = utc_now()
    cursor = conversations.find({},{"title": 1 }).sort("last_interacted",DESCENDING)
    return {doc["_id"]: doc["title"] for doc in cursor}