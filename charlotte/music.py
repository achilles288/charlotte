import asyncio
import discord
import pafy
import random

from fast_youtube_search import search_youtube




client = 'x'

ffmpeg_options = {
  'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
  'options':'-vn'
}




def setup(cli):
  global client
  client = cli




class Song():
  #
  # The song requested by a user to play
  #
  def __init__(self, name, req=None):
    #
    # Constructor
    #
    self.request = req
    self.source = None
    self.title = None
    self.duration = 'n/a'
    
    try:
      results = search_youtube(name.split(' '))
      p = pafy.new(results[0]['id'])
      self.source = p.getbestaudio().url
      self.title = p.title
      if p.length > 3600:
        h = int(p.length/3600)
        m = int(p.length/60) % 60
        s = int(p.length) % 60
        self.duration = '{:01d}:{:02d}:{:02d}'.format(h, m, s)
      else:
        m = int(p.length/60)
        s = int(p.length) % 60
        self.duration = '{:02d}:{:02d}'.format(m, s)
    except Exception as e:
      print('Failed to search music: ' + str(e))




class MusicPlayer():
  #
  # Music player to be used for each discord server
  #
  def __init__(self, guild, ctx, vc):
    #
    # Constructor
    #
    self.guild = guild
    self.text_channel = ctx
    for ch in guild.channels:
      if ch.name.lower().find('music') != -1:
        self.text_channel = ch
        break
    self.voice = None
    self.voice_channel = vc
    self.music_queue = []
    self.now_playing = None
    self.is_loop = False
  
  
  async def disconnect(self):
    #
    # Disconnects from the voice channel
    #
    self.music_queue = []
    self.now_playing = None
    self.is_loop = False
    if self.voice and self.voice.is_connected():
      self.voice.stop()
      await self.voice.disconnect()
      print('Disconnected')
  
  
  async def join(self):
    #
    # Runs the timing events
    #
    self.voice = discord.utils.get(client.voice_clients, guild=self.guild)
    if not self.voice or not self.voice.is_connected():
      try:
        self.voice = await self.voice_channel.connect()
      except:
        print("Error connecting to a voice channel")
        return
    else:
      return
    
    i = 0
    while self.voice.is_connected():
      await asyncio.sleep(1)
      if not self.voice.is_playing() and not self.voice.is_paused():
        i += 1
        if i >= 120:
          await self.disconnect()
          break
        if len(self.music_queue) > 0:
          await self.play_next()
  
  
  async def play(self, song):
    #
    # Adds the music to the queue
    #
    if not song.source:
      return
    self.music_queue.append(song)
    if not self.voice or not self.voice.is_connected():
      await self.join()
  
  
  async def play_next(self):
    #
    # Plays the next music 
    #
    texts = (
      u'Now playing ***{0.title}*** \U0001f3b5',
      '***{0.title}*** is playing now',
      u'\U0001f3b7 Playing ***{0.title}*** now',
      'Playing ***{0.title}*** now'
    )
    i = random.randrange(len(texts))
    msg = texts[i]

    if len(self.music_queue) == 0:
      return
    
    song = self.music_queue[0]
    self.music_queue.pop(0)
    if self.is_loop:
      self.music_queue.append(song)
    
    audio = discord.FFmpegPCMAudio(song.source, **ffmpeg_options)
    self.now_playing = song
    await self.text_channel.send(msg.format(song))
    self.voice.play(audio)
  

  def pause(self):
    #
    # Pauses the currently playing music
    #
    if self.voice and self.voice.is_playing():
      self.voice.pause()
  
  
  def resume(self):
    #
    # Pauses the currently playing music
    #
    if self.voice and self.voice.is_paused():
      self.voice.resume()
  
  
  def queue_len(self):
    #
    # Gets the number of songs in the queue
    #
    return len(self.music_queue)
  
  
  async def show_queue(self, ctx=None):
    #
    # Shows the playlist in the specified text channel
    #
    texts = (
      u"Today's playlist \U0001f3b5",
      u"Songs listed in queue \U0001f3b7",
      u"Here is the playlist \U0001f3b8"
    )
    i = random.randrange(len(texts))
    msg = texts[i]
    if self.now_playing:
      msg += '\nNow: {0.title} [{0.duration}]'.format(self.now_playing)
    for i in range(len(self.music_queue)):
      msg += '\n{0}. {1.title} [{1.duration}]'.format(i+1, self.music_queue[i])
    if ctx:
      await ctx.send(msg)
    else:
      self.text_channel.send(msg)
  
  
  def skip(self, pos=1):
    #
    # Shows the playlist in the specified text channel
    #
    if pos < 1 or pos > len(self.music_queue):
      return

    for i in range(pos-1):
      song = self.music_queue[0]
      self.music_queue.pop(0)
      if self.is_loop:
        self.music_queue.append(song)
    self.voice.stop()
  
  
  def remove(self, pos):
    #
    # Removes a song from the playlist
    #
    if pos < 1 or pos > len(self.music_queue):
      return
    song = self.music_queue[pos-1]
    self.music_queue.pop(pos-1)
    return song




