import json, time, re
from datetime import datetime

from telebot.apihelper import ApiTelegramException

from check_init import (
    CHROME_UA, 
    CheckUpdate,
    CheckUpdateWithBuildDate,
    SfCheck, 
    PlingCheck, 
    GithubReleases
)
from tgbot import send_message as _send_message
from logger import print_and_log

# Github

class Magisk(GithubReleases):
    fullname = "Magisk Stable"
    repository_url = "topjohnwu/Magisk"
    developer = "topjohnwu"
        
class UniversalSafetyNetFix(GithubReleases):
    fullname = "Universal SafetyNet Fix"
    repository_url = "kdrag0n/safetynet-fix"
    developer = "kdrag0n"
        
class Lsposed(GithubReleases):
    fullname = "LSPosed"
    repository_url = "LSPosed/LSPosed" 
    developer = "LSPosed"
    
class Shamiko(GithubReleases):
    fullname = "Shamiko"
    repository_url = "LSPosed/LSPosed.github.io"    
    developer = "LSPosed"   
    
class PixelXpert(GithubReleases):
    fullname = "PixelXpert"
    repository_url = "siavash79/PixelXpert"    
    developer = "siavash79"
    
class OpenFonts(GithubReleases):
    fullname = "Open Fonts"
    repository_url = "Magisk-Modules-Alt-Repo/open_fonts"    
    developer = "F3FFO"
    
class AudioJitterSilencer(GithubReleases):
    fullname = "Audio Jitter Silencer"
    repository_url = "Magisk-Modules-Alt-Repo/audio-jitter-silencer"    
    developer = "yzyhk904"
    
class YAKT(GithubReleases):
    fullname = "Yet Another Kernel Tweaker"
    repository_url = "NotZeetaa/YAKT"    
    developer = "NotZeetaa"    
        
class AudioMiscSettings(GithubReleases):
    fullname = "Audio Misc. Settings"
    repository_url = "Magisk-Modules-Alt-Repo/audio-misc-settings"    
    developer = "yzyhk904" 
    
class TrichromeLibrarySquoosh(GithubReleases):
    fullname = "TrichromeLibrary Squoosh"
    repository_url = "entr0pia/trichromelibrary-squoosh"    
    developer = "entr0pia"     
        
class MiXplorerMM(GithubReleases):
    fullname = "MiXplorer Magisk Module"
    repository_url = "Magisk-Modules-Alt-Repo/MiXplorer" 
    developer = "Psk-Ita"       
        
class ACC(GithubReleases):
    fullname = "Advanced Charging Controller"
    repository_url = "VR-25/acc" 
    developer = "VR-25"          
    
class ToyBoxExt(GithubReleases):
    fullname = "ToyBox (Ext)"
    repository_url = "Magisk-Modules-Alt-Repo/ToyBox-Ext" 
    developer = "zgfg"          
       
class MagicToolFlash(GithubReleases):
    fullname = "Magic ToolFlash"
    repository_url = "Magisk-Modules-Alt-Repo/magic-flash" 
    developer = "HuskyDG"          
  
class MicroGInstallerRevived(GithubReleases):
    fullname = "MicroG Installer Revived"
    repository_url = "nift4/microg_installer_revived" 
    developer = "nift4"  
    
class XmlPak(GithubReleases):
    fullname = "xmlpak"
    repository_url = "Magisk-Modules-Repo/xmlpak" 
    developer = "RadekBledowski"          
           
class QuickSwitch(GithubReleases):
    fullname = "QuickSwitch"
    repository_url = "skittles9823/QuickSwitch" 
    developer = "skittles9823"       
    
class MIUIWidgets(GithubReleases):
    fullname = "MIUI Widgets Port"
    repository_url = "R9TRH/MIUIwidgets" 
    developer = "R9TRH"           
    
class Uperf(GithubReleases):
    fullname = "Uperf"
    repository_url = "yc9559/uperf" 
    developer = "yc9559"      
    
