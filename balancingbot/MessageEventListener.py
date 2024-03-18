from ast import alias
import asyncio
from math import inf
import random
import discord
from discord.ext import commands
from itertools import combinations
from itertools import product

import numpy as np

class MessageEventListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.teams = []
        self.positions = ['탑', '정글', '미드', '원딜', '서폿']
        self.command = None
        self.ModifyCommand = None
        self.names = []
        self.scores = []
        self.old_player_index = 0

    @commands.command(name='밸런스', aliases=['라인고정', '칼바람'])
    async def 밸런스(self, ctx):
        self.players = {}
        self.teams = []
        self.names = []
        self.scores = []

        self.command = ctx.invoked_with # 명령어 저장
        
        print(self.command)

        if ctx.invoked_with == '밸런스':
            await ctx.send("1번째 플레이어를 입력하세요 (예. $Player1 플2)")
        elif ctx.invoked_with == '라인고정':
            await ctx.send("1번째 탑을 입력하세요 (예. $Player1 플2)")
        elif ctx.invoked_with == '칼바람':
            await ctx.send("1번째 플레이어를 입력하세요 (예. $Player1 플2)")

    @commands.command(name='수정')
    async def 수정(self, ctx):
        if len(self.names) == 0:
            await ctx.send("수정할 플레이어가 없습니다")
            return
        
        print(f"before names: {self.names}, scores: {self.scores}")

        self.ModifyCommand = ctx.invoked_with

        AsisPlayers="참가자 명단\n"
        for index, asisPlayer in enumerate(self.names):
            AsisPlayers += f"{index+1}. {asisPlayer}\n"
        AsisPlayers += "빠지는 플레이어의 번호를 입력하세요."
        
        await ctx.channel.send(AsisPlayers)

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        old_player_index_msg = await self.bot.wait_for('message', check=check)
        old_player_index_str = old_player_index_msg.content

        try:
            self.old_player_index = int(old_player_index_str)
            if self.old_player_index > len(self.names):
                raise ValueError("올바른 번호를 입력하세요.")
        except ValueError as e:
            await ctx.send(str(e))
            return

        old_player_name = self.names[self.old_player_index-1]
        del self.players[old_player_name]

        if self.command == '라인고정':
            if self.positions[(self.old_player_index-1)//2] == '미드':
                position_ment= "를"
            else:
                position_ment= "을"

            await ctx.send(f"<{old_player_name}> 플레이어를 교체합니다. \n새로운 {self.positions[(self.old_player_index-1)//2]}{position_ment} 입력하세요 (예. $김솬 다2):")
            del self.names[self.old_player_index-1]
            del self.scores[self.old_player_index-1]
        elif self.command == '밸런스' or self.command == '칼바람':
            del self.names[self.old_player_index-1]
            del self.scores[self.old_player_index-1]
            await ctx.send(f"<{old_player_name}> 플레이어를 교체합니다. \n새로운 플레이어 정보를 입력하세요 (예. $김솬 실2):")

        old_player_index_msg = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.startswith('$') and self.command != None:
            player_input = message.content.split()
            player_name = player_input[0][1:]
            tier = player_input[1]

            # 티어를 점수로 변환
            score = self.change(tier)

            # 플레이어와 점수를 저장
            self.players[player_name] = score
            self.names.append(player_name)
            self.scores.append(score)

            print(f"self.names: {self.names}, self.scores: {self.scores}")
            print(self.players)

            if self.ModifyCommand == '수정':
                self.names.insert(self.old_player_index-1, self.names[len(self.names)-1])
                self.scores.insert(self.old_player_index-1, self.scores[len(self.scores)-1])
                del self.names[len(self.names)-1]
                del self.scores[len(self.scores)-1]
                self.ModifyCommand = None

            if len(self.names) < 10:
                if self.command == '라인고정':
                    if self.positions[len(self.names)//2] == '미드':
                        position_ment= "를"
                    else:
                        position_ment= "을"
                    await message.channel.send(f"{len(self.names)%2 + 1}번째 {self.positions[len(self.names)//2]}{position_ment} 입력하세요")
                else:
                    await message.channel.send(f"{len(self.names) + 1}번째 플레이어를 입력하세요")
            elif len(self.names) > 10:
                del self.players[self.names[10]]
                del self.names[10]
                del self.scores[10]
                print(self.names, self.scores, self.players)
                await message.channel.send("입력 가능한 플레이어가 초과되었습니다.")
            else:
                if self.command == '라인고정':
                    self.teams = self.lane_balance(self.names, self.scores)
                else:
                    self.teams = self.balance_teams(self.names, self.scores)
                    
                print(f"self.teams {self.teams}")
                if isinstance(self.teams, tuple):
                    # best_team이 반환된 경우
                    await message.channel.send("**최적의 밸런스를 만들수 없는 멤버 조합입니다.** \n최소 점수차의 팀을 보여드리겠습니다.")
                    team1_info = '\n'.join([f"<{player}>" for player in self.teams[0]])
                    team2_info = '\n'.join([f"<{player}>" for player in self.teams[1]])

                    # 점수 총합 계산 및 추가
                    team1_score = sum([self.players[player] for player in self.teams[0]])
                    team2_score = sum([self.players[player] for player in self.teams[1]])

                    team1_info += f"\n**총합:** {team1_score}"
                    team2_info += f"\n**총합:** {team2_score}"

                    embed = discord.Embed(title=f"팀 조합", color=random.randint(0, 0xFFFFFF))
                    embed.add_field(name="팀 1", value=team1_info, inline=True)
                    embed.add_field(name="팀 2", value=team2_info, inline=True)

                    await message.channel.send(embed=embed)
                    
                else:
                    embed = discord.Embed(title=f"팀 조합", color=random.randint(0, 0xFFFFFF))
                    half_teams = len(self.teams)//2
                    
                    for index, team in enumerate(self.teams[:half_teams]):
                        team1_info = '\n'.join([f"<{player}>" for player in team[0]])
                        team2_info = '\n'.join([f"<{player}>" for player in team[1]])

                        # 점수 총합 계산 및 추가
                        team1_score = sum([self.players[player] for player in team[0]])
                        team2_score = sum([self.players[player] for player in team[1]])

                        team1_info += f"\n총합: {team1_score}"
                        team2_info += f"\n총합: {team2_score}"

                        embed.add_field(name=f"조합 {index + 1}", value=f"**팀 1:**\n{team1_info}", inline=True)
                        embed.add_field(name="\u200b", value=f"**팀 2:**\n{team2_info}", inline=True)  # "\u200b"는 빈 칸
                        if index+1 != half_teams:
                            embed.add_field(name="\u200b", value="\u200b", inline=False)

                    await message.channel.send(embed=embed)
        elif message.content.startswith('$') and self.command == None:
            await message.channel.send("명령어를 먼저 입력하세요 (예. !밸런스, !라인고정, !칼바람)")



    # 일반 밸런싱    
    def balance_teams(self, names, scores):

        all_possible_teams = list(combinations(range(10), 5))

        best_teams = []
        min_diff = np.inf
        best_team = None

        for team1 in all_possible_teams:
            team2 = [i for i in range(10) if i not in team1]

            team1_score = sum(scores[i] for i in team1)
            team2_score = sum(scores[i] for i in team2)

            diff = abs(team1_score - team2_score)
            total = team1_score + team2_score

            if diff < total/100:
                if len(best_teams) < 16:
                    best_teams.append(([names[i] for i in team1], [names[i] for i in team2]))
                else:
                    break;

            if diff < min_diff:
                min_diff = diff
                best_team = (list([names[i] for i in team1]), list([names[i] for i in team2]))

        if not best_teams:
            print("Error: 최적의 밸런스를 만들 수 없는 조합입니다.")
            print(best_team)
            return best_team
        print(f"total/100:  {total/100}")
        return best_teams
    
    # 라인고정 모드 밸런싱
    def lane_balance(self, names, scores):
        positions = [names[i:i+2] for i in range(0, len(names), 2)]
        position_scores = {names[i]: scores[i] for i in range(len(names))}

        best_teams = []
        best_team = []

        all_possible_teams = list(product(*[[(player1, player2), (player2, player1)] for player1, player2 in positions]))

        for team in all_possible_teams:
            team1, team2 = zip(*team)  # Unzip the team

            team1_score = sum(position_scores[player] for player in team1)
            team2_score = sum(position_scores[player] for player in team2)

            diff = abs(team1_score - team2_score)
            total = team1_score + team2_score

            if diff < total/50:
                if len(best_teams) < 16:
                    best_teams.append((team1, team2))
                else:
                    break;
        
        print(f"total/50:  {total/50}")
            
        if not best_teams :
            print("Error: 최적의 밸런스를 만들 수 없는 조합입니다.")
            team1 = []
            team2 = []
            
            sum1 = 0
            sum2 = 0
            sum3 = 0
            sum4 = 0
            
            # scores를 기준으로 names를 정렬
            for i in range(0, len(names)-1, 2):
                if scores[i] < scores[i+1]:
                    names[i], names[i+1] = names[i+1], names[i]
                    scores[i], scores[i+1] = scores[i+1], scores[i]

            
            for i in range(0, len(names), 2):
                if sum1 <= sum2:
                    team1.append(names[i])
                    sum1 += scores[i]
                    team2.append(names[i+1])
                    sum2 += scores[i+1]
                else:
                    team1.append(names[i+1])
                    sum1 += scores[i+1]
                    team2.append(names[i])
                    sum2 += scores[i]
                    
            sum3 = sum1 - scores[0] + scores[1]
            sum4 = sum2 - scores[1] + scores[0]
            
            # 두 팀의 탑을 바꿨을 때 점수차의 절대값이 더 작으면 탑 교환
            if abs(sum3 - sum4) < abs(sum1 - sum2):
                team1[0], team2[0] = team2[0], team1[0]
                sum1 = sum3
                sum2 = sum4
            
            best_team = (list(team1), list(team2))
            return best_team
            
        return best_teams

    

    @staticmethod                
    def change(tier):
        score = 0
        
        cut = tier[0]
        number = tier[-1]

        if cut == "아":
            tier = "아이언"
        elif cut == "브":
            tier = "브론즈"
        elif cut == "실":
            tier = "실버" + number
        elif cut == "골":
            tier = "골드" + number
        elif cut == "플":
            tier = "플레티넘" + number
        elif cut in ["에", "애"]:
            tier = "에메랄드" + number
        elif cut == "다":
            tier = "다이아" + number
        elif cut in ["마", "그", "챌"]:
            try:
                masterCut = tier[-3]
                if masterCut in ['마', '스', '터']:
                    number = '0'
                elif (cut == "챌" and len(tier) == 5) or (cut == "챌" and len(tier) == 7):
                    number = '9'
                else:
                    number = masterCut
            except IndexError:
                if tier[-1] == '마':
                    number = '0'
                elif cut == "그" and len(tier) == 2:
                    number = '5'
                elif cut == "챌" and len(tier) == 1:
                    number = '8'
                elif tier[-2] == '마':
                    number = '0'
            tier = "마/그/챌" + number

        # Switch case 구현
        tier_map = {
            "아이언": 5,
            "브론즈": 5,
            "실버4": 9, "실버실": 9, "실버버": 9,
            "실버3": 11,
            "실버2": 13,
            "실버1": 14,
            "골드4": 16, "골드드": 16, "골드골": 16,
            "골드3": 17,
            "골드2": 18,
            "골드1": 19,
            "플레티넘4": 21, "플레티넴플": 21, "플레티넘레": 21, "플레티넘넘": 21,
            "플레티넘3": 22,
            "플레티넘2": 23,
            "플레티넘1": 24,
            "에메랄드4": 26, "에메랄드드": 26, "에메랄드메": 26, "에메랄드에": 26,
            "에메랄드3": 27,
            "에메랄드2": 28,
            "에메랄드1": 29,
            "다이아4": 31, "다이아아": 31, "다이아다": 31,
            "다이아3": 34,
            "다이아2": 37,
            "다이아1": 43,
            "마/그/챌0": 49,
            "마/그/챌1": 53,
            "마/그/챌2": 55,
            "마/그/챌3": 58,
            "마/그/챌4": 61,
            "마/그/챌5": 63,
            "마/그/챌6": 65,
            "마/그/챌7": 67,
            "마/그/챌8": 70,
            "마/그/챌9": 74,
        }
        score = tier_map.get(tier, 5)
        
        return score