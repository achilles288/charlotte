import asyncio
import discord
import requests

from environment import *




async def send_attachment_link(ctx, filename, msg=None):
  #
  # Sends a link to an attachment stored on the web server (charlotte3-bdo-web)
  #
  isLink = False
  url = '{0}/{1}'.format(resource_url, filename)
  try:
    # The HTTP request to check the web resource activity or to wake up the app
    response = requests.get('{0}/ping.txt'.format(resource_url), timeout=1)
    if response.status_code == 200:
      isLink = True
  except:
    print('Server timeout')
  
  if isLink:
    # Sends the image link to the text channel
    if msg:
      await ctx.send(msg)
    await ctx.send(url)
  else:
    # Sends the local image as an attachment instead
    print('Sending a local attachment')
    path = '{0}/static/{1}'.format(app_path, filename)
    file = discord.File(path)
    try:
      if msg:
        await ctx.send(file=file, content=msg)
      else:
        await ctx.send(file=file)
    except:
      print('Error: Failed sending a local attachment')