class ReVancedMM(GithubReleases):
    fullname = "ReVanced Magisk Module"
    repository_url = "j-hc/revanced-magisk-module" 
    developer = "j-hc"     
    
class LawniconsTeamFiles(GithubReleases):
    fullname = "Lawnicons by TeamFiles"
    repository_url = "TeamFiles/Lawnicons" 
    developer = "TeamFiles"      
      
class BCR(GithubReleases):
    fullname = "Basic Call Recorder"
    repository_url = "chenxiaolong/BCR" 
    developer = "chenxiaolong"     
    
class MiFreeform(GithubReleases):
    fullname = "Mi Freeform Window"
    repository_url = "eswd04/freeform_update" 
    developer = "eswd04"   
    
class GMSDoze(GithubReleases):
    fullname = "Universal GMS Doze"
    repository_url = "gloeyisk/universal-gms-doze" 
    developer = "gloeyisk" 
    
class YTAdAway(GithubReleases):
    fullname = "YouTube AdAway"
    repository_url = "wanam/YouTubeAdAway" 
    developer = "wanam"     
    
class ReVancedYT(GithubReleases):
    fullname = "Revanced YT"
    repository_url = "shekhawat2/ReVancedYT" 
    developer = "shekhawat2"         
    
class TachiyomiStable(GithubReleases):
    fullname = "Tachiyomi Manga Reader Stable"
    repository_url = "tachiyomiorg/tachiyomi" 
    developer = "tachiyomiorg"        
    
class TachiyomiPreview(GithubReleases):
    fullname = "Tachiyomi Manga Reader Preview"
    repository_url = "tachiyomiorg/tachiyomi-preview" 
    developer = "tachiyomiorg"            
    
class GoogleDialerFramework(GithubReleases):
    fullname = "Google Dialer Framework"
    repository_url = "Magisk-Modules-Repo/GoogleDialerFramework" 
    developer = "TheJulianJES"       
    
class DSUSideloader(GithubReleases):
    fullname = "DSU Sideloader"
    repository_url = "VegaBobo/DSU-Sideloader" 
    developer = "VegaBobo"  
    
class NewPipe(GithubReleases):
    fullname = "NewPipe"
    repository_url = "TeamNewPipe/NewPipe" 
    developer = "TeamNewPipe"   
    
class NekoMDReader(GithubReleases):
    fullname = "Neko MangaDex Reader"
    repository_url = "CarlosEsco/Neko" 
    developer = "CarlosEsco"      
    
class MKAppManager(GithubReleases):
    fullname = "App Manager"
    repository_url = "MuntashirAkon/AppManager" 
    developer = "MuntashirAkon"          
    
class RKIcons(GithubReleases):
    fullname = "RK Icons"
    repository_url = "RadekBledowski/rkicons" 
    developer = "RadekBledowski"         
    
class Bromite(GithubReleases):
    fullname = "Bromite Browser & WebView"
    repository_url = "bromite/bromite" 
    developer = "bromite"             
    
class TelegramMonet(GithubReleases):
    fullname = "Telegram Monet"
    repository_url = "c3r5b8/Telegram-Monet" 
    developer = "c3r5b8"            
    
class TermuxMonet(GithubReleases):
    fullname = "Termux Monet"
    repository_url = "HardcodedCat/termux-monet" 
    developer = "HardcodedCat"
    
class TermuxMonet(GithubReleases):
    fullname = "Termux Monet"
    repository_url = "HardcodedCat/termux-monet" 
    developer = "HardcodedCat"    
    
class RootlessJamesDSP(GithubReleases):
    fullname = "Rootless JamesDSP"
    repository_url = "ThePBone/RootlessJamesDSP" 
    developer = "ThePBone"        
    
class ReVancedManager(GithubReleases):
    fullname = "ReVanced Manager"
    repository_url = "revanced/revanced-manager" 
    developer = "revanced"            
    
