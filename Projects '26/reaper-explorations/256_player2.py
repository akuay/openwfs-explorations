from reaper_python import *
import os
import subprocess

NUM_CHANNELS = 256
FFMPEG = "ffmpeg"

# Source channel -> hardware output
HARDWARE_OUTPUTS = list(range(1, NUM_CHANNELS + 1))


def choose_file():
    ok, path, _, _ = RPR_GetUserFileNameForRead(
        "", "Select 256-channel audio file", ""
    )
    return path if ok else None


def choose_folder():
    ok, path = RPR_GetUserInputs("Output folder", 1, "Folder path:", "")

    if not ok or not path:
        return None

    return path.strip('"')


def split_file(src, outdir):
    os.makedirs(outdir, exist_ok=True)

    cmd = [
        FFMPEG,
        "-y",
        "-i", src,
        "-vn"
    ]

    files = []

    for ch in range(NUM_CHANNELS):
        filename = os.path.join(
            outdir,
            "CH_{:03d}.wav".format(ch + 1)
        )

        cmd += [
            "-map_channel",
            "0.0.{}".format(ch),
            "-c:a",
            "pcm_s24le",
            filename
        ]

        files.append(filename)

    result = subprocess.call(cmd)

    if result != 0:
        raise RuntimeError("FFmpeg failed while splitting the file.")

    return files


def create_track(wav, channel):
    RPR_InsertTrackAtIndex(
        RPR_CountTracks(0),
        True
    )

    track = RPR_GetTrack(
        0,
        RPR_CountTracks(0) - 1
    )

    RPR_GetSetMediaTrackInfo_String(
        track,
        "P_NAME",
        "CH {:03d}".format(channel),
        True
    )

    RPR_SetMediaTrackInfo_Value(
        track,
        "I_NCHAN",
        2
    )

    RPR_SetMediaTrackInfo_Value(
        track,
        "B_MAINSEND",
        0
    )

    item = RPR_AddMediaItemToTrack(track)

    take = RPR_AddTakeToMediaItem(item)

    source = RPR_PCM_Source_CreateFromType(
        "WAVE"
    )

    RPR_SetMediaItemTake_Source(
        take,
        RPR_PCM_Source_CreateFromFile(
            wav
        )
    )

    send = RPR_CreateTrackSend(
        track,
        None
    )

    # Mono source.
    RPR_SetTrackSendInfo_Value(
        track,
        0,
        send,
        "I_SRCCHAN",
        1024
    )

    # Mono hardware destination.
    hardware = HARDWARE_OUTPUTS[channel - 1] - 1

    RPR_SetTrackSendInfo_Value(
        track,
        0,
        send,
        "I_DSTCHAN",
        hardware | 1024
    )

    RPR_SetTrackSendInfo_Value(
        track,
        0,
        send,
        "D_VOL",
        1.0
    )


def main():
    src = choose_file()

    if not src:
        return

    outdir = choose_folder()

    if not outdir:
        return

    output_dir = os.path.join(
        outdir,
        os.path.splitext(
            os.path.basename(src)
        )[0] + "_split"
    )

    try:
        RPR_ShowConsoleMsg(
            "Splitting 256-channel file...\n"
        )

        files = split_file(
            src,
            output_dir
        )

        RPR_Undo_BeginBlock()
        RPR_PreventUIRefresh(1)

        for channel, wav in enumerate(files, 1):
            create_track(wav, channel)

        RPR_UpdateArrange()

        RPR_Undo_EndBlock(
            "Create 256-channel hardware routing",
            -1
        )

        RPR_ShowMessageBox(
            "Finished.\n\n"
            "256 mono WAV files saved to:\n"
            + output_dir,
            "256 Channel Router",
            0
        )

    except Exception as e:
        RPR_ShowMessageBox(
            str(e),
            "256 Channel Router",
            0
        )

    finally:
        RPR_PreventUIRefresh(-1)


main()
 