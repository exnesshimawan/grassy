# -*- coding: utf-8 -*-
# @Time     :2023/12/26 17:00
# @Author   :ym
# @File     :main.py
# @Software :PyCharm

import asyncio
import random
import ssl
import json
import time
import uuid
from loguru import logger
import aiohttp  # Mengganti websockets_proxy dengan aiohttp

async def connect_to_wss(socks5_proxy, user_id):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy))
    logger.info(f"Device ID: {device_id}")
    
    proxy_url = socks5_proxy.replace("http://", "socks5://")
    uri = "wss://proxy.wynd.network:4650/"
    custom_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                await asyncio.sleep(random.randint(1, 10) / 10)
                
                async with session.ws_connect(uri, proxy=proxy_url, ssl=False, headers=custom_headers) as websocket:
                    
                    async def send_ping():
                        while True:
                            send_message = json.dumps({
                                "id": str(uuid.uuid4()),
                                "version": "1.0.0",
                                "action": "PING",
                                "data": {}
                            })
                            logger.debug(f"Sending PING: {send_message}")
                            await websocket.send_str(send_message)
                            await asyncio.sleep(20)
                    
                    asyncio.create_task(send_ping())
                    
                    while True:
                        response = await websocket.receive()
                        if response.type == aiohttp.WSMsgType.TEXT:
                            message = json.loads(response.data)
                            logger.info(f"Received message: {message}")
                            
                            if message.get("action") == "AUTH":
                                auth_response = {
                                    "id": message["id"],
                                    "origin_action": "AUTH",
                                    "result": {
                                        "browser_id": device_id,
                                        "user_id": user_id,
                                        "user_agent": custom_headers['User-Agent'],
                                        "timestamp": int(time.time()),
                                        "device_type": "extension",
                                        "version": "2.5.0"
                                    }
                                }
                                logger.debug(f"Sending AUTH response: {auth_response}")
                                await websocket.send_str(json.dumps(auth_response))
                            
                            elif message.get("action") == "PONG":
                                pong_response = {"id": message["id"], "origin_action": "PONG"}
                                logger.debug(f"Sending PONG response: {pong_response}")
                                await websocket.send_str(json.dumps(pong_response))
                        elif response.type == aiohttp.WSMsgType.CLOSED:
                            logger.warning("WebSocket closed, reconnecting...")
                            break
                        elif response.type == aiohttp.WSMsgType.ERROR:
                            logger.error(f"WebSocket error: {response.data}")
                            break
            
            except Exception as e:
                logger.error(f"Error in WebSocket connection: {e}")
                logger.error(f"Proxy used: {socks5_proxy}")
                await asyncio.sleep(5)  # Wait before reconnecting

async def main():
    _user_id = 'ID GRASSMU'
    
    # Membaca proxy dari file proxy.txt
    with open('proxy.txt', 'r') as f:
        socks5_proxy_list = [line.strip() for line in f if line.strip()]
    
    tasks = [connect_to_wss(proxy, _user_id) for proxy in socks5_proxy_list]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