class NeoLauncher(GithubReleases):
    fullname = "Neo Launcher"
    repository_url = "NeoApplications/Neo-Launcher" 
    developer = "NeoApplications"      
    
class NeoStore(GithubReleases):
    fullname = "Neo Store"
    repository_url = "NeoApplications/Neo-Store" 
    developer = "NeoApplications" 
    description = "A material F-Droid client for everyone."
                 
class SealDownloader(GithubReleases):
    fullname = "Seal Video/Audio Downloader"
    repository_url = "JunkFood02/Seal" 
    developer = "JunkFood02"    
    description = "Video/Audio downloader for Android, designed and themed with Material You."
    
class xManagerSpotify(GithubReleases):
    fullname = "xManager Spotify"
    repository_url = "xManager-v2/xManager-Spotify" 
    developer = "xManager-v2"    
    description = "An android application where you can manage and install all versions of the spotify app."
    
class Xtra(GithubReleases):
    fullname = "Xtra"
    repository_url = "crackededed/Xtra" 
    developer = "crackededed"    
    description = "Xtra is a Twitch player and browser for Android."    
    
class InfinityForReddit(GithubReleases):
    fullname = "Infinity For Reddit"
    repository_url = "Docile-Alligator/Infinity-For-Reddit" 
    developer = "Docile-Alligator"    
    description = "A Reddit client on Android written in Java. It does not have any ads and it features a clean UI and smooth browsing experience."  
    
class SagerNet(GithubReleases):
    fullname = "SagerNet"
    repository_url = "SagerNet/SagerNet" 
    developer = "SagerNet"    
    description = "A universal proxy toolchain for Android, written in Kotlin."  
    
class Cloudstream(GithubReleases):
    fullname = "Cloudstream"
    repository_url = "recloudstream/cloudstream" 
    developer = "recloudstream"    
    description = "Android app for streaming and downloading Movies, TV-Series and Anime."      
        
class YTDLnis(GithubReleases):
    fullname = "YTDLnis"
    repository_url = "deniscerri/ytdlnis" 
    developer = "deniscerri"    
    description = "Android app for downloading audio and videos using yt-dlp."        
    
class ReadYou(GithubReleases):
    fullname = "Read You"
    repository_url = "Ashinch/ReadYou" 
    developer = "Ashinch"    
    description = "A RSS reader which combines the interaction logic of Reeder with the design style of Material Design 3 (You)."            
    
class Saikou(GithubReleases):
    fullname = "Saikou"
    repository_url = "saikou-app/saikou" 
    developer = "saikou-app"    
    description = "Saikou is crafted based on simplistic yet state-of-the-art elegance. It is an Anilist only client, which also lets you stream-download Anime & Manga. "
    
class GoogleDialerMod(GithubReleases):
    fullname = "Google Dialer Mod"
    repository_url = "jacopotediosi/GoogleDialerMod" 
    developer = "jacopotediosi"    
    description = "The ultimate All-In-One Utility to tweak Google Dialer."
    
class AmazeFileManager(GithubReleases):
    fullname = "Amaze File Manager"
    repository_url = "TeamAmaze/AmazeFileManager" 
    developer = "TeamAmaze"    
    description = "Simple and attractive Material Design file manager for Android"
    
class UngoogledChromiumAndroid(GithubReleases):
    fullname = "Ungoogled Chromium Android"
    repository_url = "ungoogled-software/ungoogled-chromium-android" 
    developer = "ungoogled-software"    
    description = "A lightweight approach to removing Google web service dependency"
    
class Lemuroid(GithubReleases):
    fullname = "Lemuroid"
    repository_url = "Swordfish90/Lemuroid" 
    developer = "Swordfish90"    
    description = "Lemuroid is an open-source emulation project for Android based on Libretro."
    
class LoopHabitTracker(GithubReleases):
    fullname = "Loop Habit Tracker"
    repository_url = "iSoron/uhabits" 
    developer = "iSoron"    
    description = "Loop Habit Tracker, a mobile app for creating and maintaining long-term positive habits."
    
