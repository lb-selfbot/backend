from typing import Any, Dict, Tuple
import threading
import time
import os

import discord
import janus

class ClydeJob:
    username: str
    message: str
    response: str
    error: bool

    def __init__(self, username: str, message: str) -> None:
        self.username = username
        self.message = message
        self.response = ""
        self.error = False
    
    def __hash__(self) -> int:
        return hash(self.username+self.message)


class ClydeBot(discord.Client):
    def __init__(self, **options: Any) -> None:
        self.channel_id = options.pop("channel_id", 1101233174316585052)
        self.tasks: janus.Queue[ClydeJob] = None
        self.responses: Dict[int, ClydeJob] = {}

        super().__init__(allowed_mentions=discord.AllowedMentions.none(), **options)

    async def get_response(self, username: str, message: str) -> str:
        # Get the channel
        channel = self.get_channel(self.channel_id)
        if channel is None:
            channel = await self.fetch_channel(self.channel_id)

        # Get the thread
        thread_name = f"Clyde - {username}"

        thread = discord.utils.get(channel.threads, name=thread_name)

        if thread is None:
            thread = await channel.create_thread(name=thread_name)

        # Send the message and wait for response
        await thread.send(f"@Clyde {message}", files=[])
        message = await self.wait_for(
            "message", check=lambda m: m.channel == thread, timeout=10
        )

        return message.content

    async def worker(self) -> None:
        while True:
            job = await self.tasks.async_q.get()

            try:
                job.response = await self.get_response(job.username, job.message)
            except discord.errors.HTTPException as e:
                job.response = "Failed to get response: " + str(e)
                job.error = True


            self.responses[hash(job)] = job
    
    def wait_for_response(self, job: ClydeJob) -> Tuple[str, bool]:
        job_hash = hash(job)
        
        if job_hash in self.responses:
            job = self.responses[job_hash]

            response, error = job.response, job.error
            
            del self.responses[job_hash]

            return (response, error)

        for i in range(50):
            if job_hash in self.responses:
                job = self.responses[job_hash]

                response, error = job.response, job.error

                del self.responses[job_hash]

                return (response, error)
            
            time.sleep(0.1)
        
        return ("Failed to get response", True)

    async def on_ready(self) -> None:
        self.tasks = janus.Queue()
        self.loop.create_task(self.worker())


clyde_bot = ClydeBot()


def run_clyde_bot():
    if clyde_bot.is_ready():
        return

    thread = threading.Thread(
        target=lambda: clyde_bot.run(os.environ.get("CLYDE_BOT_TOKEN")),
        daemon=True,
    )

    thread.start()
