import asyncio

import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from django.core.serializers.json import DjangoJSONEncoder
from .models import Notification
class NotificatonConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_initial_data()
        await self.channel_layer.group_add('all', self.channel_name)

    async def disconnect(self, close_code):
        print(f"WebSocket connection closed with code: {close_code}")

    async def send_notification(self, event=None):
        print("SEND ALERT CONSUMER CALLED ===============")
        notification = await self.get_notification()
        await self.send(text_data=json.dumps({
            'notification': notification
        }, cls=DjangoJSONEncoder))  # Use DjangoJSONEncoder to handle serialization

    async def send_initial_data(self):
        notification = await self.get_notification()
        await self.send(text_data=json.dumps({
            'initial_notification': notification
        }, cls=DjangoJSONEncoder))  # Use DjangoJSONEncoder to handle serialization

    @database_sync_to_async
    def get_notification(self):
        notification = Notification.objects.all().values()
        for alert in notification:
            alert['dateTime'] = alert['dateTime'].isoformat() if alert['dateTime'] else None
        return list(notification)

    async def send_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

# Define a global instance of AlertConsumer
# alert_consumer = AlertConsumer()

async def send_alert_update(self):
    print("SEND ALERT CALLED ++++++++✅")
    # Trigger send_notification method on the global instance of AlertConsumer
    await self.AlertConsumer.send_notification()