class ActivityManager(GithubReleases):
    fullname = "Activity Manager"
    repository_url = "sdex/ActivityManager" 
    developer = "sdex"    
    description = "Discover activities of installed applications, run them, and create shortcuts."

class BuiltInBusyBox(GithubReleases):
    fullname = "BuiltIn BusyBox"
    repository_url = "zgfg/BuiltIn-BusyBox" 
    developer = "zgfg"    
    description = "Systemless Magisk module to install BusyBox binary with its applets (UNIX/Linux command-line utilities)."

class SystemlessHostsKernelSUModule(GithubReleases):
    fullname = "Systemless Hosts Module (KernelSU)"
    repository_url = "symbuzzer/systemless-hosts-KernelSU-module"
    developer = "symbuzzer"    
    description = "Required module to use applications such as AdAway on KernelSU."

class UniversalSafetyNetAndPlayIntegrityFixMod(GithubReleases):
    fullname = "Universal SafetyNet & Play Integrity Fix (Mod)"
    repository_url = "Displax/safetynet-fix" 
    developer = "Displax"    
    description = "Magisk module to work around Google's SafetyNet and Play Integrity attestation."

class PlayIntegrityFix(GithubReleases):
    fullname = "Play Integrity Fix"
    repository_url = "chiteroman/PlayIntegrityFix" 
    developer = "chiteroman"    
    description = "This module attempts to fix Play Integrity verdicts to get a certified device on bootloader unlocked devices."

class DisableRotationSuggest(GithubReleases):
    fullname = "Disable Rotation Suggest"
    repository_url = "SAPTeamDEV/disable-rotate-suggest" 
    developer = "SAPTeamDEV"    
    description = "Permanently disables the rotate screen suggestion feature in Android P+ AOSP-Like roms works in LOS, Pixel Experience and other AOSP roms."

class ZygiskNext(GithubReleases):
    fullname = "Zygisk Next"
    repository_url = "Dr-TSNG/ZygiskNext" 
    developer = "Dr-TSNG"    
    description = "Standalone implementation of Zygisk, providing Zygisk API support for KernelSU and a replacement of Magisk's built-in Zygisk."

class MagiskOverlayfs(GithubReleases):
    fullname = "Magisk Overlayfs"
    repository_url = "HuskyDG/magic_overlayfs" 
    developer = "HuskyDG"    
    description = "Make system partition become read-write (it is also possible without Magisk)."

class SpotX(GithubReleases):
    fullname = "SpotX"
    repository_url = "SpotX-Official/SpotX" 
    developer = "SpotX-Official"    
    description = "SpotX patcher used for patching the desktop version of Spotify."

class BootloaderSpoofer(GithubReleases):
    fullname = "BootloaderSpoofer"
    repository_url = "chiteroman/BootloaderSpoofer" 
    developer = "chiteroman"    
    description = "Spoof locked bootloader on local attestations."

class Cromite(GithubReleases):
    fullname = "Cromite"
    repository_url = "uazo/cromite" 
    developer = "uazo"    
    description = "Cromite a Bromite fork with ad blocking and privacy enhancements; take back your browser!"

class AdAway(GithubReleases):
    fullname = "AdAway"
    repository_url = "AdAway/AdAway" 
    developer = "AdAway"    
    description = "AdAway is a free and open source ad blocker for Android."

class Aria2App(GithubReleases):
    fullname = "Aria2App"
    repository_url = "devgianlu/Aria2App" 
    developer = "devgianlu"    
    description = "Aria2App is an advanced download manager based on aria2 that can handle remote servers too."

class DuckDuckGo(GithubReleases):
    fullname = "DuckDuckGo"
    repository_url = "duckduckgo/Android" 
    developer = "duckduckgo"    
    description = "DuckDuckGo Android App."

class MihonApp(GithubReleases):
    fullname = "Mihon App"
    repository_url = "mihonapp/mihon" 
    developer = "mihonapp"    
    description = "Discover and read manga, webtoons, comics, and more – easier than ever on your Android device."

