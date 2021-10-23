import discord
import os
import random
import threading

from PIL import Image
from PIL import ImageFilter
from PIL import ImageFont
from PIL import ImageDraw 

from environment import app_path, tmp




mutex = threading.Lock()

messages = (
  u"Hey {0.mention}, welcome to the {0.guild.name} guild's official discord "
   "server.\n"
   "Please take time to read the {1} so that everyone can be happy living in "
   "the harmony \U0001f3b5.\n"
   "Enjoy the guild here and special thanks \U0001f49b for joining our guild.",
  
  u"Welcome {0.mention}, this is the {0.guild.name} guild's discord server.\n"
   "Here {1}, please take time to read it and become part of our friendly "
   "circle \u2600\ufe0f.\n"
   "Special thanks \U0001f49a for joining our guild and hope you enjoy "
   "staying here",
  
  u"Hello {0.mention}, welcome to {0.guild.name} merchants guild \U0001f4b0.\n"
   "Please take time to read the {1} so that everyone can be happy living in "
   "the friendly atmosphere \u2600\ufe0f.\n"
   "Special thanks \U0001f49c for joining our guild and hope you enjoy "
   "staying here"
)

image_count = 3




def image_print_text(im, txt):
  #
  # Edits the input image by adding the input text at the center
  #
  draw = ImageDraw.Draw(im)
  ttf_file = '{0}/static/RobotoCondensed-Bold.ttf'.format(app_path)
  font = ImageFont.truetype(ttf_file, 42)
  w, h = draw.textsize(txt, font)
  r = 3
  textIm = Image.new('RGBA', im.size)
  pos = (int(0.5*im.size[0]-w/2-r), int(0.67*im.size[1]-h/2-r))
  textDraw = ImageDraw.Draw(textIm)
  textDraw.text(pos, txt, (0,0,0,255), font=font)
  textIm = textIm.filter(ImageFilter.GaussianBlur(radius=r))
  textDraw = ImageDraw.Draw(textIm)
  textDraw.text(pos, txt, (255,255,255,255), font=font)
  out = Image.new('RGBA', im.size)
  out.paste(im)
  out = Image.alpha_composite(out, textIm)
  return out




async def welcome(member):
  #
  # Get a welcome image with the member's name written on it and send it to the
  # welcome channel with a message
  #
  i = random.randrange(image_count)
  im = Image.open('{0}/static/welcome{1}.png'.format(app_path, i))
  txt = 'Welcome {0}'.format(member.display_name)
  im = image_print_text(im, txt)
  
  rules = 'rules'
  for ch in member.guild.channels:
    if ch.name.find('rules') != -1:
      rules = ch.mention
      break
  # The message to be sent
  i = random.randrange(len(messages))
  msg = messages[i].format(member, rules)
  ctx = 'x'
  for ch in member.guild.channels:
    if ch.name.find('welcome') != -1:
      ctx = ch
      break
  if ctx == 'x':
    print('No welcome channel')
    return
  
  # The sending action
  mutex.acquire()
  if not os.path.exists(tmp):
    os.makedirs(tmp)
  tmpFile = '{0}/welcome.png'.format(tmp)
  im.save(tmpFile)
  file = discord.File(tmpFile)
  try:
    await ctx.send(file=file, content=msg)
  except:
    print('Error: Failed sending a welcome message')
  os.remove(tmpFile)
  mutex.release()