players = {}




async def play(message, music):
  #
  # The bot is commended to join to the user's voice channel and play the music
  #
  texts = (
    u'Track queued at position {0} \U0001f3b5\n***{1.title}***',
    'Track queued at position {0}\n***{1.title}***',
    u'Queued song at position {0} \U0001f3b9\n***{1.title}***',
    'Queued song at position {0}\n***{1.title}***',
  )
  i = random.randrange(len(texts))
  msg = texts[i]

  user = message.author
  ctx = message.channel
  if not user.voice or not user.voice.channel:
    await ctx.send(u'You are not connected to a voice channel \U0001f62b')
    return
  vc = user.voice.channel
  player = players.get(user.guild)
  if not player:
    player = MusicPlayer(user.guild, ctx, vc)
    players[user.guild] = player
  if player.voice_channel != user.voice.channel:
    await ctx.send(u"I'm playing music in another channel \U0001f625")
    return
  
  song = Song(music)
  if song.source:
    i = player.queue_len() + 1
    await ctx.send(msg.format(i, song))
    await player.play(song)
  else:
    await ctx.send(u'Sorry, I cannot find the song you requested \U0001f625')




async def pause(message):
  #
  # The bot is commended to pause the music
  #
  player = players.get(message.author.guild)
  if not player:
    return
  player.pause()




async def resume(message):
  #
  # The bot is commended to resume the music
  #
  player = players.get(message.author.guild)
  if not player:
    return
  player.resume()




async def queue(message):
  #
  # The bot is commended to show the queue
  #
  player = players.get(message.author.guild)
  ctx = message.channel
  if not player:
    return
  await player.show_queue(ctx)




async def skip(message, pos=1):
  #
  # The bot is commended to skip the music
  #
  player = players.get(message.author.guild)
  if not player:
    return
  player.skip(pos)




async def remove(message, pos):
  #
  # The bot is commended to remove a music from the queue
  #
  player = players.get(message.author.guild)
  ctx = message.channel
  if not player:
    return
  if pos > 0 and pos <= player.queue_len():
    song = player.remove(pos)
    await ctx.send('Removed ***{0.title}*** from the queue'.format(song))




async def loop(message):
  #
  # The bot is commended to join to the user's voice channel and play the music
  #
  texts = (
    u"Alright, I'm now playing the songs in the loop \U0001f3b8",
    u"Ok, I'm now looping the songs \U0001f3b9",
    u"The music is playing in the loop \U0001f3b5",
    u"Playing the music in the loop now \U0001f3b5"
  )
  i = random.randrange(len(texts))
  
  player = players.get(message.author.guild)
  ctx = message.channel
  if not player:
    return
  
  if not player.is_loop:
    player.is_loop = True
    await ctx.send(texts[i])
  else:
    player.is_loop = False
    await message.add_reaction(u'\U0001f44c')




async def disconnect(message):
  #
  # The bot is commended to disconnect the voice channel
  #
  player = players.get(message.author.guild)
  if not player:
    return
  await player.disconnect()