class Yōkai(GithubReleases):
    fullname = "Yōkai"
    repository_url = "null2264/yokai" 
    developer = "null2264"    
    description = "A free and open source manga reader"

class TachiyomiS97(GithubReleases):
    fullname = "TachiyomiS97"
    repository_url = "Saud-97/TachiyomiS97" 
    developer = "Saud-97"    
    description = "Free and open source manga reader for Android. A faster version of Tachiyomi."

class TachiyomiAZ(GithubReleases):
    fullname = "TachiyomiAZ"
    repository_url = "az4521/tachiyomiAZ" 
    developer = "az4521"    
    description = "Free and open source manga reader for Android."

class TachiyomiJ2K(GithubReleases):
    fullname = "TachiyomiJ2K"
    repository_url = "Jays2Kings/tachiyomiJ2K" 
    developer = "Jays2Kings"    
    description = "TachiyomiJ2K is a free and open source manga reader for Android 6.0 and above. Based on the original Tachiyomi."

class TachiyomiSY(GithubReleases):
    fullname = "TachiyomiSY"
    repository_url = "jobobby04/TachiyomiSY" 
    developer = "jobobby04"    
    description = "This version of Tachiyomi, TachiyomiSY was based off TachiyomiAZ."

class ReVancedExtendedMagiskModule(GithubReleases):
    fullname = "ReVanced Extended Magisk Module"
    repository_url = "MatadorProBr/revanced-extended-magisk-module" 
    developer = "MatadorProBr"    
    description = "Extensive ReVanced Extended builder. Builds both modules and APKs. Updated hourly."

class ReVancedMagiskModule(GithubReleases):
    fullname = "ReVanced Magisk Module"
    repository_url = "j-hc/revanced-magisk-module" 
    developer = "j-hc"    
    description = "Extensive ReVanced builder. Builds both modules and APKs. Updated daily."

class ReVancedAPKs(GithubReleases):
    fullname = "ReVanced APKs"
    repository_url = "revanced-apks/build-apps" 
    developer = "revanced-apks"    
    description = "The ReVanced APKs."

# Pling
    
class Pixelify(PlingCheck):
    fullname = "Pixelify"
    p_id = 1825201  
    developer = "shivan999"  
   
class Dex2oatOptimizer(PlingCheck):
    fullname = "dex2oat optimizer"
    p_id = 1819191  
    developer = "iamlooper" 
         
class MemeUIEnhancer(PlingCheck):
    fullname = "MemeUI Enhancer"
    p_id = 1723021  
    developer = "iamlooper"      
    
class AtAGlanceEnhancer(PlingCheck):
    fullname = "At A Glance Enhancer"
    p_id = 1833656  
    developer = "iamlooper"              
    
class XCharge(PlingCheck):
    fullname = "XCharge"
    p_id = 1832596  
    developer = "iamlooper"            
    
class XEngine(PlingCheck):
    fullname = "XEngine"
    p_id = 1704617  
    developer = "iamlooper"            
    
class XLoad(PlingCheck):
    fullname = "XLoad"
    p_id = 1726993  
    developer = "iamlooper"    
    
class DolbyAtmosMM(PlingCheck):
    fullname = "Dolby Atmos Magic Revision"
    p_id = 1610004  
    developer = "reiryuki"          
    
class MPL(PlingCheck):
    fullname = "Mod Pixel Launcher"
    p_id = 1720688  
    developer = "saitama96"         
    
class MemeUIMods(PlingCheck):
    fullname = "MemeUI Mods"
    p_id = 1859136  
    developer = "bedircan"       
    
class StratospherePerf(PlingCheck):
    fullname = "Stratosphere Performance"
    p_id = 1778931  
    developer = "crankv2"      
    
class AudioWizardDTSXUltraZen6MM(PlingCheck):
    fullname = "Audio Wizard DTSX Ultra Zen 6 Magisk Module"
    p_id = 1531567  
    developer = "reiryuki"     
    
