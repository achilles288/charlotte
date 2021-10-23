import discord
import random

import music

from environment import token, owner
from attachment import send_attachment_link
from welcome import welcome




# https://discord.com/api/oauth2/authorize?client_id=889846989297164328&permissions=3189760&scope=bot

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
mention = 'x'
local = False




@client.event
async def on_ready():
  # 
  # The function triggered when the bot logs in to the discord
  # 
  global mention
  mention = client.user.mention[2:-1]
  music.setup(client)
  print('Logged in as {0.user}'.format(client))




async def on_command(message, cmd, args):
  #
  # Whenever a message starts with a dot character, this function is called
  #
  ctx = message.channel
  user = message.author

  if cmd == 'hug' and len(args) > 0:
    i = random.randrange(8)
    msg = '{0} hugs {1}'.format(user.display_name, args[0])
    await send_attachment_link(ctx, 'hug{0}.gif'.format(i), msg)
  
  elif cmd == 'slap' and len(args) > 0:
    i = random.randrange(6)
    msg = '{0} slaps {1}'.format(user.display_name, args[0])
    await send_attachment_link(ctx, 'slap{0}.gif'.format(i), msg)
  
  elif cmd == 'p' or cmd == 'play':
    if len(args) == 0:
      return
    name = ' '.join(args)
    await music.play(message, name)
  
  elif cmd == 'pause':
    await music.pause(message)
  
  elif cmd == 'resume':
    await music.resume(message)
  
  elif cmd == 'q' or cmd == 'queue':
    await music.queue(message)
  
  elif cmd == 'skip':
    if len(args) == 0:
      await music.skip(message)
    else:
      await music.skip(message, int(args[0]))
  
  elif cmd == 'remove':
    if len(args) > 0:
      await music.remove(message, int(args[0]))
  
  elif cmd == 'loop':
    await music.loop(message)
  
  elif cmd == 'dc' or cmd == 'disconnect':
    await music.disconnect(message)
  
  elif cmd == 'logout':
    if user.mention == owner:
      await client.close()




async def on_mention(message):
  #
  # The funciton is called from on_message if the input message contains the
  # mention string to the bot
  #
  return




@client.event
async def on_message(message):
  #
  # The event function triggered whenever a member sends a message
  #
  if message.author == client.user:
    return
  
  if len(message.content) < 256:
    if message.content.startswith('.') and len(message.content) >= 2:
      print('{0.author.display_name} commanded: {0.content}'.format(message))
      tokens = message.content.split(' ')
      await on_command(message, tokens[0][1:], tokens[1:])
    
    elif message.content.find(mention) != -1:
      print('{0.author.display_name} mentioned: {0.content}'.format(message))
      await on_mention(message)
    
    else:
      print('{0.author.display_name}: {0.content}'.format(message))




@client.event
async def on_member_join(member):
  #
  # The event function triggered whenever a new member joins to the server
  #
  print('{0.display_name} has joined the server'.format(member))
  await welcome(member)




if __name__ == "__main__":
  local = True
  client.run(token)