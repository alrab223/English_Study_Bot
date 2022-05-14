import asyncio
import random

from discord.ext import commands

from cog.util.DbModule import DbModule as db


class English(commands.Cog):

   def __init__(self, bot):
      self.bot = bot
      self.db = db()

   @commands.dm_only()
   @commands.group("toeicオプション")
   async def toeic_option(self, ctx):
      if ctx.invoked_subcommand is None:
         with open("text/toeic_option.txt", "r")as f:
            text = f.read()
         await ctx.send(text)

   @toeic_option.command("-t")
   async def t(self, ctx, sec: int):
      self.db.update("daily_english", {"intervals": sec}, {"id": ctx.author.id})
      await ctx.send(f"インターバルを{sec}秒に変更しました")

   @toeic_option.command("-l")
   async def lists(self, ctx, level: int):
      words = self.db.select(f"select *from English where level={level}")
      text = "```"
      text2 = "```"
      text3 = "```"
      for i, word in enumerate(words):
         if i < 30:
            text += f'{word["words"]} : {word["japanese"]}\n'
         elif i < 60:
            text2 += f'{word["words"]} : {word["japanese"]}\n'
         else:
            text3 += f'{word["words"]} : {word["japanese"]}\n'
      text += "```"
      text2 += "```"
      text3 += "```"
      await ctx.send(text)
      await ctx.send(text2)
      await ctx.send(text3)

   def question_select(self, ctx, random_level=False):
      if random_level is True:  # レベルに関係なく問題を返す
         questions = self.db.select(
             "SELECT * FROM English LEFT outer JOIN english_score ON English.words=english_score.word")
         return questions
      else:  # レベルから問題を選出
         level = self.db.select(f"select level from daily_english where id={ctx.author.id}")[0]["level"]
         questions = self.db.select(  # 正解数が３以下の問題を選出
             f"SELECT * FROM English LEFT outer JOIN english_score ON English.words=english_score.word WHERE (user_id={ctx.author.id} OR LEVEL={level}) GROUP BY English.words HAVING COUNT(*)<=2")
         return questions

   @commands.dm_only()
   @commands.slash_command(name="パス")
   async def Pass(self, ctx):
      if self.db.select(f"select *from daily_english where id={ctx.author.id}")[0]["Pass"] >= 3:
         self.db.update("daily_english", {"Pass": 0, "daily": 1}, {"id": ctx.author.id})
         await ctx.send("パスを使って発言権を得た")
      else:
         await ctx.send("パスが足りない")

   @commands.slash_command(name="toeicチャレンジ登録")
   async def toeic_regist(self, ctx):
      if self.db.select(f"select *from daily_english where id={ctx.author.id}") == []:
         self.db.allinsert("daily_english", [ctx.author.id, 1, 1, 1, 3])
         await ctx.send(f"{ctx.author.mention}登録しました")
      else:
         await ctx.send(f"{ctx.author.mention}すでに登録されています")

   @commands.slash_command(name="toeicチャレンジ解除")
   async def toeic_remove(self, ctx):
      if self.db.select(f"select *from daily_english where id={ctx.author.id}") != []:
         self.db.delete("daily_english", {"id": ctx.author.id})
         await ctx.send(f"{ctx.author.mention}解除しました")
         self.db.delete("english_score", {"user_id": ctx.author.id})
      else:
         await ctx.send(f"{ctx.author.mention}まだ登録されていません")

   @commands.dm_only()
   @commands.slash_command(name="toeicチャレンジ開始")
   async def toeic(self, ctx):
      score = 0
      interval = self.db.select(f"select intervals from daily_english where id={ctx.author.id}")[0]["intervals"]
      await ctx.send("単語テストはっじまるよ～\n\n")
      questions = self.question_select(ctx, True)  # 問題の用意がレベルアップに間に合わない時はここの引数をTrueとする

      if len(questions) < 10:
         self.db.update(f"update daily_english set level=level+1 where id={ctx.author.id}")
         await ctx.send("レベルが上がりました。もう一度コマンド入力をお願いします")
         return

      questions = random.sample(questions, 10)
      for i, q in enumerate(questions):
         choices = []
         await ctx.send(f"第{i+1}問目")
         while True:
            dummy = self.db.select("select japanese from English order by rand() limit 5")  # 選択肢の数
            for choice in dummy:
               choices.append(choice["japanese"])
            choices.append(q["japanese"])
            if len(choices) != len(set(choices)):
               choices = []
               continue
            else:
               break
         random.shuffle(choices)
         for i in range(len(choices)):
            choices[i] = str(i + 1) + "," + choices[i]
         text = "  ".join(choices)
         await ctx.send(f"{q['words']}```\n{text}```\n")

         def user_check(message):
            return message.author.id == ctx.author.id
         try:
            msg = await self.bot.wait_for('message', timeout=15.0, check=user_check)
            if choices[int(msg.content) - 1].split(",")[1] == q["japanese"]:
               await ctx.send("正解！")
               score += 1
               self.db.allinsert("english_score", [ctx.author.id, q["words"]])
            elif msg.content == "7":
               await ctx.send("中止しました")
               return
            else:
               await ctx.send(f"残念！正解は\n`{q['japanese']}`\nです")
         except asyncio.TimeoutError:
            await ctx.send("判断が遅い！")
         await asyncio.sleep(interval)
      if score > 7:
         self.db.update("daily_english", {"daily": 1}, {"id": ctx.author.id})
         await ctx.send("ロックを解除しました")

      await ctx.send(f"{score}点\n毎日やって英語力を上げよう")
      return

   async def toeic_reset(self):
      channel = self.bot.get_channel()
      await channel.send("Toeicチャレンジャーはロックが掛かりました。問題を解いて解除しゃしゃしゃしゃしゃしゃしゃしゃしゃしゃしゃしゃ")
      self.db.custom_update("update daily_english set daily=0,Pass=Pass+1")
      user = self.db.select("select *from daily_english")
      for i in user:
         member = self.bot.get_user(i['id'])
         if i["Pass"] <= 3:
            num = i["Pass"]
         else:
            num = 3
         await channel.send(f"{member.display_name}はパスが{num}3つ残っています。`!パス`でパスを3つ使ってtoeicチャレンジをパスできます")

   @commands.Cog.listener()
   async def on_message(self, message):
      if message.author.bot:
         return

      try:
         flag = self.db.select(f"select daily from daily_english  where id={message.author.id}")
         if (flag[0]["daily"] == 0) and (message.guild.id == 557933106544508980):
            await message.delete()
      except Exception:
         pass


def setup(bot):
   bot.add_cog(English(bot))
