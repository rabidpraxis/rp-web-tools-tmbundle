#!/usr/bin/env python
# ====== tm_browser_refresh ==================================================
# ============================================================================
import os
import subprocess
import time

# ============================================================================
# Set this variable in your project and it will search for the title of the
# browser that contains this.
# ============================================================================
try:
  tab_title = os.environ['RP_REFRESH_TITLE_CONTAINS']
  do_title_contains = True
except KeyError:
  do_title_contains = False

delay = "0.25" # delay before refreshing

# ============================================================================
# dict containing the Applications
#   appName: The name of the OS X process (differs from the display name)
#   command: Command to be executed from within the shell to refresh the browser
# ============================================================================
apps = {
"Safari"  : {"appName" : "Safari", 
             "command_active" : """osascript -e '
                delay ${delay}
                tell application "Safari" 
                  try
                    tell current tab of window 1 to do JavaScript "location.reload(true)"
                  end try
                end tell
               ' &>/dev/null &""",
             "command_title" : """osascript -e '
               delay ${delay}
               tell application "Safari"
               	set wins_ to (tabs of windows whose name contains "${title}")
               	repeat with win_ in wins_
               		repeat with tab_ in win_
               			tell tab_ to do JavaScript "location.reload(true)"
               		end repeat
               	end repeat
               end tell           
              ' &>/dev/null &"""},
"Chrome"  : {"appName" : "Google Chrome Helper",
             "command_active" : """osascript -e '
                delay ${delay}
                tell application "Google Chrome" 
                  try
                    tell active tab of window 1 to reload
                  end try
                end tell
                ' &>/dev/null &""",
             "command_title" : """osascript -e '
               delay ${delay}
               tell application "Google Chrome"
               	set wins_ to (tabs of windows whose title contains "${title}")
               	repeat with win_ in wins_
               		repeat with tab_ in win_
               			tab_ reload
               		end repeat
               	end repeat
               end tell                
             ' &>/dev/null &"""},
"Firefox" : {"appName" : "firefox-bin",
             "command_active" : """osascript -e '
                 delay ${delay}
                 tell application "Firefox"
                 	if (count of (windows whose id is not -1)) is greater than 0 then
                   try
                      do shell script "echo 'BrowserReload()' | nc localhost 4242"
                   end try
                 end tell
                 ' &>/dev/null &""",
             # This is a nasty nasty mess.. I know. It works though.
             "command_title" : """osascript -e '
             delay ${delay}
             tell application "Firefox"
             	if (count of (windows whose id is not -1)) is greater than 0 then
                try
               		set js to "var windowEnum = Cc[\\\\\\\"@mozilla.org/appshell/window-mediator;1\\\\\\\"].getService(Ci.nsIWindowMediator).getEnumerator(\\\\\\\"\\\\\\\");while(windowEnum.hasMoreElements()) {var browsers = windowEnum.getNext().gBrowser.browsers;for (var i=0; i < browsers.length; i++) {if (browsers[i].contentTitle.indexOf(\\\\\\\"${title}\\\\\\\") != -1)browsers[i].reload();}}"
               		do shell script "echo \\\"" & js & "\\\" | nc localhost 4242"
                end try
             	end if
             end tell
             ' &>/dev/null &"""}
}

# ====== Checks for running browser ==========================================
def check_app(arg):
  return int(subprocess.Popen("osascript -e 'tell app \"System Events\" to count processes whose name is \""+arg+"\"'", 
             shell=True, stdout=subprocess.PIPE).communicate()
             [0])>0

# ====== lets go! ============================================================
for k, v in apps.iteritems():
  if check_app(v['appName']):
    if do_title_contains:
      subprocess.Popen(v['command_title'].replace("${title}", tab_title).replace("${delay}", delay), shell=True)
    else:
      subprocess.Popen(v['command_active'].replace("${delay}", delay), shell=True)