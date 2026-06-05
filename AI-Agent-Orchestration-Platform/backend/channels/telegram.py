import asyncio
import httpx
from sqlmodel import Session, select
import json
import logging

from backend.config import settings
import backend.database as db
from backend.models import Agent, Workflow, Conversation

from backend.runtime.executor import execute_workflow

logger = logging.getLogger(__name__)

async def register_webhook():
    """Register the FastAPI endpoint as a Telegram bot webhook."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_WEBHOOK_URL:
        logger.warning("Telegram Bot Token or Webhook URL not set. Webhook registration skipped.")
        return
        
    telegram_api = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook"
    webhook_url = f"{settings.TELEGRAM_WEBHOOK_URL}/webhook/telegram"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(telegram_api, json={"url": webhook_url})
            if resp.status_code == 200:
                logger.info(f"Telegram webhook successfully registered at: {webhook_url}")
            else:
                logger.error(f"Failed to register webhook. Status: {resp.status_code}, Response: {resp.text}")
    except Exception as e:
        logger.error(f"Exception during Telegram webhook registration: {str(e)}")

async def handle_telegram_update(update: dict):
    """Handle incoming updates (messages) from Telegram."""
    if "message" not in update or "text" not in update["message"]:
        return
        
    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"]
    
    # 1. Locate the Telegram-channelized agent
    def _get_agent():
        with Session(db.engine) as session:
            statement = select(Agent).where(Agent.channel == "telegram")
            return session.exec(statement).first()
            
    agent = await asyncio.to_thread(_get_agent)
    if not agent:
        await send_telegram_message(chat_id, "No agent is currently configured to handle Telegram commands.")
        return

    # 2. Record the conversation start state
    def _create_conv():
        with Session(db.engine) as session:
            conv = Conversation(
                agent_id=agent.id,
                channel="telegram",
                user_id=str(chat_id),
                user_message=text,
                agent_response=""
            )
            session.add(conv)
            session.commit()
            session.refresh(conv)
            return conv.id
            
    conv_id = await asyncio.to_thread(_create_conv)

    # 3. Locate a workflow that contains this agent
    def _find_workflow():
        with Session(db.engine) as session:
            workflows = session.exec(select(Workflow)).all()
            for wf in workflows:
                try:
                    graph = json.loads(wf.graph_json)
                    for node in graph.get("nodes", []):
                        if node.get("type") == "agent" and node.get("agent_id") == agent.id:
                            return wf
                except Exception:
                    pass
            return None

    workflow = await asyncio.to_thread(_find_workflow)
    if not workflow:
        reply = f"Found Telegram Agent '{agent.name}', but no active workflow contains this agent node."
        await send_telegram_message(chat_id, reply)
        
        def _update_err_reply():
            with Session(db.engine) as session:
                conv = session.get(Conversation, conv_id)
                if conv:
                    conv.agent_response = reply
                    session.add(conv)
                    session.commit()
        await asyncio.to_thread(_update_err_reply)
        return

    # 4. Send initial Thinking message
    thinking_msg_id = await send_telegram_message(chat_id, "Thinking... 🧠")

    # 5. Trigger the workflow run
    try:
        response_text = await execute_workflow(
            workflow.id,
            {"message": text, "chat_id": chat_id}
        )
        if thinking_msg_id:
            await edit_telegram_message(chat_id, thinking_msg_id, response_text)
        else:
            await send_telegram_message(chat_id, response_text)
    except Exception as e:
        response_text = f"❌ Error during workflow execution: {str(e)}"
        if thinking_msg_id:
            await edit_telegram_message(chat_id, thinking_msg_id, response_text)
        else:
            await send_telegram_message(chat_id, response_text)

    # 6. Save the response in history
    def _update_conv():
        with Session(db.engine) as session:
            conv = session.get(Conversation, conv_id)
            if conv:
                conv.agent_response = response_text
                session.add(conv)
                session.commit()
                
    await asyncio.to_thread(_update_conv)

async def send_telegram_message(chat_id: int, text: str) -> int:
    """Utility to post a message payload back to Telegram API. Returns message_id if successful, else None."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not configured. Cannot send reply.")
        return None

    # Clean Llama 3 template tags if present
    for tag in ["<|start_header_id|>", "<|end_header_id|>", "<|python_tag|>", "<|eot_id|>"]:
        text = text.replace(tag, "")
    text = text.strip()
        
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try sending as Markdown first for rich formatting
            resp = await client.post(url, json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            })
            if resp.status_code == 200:
                return resp.json().get("result", {}).get("message_id")
                
            logger.warning(f"Failed to send Markdown message to Telegram (Status: {resp.status_code}). Retrying as plain text...")
            # Fallback to plain text in case of Markdown parsing errors
            resp_fallback = await client.post(url, json={
                "chat_id": chat_id,
                "text": text
            })
            if resp_fallback.status_code == 200:
                return resp_fallback.json().get("result", {}).get("message_id")
            else:
                logger.error(f"Failed to send fallback plain text message: {resp_fallback.status_code} - {resp_fallback.text}")
    except Exception as e:
        logger.error(f"Failed to post message to Telegram API: {str(e)}")
    return None

async def edit_telegram_message(chat_id: int, message_id: int, text: str):
    """Utility to edit a previously sent message using Telegram API."""
    if not settings.TELEGRAM_BOT_TOKEN or not message_id:
        logger.warning("Bot token not configured or message_id is None. Cannot edit message.")
        return

    # Clean Llama 3 template tags if present
    for tag in ["<|start_header_id|>", "<|end_header_id|>", "<|python_tag|>", "<|eot_id|>"]:
        text = text.replace(tag, "")
    text = text.strip()

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/editMessageText"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": "Markdown"
            })
            if resp.status_code != 200:
                logger.warning(f"Failed to edit Markdown message to Telegram (Status: {resp.status_code}). Retrying as plain text...")
                resp_fallback = await client.post(url, json={
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": text
                })
                if resp_fallback.status_code != 200:
                    logger.error(f"Failed to edit fallback plain text message: {resp_fallback.status_code} - {resp_fallback.text}")
    except Exception as e:
        logger.error(f"Failed to edit message via Telegram API: {str(e)}")