class Nitron(PlingCheck):
    fullname = "Nitron Kernel Tweaker"
    p_id = 1627867  
    developer = "kartik728"         
    
class Magnetar(PlingCheck):
    fullname = "Magnetar Performance Optimizer"
    p_id = 1465345  
    developer = "kyliekyler"     
    
class PLOMA13(PlingCheck):
    fullname = "Pixel Launcher Original & Modified A13"
    p_id = 1915907  
    developer = "saitama96"      
    
class AndroidEnhancer(PlingCheck):
    fullname = "Android Enhancer"
    p_id = 1875251  
    developer = "iamlooper"     
               
class CoolModules(PlingCheck):
    fullname = "Cool Modules"
    p_id = 1582371  
    developer = "jai08" 

class PixelLauncherExtended(PlingCheck):
    fullname = "Pixel Launcher Extended"
    p_id = 1952604  
    developer = "saitama96"   

class PixelPropsUp(PlingCheck):
    fullname = "PixelPropsUp"
    p_id = 1920041  
    developer = "pixlos"
    
# Sourceforge    
    
class MagiskGApps(SfCheck):
    fullname = "Magisk GApps"
    project_name = "magiskgapps" 
    developer = "wacko1805"
               
CHECK_LIST = (
    # Github
    Magisk,
    UniversalSafetyNetFix,
    Lsposed,
    Shamiko,
    PixelXpert,
    OpenFonts,
    AudioJitterSilencer,
    YAKT,
    AudioMiscSettings,
    TrichromeLibrarySquoosh,
    MiXplorerMM,
    ACC,
    ToyBoxExt,
    MagicToolFlash,
    MicroGInstallerRevived,
    XmlPak,
    QuickSwitch,
    MIUIWidgets,
    Uperf,
    ReVancedMM,
    LawniconsTeamFiles,
    BCR,
    MiFreeform,
    GMSDoze,
    YTAdAway,
    ReVancedYT,
    TachiyomiStable,
    TachiyomiPreview,
    GoogleDialerFramework,
    DSUSideloader,
    NewPipe,
    NekoMDReader,
    MKAppManager,
    RKIcons,
    Bromite,
    TelegramMonet,
    TermuxMonet,
    RootlessJamesDSP,
    ReVancedManager,
    NeoLauncher,
    NeoStore,
    SealDownloader,
    xManagerSpotify,
    Xtra,
    InfinityForReddit,
    SagerNet,
    Cloudstream,
    YTDLnis,
    ReadYou,
    Saikou,
    GoogleDialerMod,
    AmazeFileManager,
    UngoogledChromiumAndroid,
    Lemuroid,
    LoopHabitTracker,
    ActivityManager,
    BuiltInBusyBox,
    SystemlessHostsKernelSUModule,
    UniversalSafetyNetAndPlayIntegrityFixMod,
    PlayIntegrityFix,
    DisableRotationSuggest,
    ZygiskNext,
    MagiskOverlayfs,
    SpotX,
    BootloaderSpoofer,
    Cromite,
    AdAway,
    Aria2App,
    DuckDuckGo,
    MihonApp,
    Yōkai,
    TachiyomiS97,
    TachiyomiAZ,
    TachiyomiJ2K,
    TachiyomiSY,
    ReVancedExtendedMagiskModule,
    ReVancedMagiskModule,
    ReVancedAPKs,
    # Pling
    Pixelify,
    Dex2oatOptimizer,
    MemeUIEnhancer,
    AtAGlanceEnhancer,
    XCharge,
    XEngine,
    XLoad,
    DolbyAtmosMM,
    MPL,
    MemeUIMods,
    StratospherePerf,
    AudioWizardDTSXUltraZen6MM,    
    Nitron,
    Magnetar,
    PLOMA13,
    AndroidEnhancer,
    CoolModules, 
    PixelLauncherExtended,
    PixelPropsUp,
    # Sourceforge
    MagiskGApps,
)
