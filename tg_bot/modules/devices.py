import json, math
from datetime import datetime
import urllib.error
import urllib.parse
import urllib.request

from tg_bot import dispatcher
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, RegexHandler


baseURL = "https://raw.githubusercontent.com/ColtOS-Devices/official_devices"
website = 'https://sourceforge.net/projects/coltos/files/'

__help__ = "- /devices - get all supported devices\n- #codename - get latest build"

__mod_name__ = "Devices"


def getDevices():
    request = urllib.request.urlopen(baseURL + '/devices.json')
    devices = json.loads(request.read())
    devices_list2 = [device['codename'] for device in devices]
    if not devices_list2 == devices_list:
        addHandlers(devices_list2)
    res = ["<b>Supported Devices: </b>\n\n"];
    for device in devices:
        res.append(device['name'] + ' - #' + device['codename'] + "\n")
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
        request = urllib.request.urlopen(baseURL + '/'+codename+'/build.json')
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
        dispatcher.add_handler(RegexHandler("^#" + codename + "$", device_handler))


def devices_handler(bot, update):
    update.message.reply_html(getDevices())


def device_handler(bot, update):
    text = update.message.text[1:]

    device = getDeviceInfo(text)
    build = getLastestBuild(text)

    if build is None:
        return

    link = website + device['codename'] + "/" + build['filename'] + "/download"
    
    # setup the message and send
    if device['maintainer_name'] is not None and build['filename'] is not None:
        # dirty place XD
        res = ("<b>Latest ColtOS for {} ({})</b>\n\n".format(device['name'],device['codename'])+
        "<b>Build:</b> <a href='{1}'>{0}</a>\n".format(build['filename'], link)+
        "<b>Size:</b> {}\n".format(humanSize(int(build['size'])))+
        "<b>Date:</b> {}\n".format(humanDate(int(build['datetime'])))+
        "<b>Maintainer:</b> <a href='{1}'>{0}</a>\n\n".format(device['maintainer_name'], device['maintainer_url']))

        kb = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="Download", url=link)]
            ]
        )

        update.message.reply_html(res, reply_markup=kb, disable_web_page_preview=True)


devices_list = getDevicesList()

dispatcher.add_handler(CommandHandler('devices', devices_handler))
addHandlers(devices_list)