import pygst
import gst

def on_tag(bus, msg):
    taglist = msg.parse_tag()
    print 'on_tag:'
    for key in taglist.keys():
        print '\t%s = %s' % (key, taglist[key])

#our stream to play
music_stream_uri = 'http://mp3channels.webradio.antenne.de/chillout'

#creates a playbin (plays media form an uri) 
player = gst.element_factory_make("playbin", "player")

#set the uri
player.set_property('uri', music_stream_uri)

#start playing
player.set_state(gst.STATE_PLAYING)

#listen for tags on the message bus; tag event might be called more than once
bus = player.get_bus()
bus.enable_sync_message_emission()
bus.add_signal_watch()
bus.connect('message::tag', on_tag)
def play():
    player.set_state(gst.STATE_PLAYING)

def pause():
    player.set_state(gst.STATE_PAUSED)

def stop():
    player.set_state(gst.STATE_NULL)

def play_new_uri( new_uri ):
    player.set_state(gst.STATE_NULL)
    player.set_property('uri', new_uri )
    play()

play()
#wait and let the music play
raw_input('Press enter to stop playing...')
