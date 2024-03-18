import tkinter as tk
import asyncio
from discord.ext import commands
from MessageEventListener import MessageEventListener
from InteractionEventListener import InteractionEventListener
import discord
import threading

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Balancing Bot Controller")

        # Frame to contain the buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        # Start Button
        self.start_button = tk.Button(button_frame, text="Start", width=10, height=2, font=("Arial", 12), command=self.start, background='grey')
        self.start_button.grid(row=0, column=0, padx=10)

        # Stop Button
        self.stop_button = tk.Button(button_frame, text="Stop", width=10, height=2, font=("Arial", 12), command=self.stop, background='light grey', state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10)

        # Exit Button
        self.exit_button = tk.Button(button_frame, text="Exit", width=10, height=2, font=("Arial", 12), command=self.root.destroy, background='grey')
        self.exit_button.grid(row=0, column=2, padx=10)

    async def main(self):
        intents = discord.Intents.all()
        self.bot = commands.Bot(command_prefix='!', intents = intents)

        token = 'Token'

        @self.bot.event
        async def on_ready():
            print('봇이 준비되었습니다.')

            # 봇의 프로필 메시지 설정
            await self.bot.change_presence(activity=discord.Game(name="'!설명서' 명령어로 설명서 제공"))

        await self.bot.add_cog(MessageEventListener(self.bot))
        await self.bot.add_cog(InteractionEventListener(self.bot))

        await self.bot.start(token)

    def start(self):
        self.start_button.config(state=tk.DISABLED, background='light grey')
        self.stop_button.config(state=tk.NORMAL, background='grey')
        self.exit_button.config(state=tk.DISABLED, background='light grey')
        threading.Thread(target=asyncio.run, args=(self.main(),)).start()

    def stop(self):
        if self.bot is not None:
            self.bot.loop.create_task(self.bot.close())  # This will stop the bot without exiting the script
            self.start_button.config(state=tk.NORMAL, background='grey')
            self.stop_button.config(state=tk.DISABLED, background='light grey')
            self.exit_button.config(state=tk.NORMAL, background='grey')

root = tk.Tk()
app = App(root)
root.mainloop()
