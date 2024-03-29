from discord.ext import commands

class InteractionEventListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='설명서', aliases=['도움말'])
    async def _설명서(self, ctx):
        await ctx.send(
            "■ 기능요약 ■\n"
            " **!밸런스**: 선수 입력 시작 \n"
            " **!라인고정**: 라인 고정 경기일 때 선수 입력 \n"
            " **!칼바람**: 칼바람 내전일 때 \n"
            " **!수정**: 멤버 정보 수정 \n"
            " \n"
            "1. **!밸런스**, **!라인고정** 혹은 **!칼바람** 을 입력하여 기능을 실행합니다.\n"
            "2. 참여자들이 본인을 ***@아이디 티어*** 형식으로 입력하면 한 명씩 등록됩니다.(혼자 여러 개 등록도 됩니다)\n"
            "2.1 **아이디에 공백이 있으면 붙여서** 써주세요.(김솬 o, 김 솬 x)\n"
            "2.2 티어는 대충써도 반영됩니다만, 마스터 이상부터는 뒤에 꼭 점수를 붙여주세요.\n"
            "*( 가능: 에1, 에매1, 마스터200, 마200, 그마400)*\n"
            "*( 불가능: 플 1, 그마, 챌린저, 마스터 300)*\n"
            "3. **!수정** 기능은 선수 입력 중 오타를 냈을 때, 혹은 내전 멤버가 바뀔 때 사용하세요.\n"
            "3.1 **!수정** 기능은 !밸런스, !라인고정, !칼바람 모든 모드에서 사용 가능합니다.\n"
            "4. 원하는 팀 조합을 복사하여 채팅창에 공유하여 사용하시면 진행하기 편합니다.\n"
        )