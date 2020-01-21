import json, math
from datetime import datetime
import urllib.error
import urllib.parse
import urllib.request

from tg_bot import dispatcher
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler

baseURL = "https://raw.githubusercontent.com/ColtOS-Devices/official_devices/master"
website = 'https://sourceforge.net/projects/coltos/files/'

__help__ = "- /devices - get all supported devices\n- /codename - get latest build"

__mod_name__ = "Devices"


def command_handler(bot, update):
    res = handleMessage(update.message.text);
    if res is None:
        return
    update.message.reply_markdown(res[0] if isinstance(res, tuple) else res,
                                  reply_markup=res[1] if len(res) == 2 else None,
                                  disable_web_page_preview=True)

def getDevices():
    request = urllib.request.urlopen(baseURL + '/devices.json')
    devices = json.loads(request.read())
    devices_list2 = [device['codename'] for device in devices]
    if not devices_list2 == devices_list:
        addHandlers(devices_list2)
    res = ["***Supported Devices: ***\n\n"];
    for device in devices:
        res.append(device['name'] + ' - /' + device['codename'] + "\n")
    return ''.join(res)

def getDevicesList():
    request = urllib.request.urlopen(baseURL + '/devices.json')
    devices = json.loads(request.read())
    return [device['codename'] for device in devices]

def getDeviceInfo(codename):
    request = urllib.request.urlopen(baseURL + '/devices.json')
    devices = json.loads(request.read());
    for device in devices:
        if device['codename'] == codename:
            return device
    return ''

def getLastestBuild(codename):
    try:
        request = urllib.request.urlopen(baseURL + '/builds/'+codename+'.json')
    except urllib.error.HTTPError:
        return
    builds = json.loads(request.read());
    return builds['response'][-1];

def humanSize(bytes):
    if bytes == 0:
      return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(bytes, 1024)))
    p = math.pow(1024, i)
    s = round(bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def humanDate(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y/%m/%d %H:%M')

def addHandlers(codenames):
    for codename in codenames:
        dispatcher.add_handler(CommandHandler(codename, command_handler))

def handleMessage(msg):
    # Clean and normalize the input message
    msg = msg.replace("/","")
    msg = msg.replace("@ColtEnigma_bot",'')

    if msg == 'devices':
        return getDevices()

    # grab device/build/changelog
    device = getDeviceInfo(msg)
    build = getLastestBuild(msg)

    if build is None:
        return

    link = website + device['codename'] + '&build=' + build['filename']

    # setup the message and send
    if device['maintainer_name'] is not None and build['filename'] is not None:
        # dirty place XD
        res = ("***Latest ColtOS for {} ({})***\n\n".format(device['name'],device['codename'])+
        "***Version:*** {} ({})\n".format(build['colt_version'], build['version'])+
        "***Build:*** [{}]({})\n".format(build['filename'], link)+
        "***Size:*** {}\n".format(humanSize(int(build['size'])))+
        "***Date:*** {}\n".format(humanDate(int(build['datetime'])))+
        "***Maintainer:*** [{}]({})\n\n".format(device['maintainer_name'], device['maintainer_url'])+
        "_(Also available in Config> System> Updater)_")

        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="Download", url=link)]
            ]
        )

        return res, kb

devices_list = getDevicesList()


dispatcher.add_handler(CommandHandler('devices', command_handler))
addHandlers(devices_list)